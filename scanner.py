# scanner.py - Escaneador de mods con VirusTotal y eliminación de amenazas
import os
import json
import time
import vt
import sys
from config import API_KEY, MODRINTH_PATH

def encontrar_archivos_mod(ruta_base):
    archivos = []
    # os.walk recorre solo lo que está dentro de MODRINTH_PATH
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
                    "ruta_completa": ruta_archivo,
                    "veredicto": veredicto,
                    "detalles": dict(stats),
                    "estado": "OK"
                }
            
            if tiempo_espera > 300:
                return {"instancia": instancia, "archivo": nombre, "error": "Timeout", "estado": "ERROR"}
            
            print(f"    Esperando resultado... ({tiempo_espera}s)")
            time.sleep(15)
            tiempo_espera += 15

    except vt.error.APIError as e:
        if "AlreadySubmittedError" in str(e):
            return {"instancia": instancia, "archivo": nombre, "error": "AlreadySubmittedError", "estado": "REINTENTO"}
        return {"instancia": instancia, "archivo": nombre, "error": str(e), "estado": "ERROR"}
    except Exception as e:
        return {"instancia": instancia, "archivo": nombre, "error": str(e), "estado": "ERROR"}

def guardar_progreso(resultados):
    with open("resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

def main():
    if not os.path.exists(MODRINTH_PATH):
        print(f"Error: La ruta de Modrinth no existe en este sistema.")
        return

    mods = encontrar_archivos_mod(MODRINTH_PATH)
    total_encontrados = len(mods)
    print(f"Se encontraron {total_encontrados} archivos .jar en las carpetas /mods")

    try:
        limite_usuario = int(input("¿Cuántos archivos deseas analizar en esta sesión?: "))
    except ValueError:
        return

    resultados = []
    analizados_con_exito = 0
    indice_actual = 0
    borrados_count = 0

    with vt.Client(API_KEY) as cliente:
        while analizados_con_exito < limite_usuario and indice_actual < total_encontrados:
            ruta_mod = mods[indice_actual]
            print(f"\n[Progreso: {analizados_con_exito + 1}/{limite_usuario}]")
            
            resultado = analizar_archivo(cliente, ruta_mod)
            
            if resultado.get("estado") != "REINTENTO":
                veredicto = resultado.get('veredicto', 'ERROR')
                print(f"    Veredicto: {veredicto}")

                # ELIMINACIÓN EN VIVO
                if veredicto in ["PELIGROSO", "SOSPECHOSO"]:
                    print(f"\n⚠️ AMENAZA DETECTADA: {resultado['archivo']}")
                    confirmar = input(f"    ¿Eliminar este mod de la carpeta de instancia? (s/n): ")
                    
                    if confirmar.lower() == 's':
                        try:
                            os.remove(resultado['ruta_completa'])
                            print("    [ELIMINADO] El archivo ya no está en el disco.")
                            resultado['borrado_por_usuario'] = True
                            borrados_count += 1
                        except Exception as e:
                            print(f"    [ERROR] No se pudo borrar: {e}")
                    else:
                        print("    [CONSERVADO] El archivo sigue en su carpeta.")
                        resultado['borrado_por_usuario'] = False

                resultados.append(resultado)
                analizados_con_exito += 1
                guardar_progreso(resultados)
            
            indice_actual += 1

            if analizados_con_exito < limite_usuario and indice_actual < total_encontrados:
                print("    Esperando 25s por límite de API...")
                time.sleep(25)

    # RESUMEN FINAL POR CONSOLA
    print("\n" + "="*30)
    print("       RESUMEN DE SESIÓN")
    print("="*30)
    print(f"  Analizados: {analizados_con_exito}")
    print(f"  Borrados:   {borrados_count}")
    print(f"  Limpios:    {len([r for r in resultados if r.get('veredicto') == 'LIMPIO'])}")
    print("="*30)

if __name__ == "__main__":
    main()