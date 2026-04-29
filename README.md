# ModScanner VT 🛡️

Este script de Python permite escanear de forma automática todos los archivos `.jar` (mods) de tus instancias de Modrinth utilizando la API de VirusTotal. Está diseñado para funcionar con cuentas gratuitas, respetando los límites de velocidad de la API.

## 🚀 Características

- 🔍 **Detección de mods:** Encuentra automáticamente todas las instancias de Modrinth instaladas en tu PC y lista los archivos `.jar` dentro de cada una. No hace falta indicarle rutas manualmente más allá de la carpeta base configurada en `config.py`.

- 🗂️ **Menú interactivo:** Al ejecutar el programa aparece un menú donde podés elegir qué instancia analizar, y si querés analizar todos los mods nuevos de esa instancia o un mod específico de la lista. Esto evita tener que analizar todo cada vez que agregás un mod nuevo.

- 🧪 **Análisis con VirusTotal:** Sube cada mod a VirusTotal y lo analiza contra más de 70 motores antivirus. Al terminar muestra el veredicto directamente en la terminal junto con un link directo al reporte completo en la web de VirusTotal.

- 🧠 **Sistema de memoria (HASH-DB):** Cada mod analizado queda registrado en `resultados.json` mediante su huella digital SHA-256. La próxima vez que ejecutes el programa, los mods ya conocidos se saltean automáticamente — solo se analizan los que son nuevos. Esto ahorra tiempo y cuota de la API.

- 🗑️ **Eliminación de amenazas:** Si un mod es detectado como peligroso o sospechoso, el programa pregunta si querés eliminarlo. Si confirmás, borra el archivo directamente sin tener que hacerlo a mano.

- 🔄 **Mantenimiento automático de la base de datos:** Cada 90 días el programa limpia automáticamente los datos técnicos pesados de los registros viejos, conservando solo lo esencial: nombre del archivo, veredicto, link a VirusTotal y fecha del análisis. Esto evita que `resultados.json` crezca indefinidamente con el tiempo.

- 💾 **Guardado progresivo:** Los resultados se guardan después de cada mod analizado, no al final. Si el programa se interrumpe a mitad de un escaneo, los resultados anteriores no se pierden y la próxima ejecución retoma desde donde quedó.

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instalado:

- [Python 3.x](https://www.python.org/downloads/)
- Una cuenta en [VirusTotal](https://www.virustotal.com/) para obtener tu API Key gratuita.

## 🛠️ 1. Instalación

**A. Clonar el repositorio:**

```
gh repo clone gonzaloe281/prueba
cd prueba
```

**B.Instalar dependencias:**
Este proyecto utiliza la librería oficial vt-py. Instálala usando pip:

```
pip install vt-py
```

## ⚙️ 2. Configuración

Para que el script funcione, debes crear un archivo llamado config.py en la carpeta raíz del proyecto.

Crea el archivo config.py.

Copia y pega el siguiente código, reemplazando los valores con los tuyos:

```
# config.py - Tu configuración personal

API_KEY = "TU_API_KEY_AQUI"

# Ruta donde Modrinth guarda las instancias (ajusta según tu usuario)

MODRINTH_PATH = r"C:\Users\TU_USUARIO\AppData\Roaming\ModrinthApp\profiles"
```

⚠️ IMPORTANTE: Nunca compartas tu config.py ni lo subas a GitHub, ya que contiene tu API Key privada.
El archivo .gitignore de este repo ya está configurado para ignorarlo.

## 🚀 3. Uso

Ejecuta el script principal:

```
python scanner.py
```

El script te preguntará cuántos archivos deseas analizar en la sesión actual. Al finalizar, verás los detalles en el archivo generado resultados.json.

---

📄 Licencia

Este proyecto es de uso personal. Revisa los términos de servicio de la API de VirusTotal antes de realizar escaneos masivos.

---

### Pasos adicionales recomendados:

**Crea un archivo `.gitignore`**: Para evitar que por error subas tu clave a GitHub algún día, crea un archivo llamado
`.gitignore` (literalmente así, empieza con un punto) en la misma carpeta y escribe esto adentro:

```text
 config.py
 resultados.json
 __pycache__/
 *.pyc
```

Esto le dice a GitHub: "Ignora mi clave y mis resultados personales".

---

¿Te gustaría que agreguemos alguna sección más, como una tabla de cómo leer los resultados del JSON? Posiblemente en el futuro conmbine este codigo con DJango para hacerlo bonito,
si descubro como tirar los resultados del JSON a un HTML en principio, y si puedo tambien que se ejecute todo desde un navegador...
