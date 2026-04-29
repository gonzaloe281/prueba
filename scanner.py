# scanner.py - Escaneador de mods de Modrinth con VirusTotal
import os
import json
import time
import vt
import sys
from config import API_KEY, MODRINTH_PATH

def encontrar_archivos_mod(ruta_base):
    archivos = []
    for carpeta_raiz, subcarpetas, archivos_en_carpeta in os.walk(ruta_base):
        if os.path.basename(carpeta_raiz) == "mods":
            for nombre_archivo in archivos_en_carpeta:
                if nombre_archivo.endswith(".jar"):
                    ruta_completa = os.path.join(carpeta_raiz, nombre_archivo)
                    archivos.append(ruta_completa)
    return archivos

def analizar_archivo(cliente_vt, ruta_archivo):
    nombre = os.path.basename(ruta_archivo)
    instancia = os.path.basename(os.path.dirname(os.path.dirname(ruta_archivo)))
    print(f"  Analizando: {nombre}")
    try:
        with open(ruta_archivo, "rb") as f:
            analisis = cliente_vt.scan_file(f)
        
        tiempo_espera = 0
        while True:
            resultado = cliente_vt.get_object(f"/analyses/{analisis.id}")
            if resultado.status == "completed":
                stats = resultado.stats
                veredicto = "LIMPIO"
                if stats.get("malicious", 0) > 0:
                    veredicto = "PELIGROSO"
                elif stats.get("suspicious", 0) > 0:
                    veredicto = "SOSPECHOSO"
                
                return {
                    "instancia": instancia,
                    "archivo": nombre,
                    "veredicto": veredicto,
                    "detalles": dict(stats),
                    "estado": "OK"
                }
            
            if tiempo_espera > 120:
                return {"instancia": instancia, "archivo": nombre, "error": "Tiempo de espera agotado", "estado": "ERROR"}
            
            print(f"    Esperando resultado... ({tiempo_espera}s)")
            time.sleep(15)
            tiempo_espera += 15

    except vt.error.APIError as e:
        if "AlreadySubmittedError" in str(e):
            print(f"    [AVISO] Saltando: {nombre} ya está siendo procesado por VT.")
            return {"instancia": instancia, "archivo": nombre, "error": "AlreadySubmittedError", "estado": "REINTENTO"}
        return {"instancia": instancia, "archivo": nombre, "error": str(e), "estado": "ERROR"}
    except Exception as e:
        return {"instancia": instancia, "archivo": nombre, "error": str(e), "estado": "ERROR"}

def guardar_progreso(resultados):
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

def main():
    if not os.path.exists(MODRINTH_PATH):
        print(f"Error: No se encuentra la ruta {MODRINTH_PATH}")
        return

    mods = encontrar_archivos_mod(MODRINTH_PATH)
    total_encontrados = len(mods)
    print(f"Se encontraron {total_encontrados} archivos .jar")

    try:
        limite_usuario = int(input("¿Cuántos archivos deseas analizar en esta sesión?: "))
    except ValueError:
        print("Por favor, ingresa un número válido.")
        return

    resultados = []
    analizados_con_exito = 0
    indice_actual = 0

    with vt.Client(API_KEY) as cliente:
        while analizados_con_exito < limite_usuario and indice_actual < total_encontrados:
            ruta_mod = mods[indice_actual]
            print(f"\n[Progreso: {analizados_con_exito + 1}/{limite_usuario}]")
            
            resultado = analizar_archivo(cliente, ruta_mod)
            
            # Solo contamos si el archivo se procesó o dio un error definitivo (no si está repetido)
            if resultado.get("estado") != "REINTENTO":
                resultados.append(resultado)
                analizados_con_exito += 1
                guardar_progreso(resultados)
                
                veredicto = resultado.get('veredicto', 'ERROR')
                if veredicto != "ERROR":
                    print(f"    Veredicto: {veredicto}")
            
            indice_actual += 1

            # Pausa de seguridad si aún faltan archivos por procesar
            if analizados_con_exito < limite_usuario and indice_actual < total_encontrados:
                print("    Esperando 25s para el próximo archivo...")
                time.sleep(25)

    print(f"\nSesión finalizada. Se procesaron {analizados_con_exito} archivos.")
    print("Resultados guardados en resultados.json")

if __name__ == "__main__":
    main()