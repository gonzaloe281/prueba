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
    """Paso 1: Instala las librerías del requirements.txt automáticamente."""
    print("\n📦 PASO 1: Verificando e instalando dependencias...")
    if os.path.exists("requirements.txt"):
        try:
            # -m pip install asegura que use el pip del entorno actual (venv o global)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
            print("   ✅ Dependencias listas.")
        except Exception as e:
            print(f"   ❌ Error instalando dependencias: {e}")
    else:
        print("   ⚠️ No se encontró requirements.txt. Saltando este paso.")

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
    print("\n" + "="*50)
    confirmar = input("🚀 ¿Querés iniciar el escaneo ahora? (s/n): ").strip().lower()
    if confirmar == 's':
        if os.path.exists("scanner.py"):
            print("\n--- Iniciando ModScanner VT ---\n")
            subprocess.run([sys.executable, "scanner.py"])
        else:
            print("❌ No se encontró scanner.py en esta carpeta.")

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