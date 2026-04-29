# setup.py - Configuración inicial de ModScanner VT
import os

LAUNCHERS = {
    "1": ("Modrinth",    r"C:\Users\TU_USUARIO\AppData\Roaming\ModrinthApp\profiles"),
    "2": ("CurseForge",  r"C:\Users\TU_USUARIO\curseforge\minecraft\Instances"),
    "3": ("Prism Launcher", r"C:\Users\TU_USUARIO\AppData\Roaming\PrismLauncher\instances"),
    "4": ("ATLauncher",  r"C:\Users\TU_USUARIO\ATLauncher\instances"),
    "5": ("GDLauncher",  r"C:\Users\TU_USUARIO\AppData\Roaming\gdlauncher_next\data\instances"),
    "6": ("Otro",        None),
}

def pedir_api_key():
    print("\n🔑 API Key de VirusTotal")
    print("   Podés obtenerla en: https://www.virustotal.com → perfil → API key\n")
    while True:
        api_key = input("   Ingresá tu API Key: ").strip()
        if len(api_key) >= 32:
            return api_key
        print("   ⚠️  La API Key parece incorrecta (muy corta). Intentá de nuevo.\n")

def pedir_ruta():
    while True:
        print("\n📁 Ruta de instancias de Minecraft")
        print("   Seleccioná tu launcher:\n")
        for key, (nombre, _) in LAUNCHERS.items():
            print(f"   {key}. {nombre}")

        opcion = input("\n   Elegí una opción: ").strip()
        if opcion not in LAUNCHERS:
            print("   ⚠️  Opción inválida. Elegí un número de la lista.")
            continue

        nombre, ruta_ejemplo = LAUNCHERS[opcion]

        if ruta_ejemplo:
            print(f"\n   Ruta por defecto de {nombre}:")
            print(f"   {ruta_ejemplo}")
            print(f"\n   Reemplazá TU_USUARIO con tu nombre de usuario de Windows.")

        while True:
            ruta = input("\n   Ingresá la ruta completa (o 'menu' para volver a elegir launcher): ").strip()

            if ruta.lower() == "menu":
                print("\n   🔙 Volviendo al menú de launchers...")
                break

            if not ruta:
                print("   ⚠️  La ruta no puede estar vacía. Intentá de nuevo.")
                continue

            # Limpia comillas si el usuario las pegó con ellas
            ruta = ruta.strip('"').strip("'")

            if not os.path.exists(ruta):
                print(f"\n   ❌ La ruta no existe o no se puede acceder: {ruta}")
                print("   Verificá que esté bien escrita y que el launcher esté instalado.\n")
                print("   ¿Qué querés hacer?")
                print("   1. Ingresar la ruta de nuevo")
                print("   2. Volver al menú de launchers")
                print("   3. Guardar igual y corregir después en config.py")
                accion = input("\n   Elegí una opción: ").strip()
                if accion == "1":
                    continue
                elif accion == "2":
                    print("\n   🔙 Volviendo al menú de launchers...")
                    break
                else:
                    print("   ⚠️  Guardando igual. Podés corregirla después en config.py")
                    return ruta
            else:
                print(f"   ✅ Ruta válida.")
                return ruta

def generar_config(api_key, ruta):
    contenido = f'''# config.py - Configuración personal de ModScanner VT
# Generado automáticamente por setup.py
# ⚠️ No subas este archivo a GitHub — ya está protegido por .gitignore

# API Key de VirusTotal
API_KEY = "{api_key}"

# Ruta donde tu launcher guarda las instancias de Minecraft
# Launchers compatibles: Modrinth, CurseForge, Prism, ATLauncher, GDLauncher y otros
INSTANCES_PATH = r"{ruta}"
'''
    with open("config.py", "w", encoding="utf-8") as f:
        f.write(contenido)

def main():
    print("=" * 50)
    print("  ⚙️  Configuración inicial — ModScanner VT")
    print("=" * 50)
    print("\nEste asistente va a crear tu archivo config.py.")
    print("Solo tenés que responder dos preguntas.\n")

    if os.path.exists("config.py"):
        print("⚠️  Ya existe un archivo config.py.")
        respuesta = input("   ¿Querés sobreescribirlo? (s/n): ").strip().lower()
        if respuesta != "s":
            print("\n❌ Configuración cancelada. Tu config.py no fue modificado.")
            return

    api_key  = pedir_api_key()
    ruta     = pedir_ruta()

    generar_config(api_key, ruta)

    print("\n" + "=" * 50)
    print("  ✅ config.py creado correctamente.")
    print("=" * 50)
    print("\nYa podés ejecutar el programa con:")
    print("\n   python scanner.py\n")

if __name__ == "__main__":
    main()