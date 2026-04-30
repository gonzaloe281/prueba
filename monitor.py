# monitor.py - Monitor en tiempo real de mods de Minecraft
# Vigila la carpeta de instancias y analiza automáticamente cualquier .jar nuevo
import os
import sys
import time
import json
import hashlib
import threading
import queue
from datetime import datetime

# Verificar dependencias antes de importar
try:
    import vt
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError as e:
    print(f"❌ Dependencia faltante: {e}")
    print("   Ejecutá: pip install vt-py watchdog plyer")
    sys.exit(1)

try:
    from plyer import notification
    NOTIFICACIONES = True
except ImportError:
    NOTIFICACIONES = False
    print("⚠️  plyer no disponible — las notificaciones de Windows estarán desactivadas.")

try:
    from config import API_KEY, INSTANCES_PATH
except ImportError:
    print("❌ No se encontró config.py. Ejecutá primero: python setup.py")
    sys.exit(1)

# ──────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────
DB_PATH       = "resultados.json"
LOG_PATH      = "monitor.log"
ESPERA_API    = 25   # segundos entre análisis (límite API gratuita)
ESPERA_INICIO = 5    # segundos para esperar que el archivo termine de escribirse

# ──────────────────────────────────────────
# UTILIDADES
# ──────────────────────────────────────────
def log(mensaje):
    """Escribe en consola y en monitor.log con timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}"
    print(linea)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linea + "\n")

def notificar(titulo, mensaje, peligroso=False):
    """Muestra una notificación de Windows."""
    if not NOTIFICACIONES:
        return
    try:
        notification.notify(
            title=titulo,
            message=mensaje,
            app_name="ModScanner VT",
            timeout=8
        )
    except Exception:
        pass

def calcular_hash(ruta):
    """Genera huella SHA-256 del archivo."""
    sha256 = hashlib.sha256()
    try:
        with open(ruta, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                sha256.update(bloque)
        return sha256.hexdigest()
    except Exception:
        return None

def cargar_db():
    """Carga la base de datos de resultados."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def guardar_db(datos):
    """Guarda la base de datos de resultados."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def hash_ya_conocido(h, db):
    """Verifica si el hash ya está en la base de datos."""
    return any(item.get("hash") == h for item in db if "hash" in item)

# ──────────────────────────────────────────
# ANÁLISIS
# ──────────────────────────────────────────
def analizar_archivo(ruta):
    """Analiza un archivo .jar con VirusTotal y guarda el resultado."""
    nombre = os.path.basename(ruta)
    log(f"🔍 Analizando: {nombre}")

    # Esperar a que el archivo termine de escribirse
    time.sleep(ESPERA_INICIO)

    if not os.path.exists(ruta):
        log(f"⚠️  El archivo ya no existe (puede haber sido movido): {nombre}")
        return

    h = calcular_hash(ruta)
    if not h:
        log(f"❌ No se pudo calcular el hash de: {nombre}")
        return

    db = cargar_db()

    if hash_ya_conocido(h, db):
        log(f"[SKIP] {nombre} ya fue analizado anteriormente.")
        return

    try:
        with vt.Client(API_KEY) as cliente:
            with open(ruta, "rb") as f:
                analisis = cliente.scan_file(f)

            t = 0
            while True:
                res = cliente.get_object(f"/analyses/{analisis.id}")
                if res.status == "completed":
                    stats = res.stats
                    veredicto = "P" if stats.get("malicious", 0) > 0 or stats.get("suspicious", 0) > 0 else "S"
                    
                    resultado = {
                        "hash": h,
                        "archivo_original": nombre,
                        "ultima_ruta_conocida": ruta,
                        "veredicto": veredicto,
                        "link_vt": f"https://www.virustotal.com/gui/file/{h}/detection",
                        "detalles": dict(stats),
                        "estado": "OK",
                        "fecha_escaneo": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "origen": "monitor"
                    }

                    db.append(resultado)
                    guardar_db(db)

                    if veredicto == "P":
                        maliciosos = stats.get("malicious", 0)
                        sospechosos = stats.get("suspicious", 0)
                        log(f"⚠️  PELIGROSO: {nombre} — {maliciosos} malicioso(s), {sospechosos} sospechoso(s)")
                        log(f"   🔗 {resultado['link_vt']}")
                        notificar(
                            "⚠️ MOD PELIGROSO DETECTADO",
                            f"{nombre}\n{maliciosos} motores lo marcaron como malicioso.\nRevisá el reporte en VirusTotal.",
                            peligroso=True
                        )
                    else:
                        log(f"✅ SEGURO: {nombre}")
                        notificar(
                            "✅ Mod analizado — Seguro",
                            f"{nombre} no fue detectado como amenaza."
                        )
                    break

                if t > 300:
                    log(f"⏱️  Timeout al analizar: {nombre}")
                    break

                log(f"   Esperando resultado de VT... ({t}s)")
                time.sleep(15)
                t += 15

    except Exception as e:
        log(f"❌ Error al analizar {nombre}: {e}")

# ──────────────────────────────────────────
# COLA DE ANÁLISIS
# ──────────────────────────────────────────
cola_analisis = queue.Queue()

def worker_analisis():
    """Hilo que procesa la cola de archivos uno por uno respetando el límite de la API."""
    while True:
        ruta = cola_analisis.get()
        if ruta is None:
            break
        analizar_archivo(ruta)
        if not cola_analisis.empty():
            log(f"   ⏳ Esperando {ESPERA_API}s antes del próximo análisis (límite API)...")
            time.sleep(ESPERA_API)
        cola_analisis.task_done()

# ──────────────────────────────────────────
# DETECTOR DE ARCHIVOS NUEVOS
# ──────────────────────────────────────────
class DetectorMods(FileSystemEventHandler):
    """Detecta archivos .jar nuevos dentro de carpetas /mods."""

    def on_created(self, event):
        if event.is_directory:
            return
        ruta = event.src_path
        if not ruta.endswith(".jar"):
            return
        # Solo archivos dentro de una carpeta llamada "mods"
        carpeta = os.path.basename(os.path.dirname(ruta))
        if carpeta.lower() != "mods":
            return

        nombre = os.path.basename(ruta)
        log(f"📥 Nuevo mod detectado: {nombre} — agregando a la cola de análisis")
        notificar("📥 Nuevo mod detectado", f"{nombre}\nAnalizando con VirusTotal...")
        cola_analisis.put(ruta)

# ──────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────
def main():
    print("=" * 52)
    print("  🛡️  ModScanner VT — Monitor en tiempo real")
    print("=" * 52)

    if not os.path.exists(INSTANCES_PATH):
        log(f"❌ La ruta de instancias no existe: {INSTANCES_PATH}")
        log("   Verificá tu config.py o ejecutá python setup.py")
        sys.exit(1)

    log(f"👁️  Vigilando: {INSTANCES_PATH}")
    log("   Presioná Ctrl+C para detener el monitor.\n")

    # Iniciar hilo de análisis en segundo plano
    hilo = threading.Thread(target=worker_analisis, daemon=True)
    hilo.start()

    # Iniciar watchdog
    detector = DetectorMods()
    observer = Observer()
    observer.schedule(detector, INSTANCES_PATH, recursive=True)
    observer.start()

    notificar("🛡️ ModScanner VT activo", f"Vigilando mods en:\n{INSTANCES_PATH}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\n🛑 Monitor detenido por el usuario.")
        observer.stop()
        cola_analisis.put(None)

    observer.join()

if __name__ == "__main__":
    main()