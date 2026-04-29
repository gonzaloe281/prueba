# scanner.py - Versión Final HASH-DB: Rendimiento, Enlaces VT y Veredictos S/P
import os
import json
import time
import vt
import hashlib
from datetime import datetime, timedelta
from config import API_KEY, INSTANCES_PATH

def calcular_hash(ruta_archivo):
    """Genera huella SHA-256 leyendo en bloques para optimizar RAM."""
    sha256_hash = hashlib.sha256()
    try:
        with open(ruta_archivo, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                sha256_hash.update(bloque)
        return sha256_hash.hexdigest()
    except:
        return None

def limpiar_y_reciclar_db(db_actual):
    """
    Mantenimiento Inteligente:
    - 90 días: Borra 'detalles' técnicos pesados.
    - SIEMPRE conserva: Hash, Archivo, Fecha, Veredicto (S/P) y Link VT.
    """
    hoy = datetime.now()
    periodo_reciclaje = timedelta(days=90)
    db_procesada = []
    hubo_cambios = False
    
    # Identificamos qué archivos ya tienen Hash para limpiar duplicados viejos (Migración)
    rutas_con_hash = {item.get("ultima_ruta_conocida") for item in db_actual if "hash" in item}

    for item in db_actual:
        # 1. MIGRACIÓN: Elimina basura si ya existe el mismo archivo con Hash
        if "hash" not in item:
            ruta = item.get("ultima_ruta_conocida") or item.get("ruta_completa")
            if ruta in rutas_con_hash:
                hubo_cambios = True; continue
        
        # 2. RECICLAJE TRIMESTRAL: Poda lo pesado, deja lo vital
        try:
            fecha_str = item.get("fecha_escaneo") or item.get("fecha", "2000-01-01 00:00:00")
            fecha_item = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
            
            if hoy - fecha_item > periodo_reciclaje:
                if "detalles" in item: # Solo si aún tiene los datos pesados
                    item = {
                        "hash": item.get("hash"),
                        "archivo_original": item.get("archivo_original", "Desconocido"),
                        "veredicto": item.get("veredicto", "S"),
                        "link_vt": item.get("link_vt", f"https://www.virustotal.com/gui/file/{item.get('hash')}/detection"),
                        "fecha_escaneo": fecha_str
                    }
                    hubo_cambios = True
        except: pass
            
        db_procesada.append(item)
    return db_procesada, hubo_cambios

def encontrar_instancias_y_mods(ruta_base):
    instancias = {}
    try:
        for item in os.listdir(ruta_base):
            ruta_instancia = os.path.join(ruta_base, item)
            if os.path.isdir(ruta_instancia):
                ruta_mods = os.path.join(ruta_instancia, "mods")
                if os.path.exists(ruta_mods) and os.path.isdir(ruta_mods):
                    mods = [os.path.join(ruta_mods, f) for f in os.listdir(ruta_mods) if f.endswith(".jar")]
                    if mods: instancias[item] = sorted(mods)
    except: pass
    return instancias

def analizar_archivo(cliente_vt, ruta_archivo, hash_archivo):
    nombre = os.path.basename(ruta_archivo)
    print(f"\n  🔍 Analizando: {nombre}")
    try:
        with open(ruta_archivo, "rb") as f:
            analisis = cliente_vt.scan_file(f)
        
        t = 0
        while True:
            res = cliente_vt.get_object(f"/analyses/{analisis.id}")
            if res.status == "completed":
                stats = res.stats
                # Veredicto: P (Peligro), S (Seguro)
                veredicto = "P" if stats.get("malicious", 0) > 0 or stats.get("suspicious", 0) > 0 else "S"
                return {
                    "hash": hash_archivo,
                    "archivo_original": nombre,
                    "ultima_ruta_conocida": ruta_archivo,
                    "veredicto": veredicto,
                    "link_vt": f"https://www.virustotal.com/gui/file/{hash_archivo}/detection",
                    "detalles": dict(stats),
                    "estado": "OK",
                    "fecha_escaneo": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            if t > 300: return {"archivo": nombre, "error": "Timeout"}
            time.sleep(15); t += 15
    except Exception as e: return {"archivo": nombre, "error": str(e)}

def cargar_base_datos():
    if not os.path.exists("resultados.json"): return []
    try:
        with open("resultados.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        data_limpia, cambios = limpiar_y_reciclar_db(data)
        if cambios:
            print("[SISTEMA] Aplicando reciclaje y limpieza trimestral...")
            guardar_base_datos(data_limpia)
        return data_limpia
    except: return []

def guardar_base_datos(datos):
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def procesar_escaneo(cliente, lista_mods, nombre_instancia, db_actual):
    borrados = 0
    hashes_conocidos = {item["hash"] for item in db_actual if "hash" in item}

    for i, ruta_mod in enumerate(lista_mods):
        h = calcular_hash(ruta_mod)
        if not h or h in hashes_conocidos:
            if h: print(f"  [SKIP] {os.path.basename(ruta_mod)} ya analizado.")
            continue

        print(f"\n[Archivo {i+1}/{len(lista_mods)}]")
        res = analizar_archivo(cliente, ruta_mod, h)
        res["ultima_instancia"] = nombre_instancia
        
        if res.get("estado") == "OK":
            status_txt = "⚠️ PELIGROSO" if res['veredicto'] == "P" else "✅ SEGURO"
            print(f"    Veredicto: {status_txt} | Link: {res['link_vt']}")

            if res['veredicto'] == "P":
                if input(f"    ¿Eliminar amenaza? (s/n): ").lower() == 's':
                    try: 
                        os.remove(ruta_mod); print("    ✅ Borrado."); borrados += 1
                    except: print("    ❌ Error al borrar.")
            
            db_actual.append(res)
            hashes_conocidos.add(h)
            guardar_base_datos(db_actual)

        if i < len(lista_mods) - 1:
            print("    Esperando 25s (API Limit)...")
            time.sleep(25)
    print(f"\n--- Sesión finalizada. Borrados: {borrados} ---")

def main():
    while True:
        if not os.path.exists(INSTANCES_PATH): break
        db_total = cargar_base_datos()
        mapa = encontrar_instancias_y_mods(INSTANCES_PATH)

        print("\n=== MENÚ PRINCIPAL (ModScanner HASH-DB) ===")
        nombres = list(mapa.keys())
        for i, nombre in enumerate(nombres, 1):
            print(f"{i}. {nombre} ({len(mapa[nombre])} mods)")
        print("0. SALIR")

        op_inst = input("\nElija instancia: ")
        if op_inst == "0": break
        try:
            nombre_sel = nombres[int(op_inst) - 1]
            mods_instancia = mapa[nombre_sel]
        except: continue

        while True:
            print(f"\n=== MODS EN {nombre_sel} ===")
            print("1. [ANALIZAR CONTENIDO NUEVO]")
            for i, ruta in enumerate(mods_instancia, 2):
                print(f"{i}. {os.path.basename(ruta)}")
            print("0. VOLVER")

            op_mod = input("\nSeleccione: ")
            if op_mod == "0": break
            with vt.Client(API_KEY) as cliente:
                if op_mod == "1": procesar_escaneo(cliente, mods_instancia, nombre_sel, db_total)
                else:
                    try:
                        idx = int(op_mod) - 2
                        procesar_escaneo(cliente, [mods_instancia[idx]], nombre_sel, db_total)
                    except: continue
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()