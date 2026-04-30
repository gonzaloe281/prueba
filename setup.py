# setup.py - Instalador y Configurador Automático para ModScanner VT
import os
import subprocess
import sys

# Diccionario de rutas predefinidas
LAUNCHERS = {
    "1": ("Modrinth",    r"C:\Users\TU_USUARIO\AppData\Roaming\ModrinthApp\profiles"),
    "2": ("CurseForge",  r"C:\Users\TU_USUARIO\curseforge\minecraft\Instances"),
    "3": ("Prism Launcher", r"C:\Users\TU_USUARIO\AppData\Roaming\PrismLauncher\instances"),
    "4": ("ATLauncher",  r"C:\Users\TU_USUARIO\ATLauncher\instances"),
    "5": ("GDLauncher",  r"C:\Users\TU_USUARIO\AppData\Roaming\gdlauncher_next\data\instances"),
    "6": ("Otro",        None),
}

def instalar_dependencias():
    """Paso 1: Instala las librerías necesarias automáticamente."""
    print("\n📦 PASO 1: Verificando e instalando dependencias...")
    dependencias = ["vt-py", "watchdog", "plyer"]
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + dependencias)
        print("   ✅ Dependencias listas.")
    except Exception as e:
        print(f"   ❌ Error instalando dependencias: {e}")

def pedir_datos():
    """Paso 2: Recopila API Key y Ruta."""
    print("\n🔑 PASO 2: Configuración de VirusTotal")
    api_key = input("   Ingresá tu API Key: ").strip()
    
    print("\n📁 PASO 3: Selección de Launcher")
    for k, v in LAUNCHERS.items():
        print(f"   {k}. {v[0]}")
    
    op = input("\n   Elegí tu launcher: ").strip()
    nombre, ruta_base = LAUNCHERS.get(op, ("Otro", None))
    
    if op == "6" or not ruta_base:
        ruta = input("   Pegá la ruta completa de la carpeta de instancias: ").strip().replace('"', '')
    else:
        usuario = os.getlogin()
        ruta = ruta_base.replace("TU_USUARIO", usuario)
        print(f"   Ruta detectada: {ruta}")
    
    return api_key, ruta

def generar_config(api_key, ruta):
    """Genera el archivo config.py."""
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(f'# Generado por setup.py\nAPI_KEY = "{api_key}"\nINSTANCES_PATH = r"{ruta}"\n')
    print("\n   ✅ Archivo config.py generado exitosamente.")

def ejecutar_scanner():
    """Paso 4: Ejecución inmediata si el usuario quiere."""
    print("\n" + "=" * 50)
    print("¿Qué querés hacer ahora?")
    print("  1. Escanear mods manualmente (scanner.py)")
    print("  2. Activar monitor en tiempo real (monitor.py)")
    print("  3. Salir por ahora")
    opcion = input("\n  Elegí una opción: ").strip()

    if opcion == "1":
        if os.path.exists("scanner.py"):
            print("\n--- Iniciando ModScanner VT ---\n")
            subprocess.run([sys.executable, "scanner.py"])
        else:
            print("❌ No se encontró scanner.py en esta carpeta.")
    elif opcion == "2":
        if os.path.exists("monitor.py"):
            print("\n--- Iniciando Monitor en tiempo real ---")
            print("   Presioná Ctrl+C para detenerlo cuando quieras.\n")
            subprocess.run([sys.executable, "monitor.py"])
        else:
            print("❌ No se encontró monitor.py en esta carpeta.")
    else:
        print("\n✅ Configuración lista. Podés ejecutar cuando quieras:")
        print("   python scanner.py   — escaneo manual")
        print("   python monitor.py   — monitor en tiempo real")

def main():
    print("=" * 50)
    print("  ⚙️  INSTALADOR / CONFIGURADOR — ModScanner VT")
    print("=" * 50)
    
    instalar_dependencias()
    
    if os.path.exists("config.py"):
        if input("\n⚠️ El archivo config.py ya existe. ¿Sobreescribir? (s/n): ").lower() != 's':
            ejecutar_scanner()
            return

    api_key, ruta = pedir_datos()
    generar_config(api_key, ruta)
    ejecutar_scanner()

if __name__ == "__main__":
    main()