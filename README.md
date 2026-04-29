# ModScanner VT 🛡️

Este script de Python permite escanear de forma automática todos los archivos `.jar` (mods) de cualquier launcher de Minecraft utilizando la API de VirusTotal. Compatible con Modrinth, CurseForge, Prism Launcher, ATLauncher y cualquier otro launcher que organice los mods en subcarpetas `mods/`. Está diseñado para funcionar con cuentas gratuitas, respetando los límites de velocidad de la API.

---

## 🚀 Características

- 🔍 **Detección de mods:** Encuentra automáticamente todas las instancias de tu launcher de Minecraft y lista los archivos `.jar` dentro de cada una. Compatible con cualquier launcher que organice los mods en subcarpetas `mods/`. No hace falta indicarle rutas manualmente más allá de la carpeta base configurada en `config.py`.

- 🗂️ **Menú interactivo:** Al ejecutar el programa aparece un menú donde podés elegir qué instancia analizar, y si querés analizar todos los mods nuevos de esa instancia o un mod específico de la lista. Esto evita tener que analizar todo cada vez que agregás un mod nuevo.

- 🧪 **Análisis con VirusTotal:** Sube cada mod a VirusTotal y lo analiza contra más de 70 motores antivirus. Al terminar muestra el veredicto directamente en la terminal junto con un link directo al reporte completo en la web de VirusTotal.

- 🧠 **Sistema de memoria (HASH-DB):** Cada mod analizado queda registrado en `resultados.json` mediante su huella digital SHA-256. La próxima vez que ejecutes el programa, los mods ya conocidos se saltean automáticamente — solo se analizan los que son nuevos. Esto ahorra tiempo y cuota de la API.

- 🗑️ **Eliminación de amenazas:** Si un mod es detectado como peligroso o sospechoso, el programa pregunta si querés eliminarlo. Si confirmás, borra el archivo directamente sin tener que hacerlo a mano.

- 🔄 **Mantenimiento automático de la base de datos:** Cada 90 días el programa limpia automáticamente los datos técnicos pesados de los registros viejos, conservando solo lo esencial: nombre del archivo, veredicto, link a VirusTotal y fecha del análisis. Esto evita que `resultados.json` crezca indefinidamente con el tiempo.

- 💾 **Guardado progresivo:** Los resultados se guardan después de cada mod analizado, no al final. Si el programa se interrumpe a mitad de un escaneo, los resultados anteriores no se pierden y la próxima ejecución retoma desde donde quedó.

---

## 📋 Requisitos Previos

Si es la primera vez que trabajás con Python, seguí estos pasos antes de continuar. Si ya tenés todo instalado, podés saltarte directo a [Instalación](#-instalación).

### 🐍 1. Python

Descargá e instalá Python desde la página oficial:

👉 [https://www.python.org/downloads/](https://www.python.org/downloads/)

> ⚠️ Durante la instalación, asegurate de tildar la opción **"Add Python to PATH"** antes de hacer clic en instalar. Sin esto, el comando `python` no va a funcionar en la terminal.

Para verificar que quedó bien instalado, abrí una terminal y ejecutá:

```
python --version
```

Debería mostrarte algo como `Python 3.x.x`.

---

### 💻 2. Visual Studio Code (editor de código)

VSCode es el editor recomendado para trabajar con este proyecto.

👉 [https://code.visualstudio.com/](https://code.visualstudio.com/)

Una vez instalado, abrí VSCode e instalá la extensión oficial de Python:

- Presioná `Ctrl+Shift+X`
- Buscá **Python** (de Microsoft) e instalala

---

### 🐙 3. Git

Git es necesario para clonar este repositorio en tu PC.

👉 [https://git-scm.com/downloads](https://git-scm.com/downloads)

Durante la instalación podés dejar todas las opciones por defecto. Para verificar que quedó instalado:

```
git --version
```

---

### 🔑 4. API Key de VirusTotal

Necesitás una cuenta gratuita en VirusTotal para obtener tu clave de acceso a la API.

👉 [https://www.virustotal.com/](https://www.virustotal.com/)

Una vez registrado:

1. Hacé clic en tu foto de perfil arriba a la derecha
2. Seleccioná **API key**
3. Copiá la clave — la vas a necesitar en el paso de configuración

> ℹ️ El plan gratuito permite hasta **4 análisis por minuto**. El programa respeta este límite automáticamente.

---

## 🛠️ Instalación

**A. Clonar el repositorio:**

```
gh repo clone gonzaloe281/prueba
cd prueba
```

**B. Instalar dependencias:**

Este proyecto utiliza la librería oficial `vt-py`. Instalala usando pip:

```
pip install vt-py
```

---

## ⚙️ Configuración

Para que el script funcione necesitás crear un archivo llamado `config.py` en la carpeta raíz del proyecto.

**1.** Creá el archivo `config.py`

**2.** Copiá y pegá el siguiente contenido, reemplazando los valores con los tuyos:

```python
# config.py - Tu configuración personal

API_KEY = "TU_API_KEY_AQUI"

# Ruta donde tu launcher guarda las instancias de Minecraft
# Reemplazá con la ruta correspondiente a tu launcher:
INSTANCES_PATH = r"C:\Users\TU_USUARIO\AppData\Roaming\ModrinthApp\profiles"
```

**Rutas según launcher:**

| Launcher           | Ruta por defecto                                                     |
| ------------------ | -------------------------------------------------------------------- |
| **Modrinth**       | `C:\Users\TU_USUARIO\AppData\Roaming\ModrinthApp\profiles`           |
| **CurseForge**     | `C:\Users\TU_USUARIO\curseforge\minecraft\Instances`                 |
| **Prism Launcher** | `C:\Users\TU_USUARIO\AppData\Roaming\PrismLauncher\instances`        |
| **ATLauncher**     | `C:\Users\TU_USUARIO\ATLauncher\instances`                           |
| **GDLauncher**     | `C:\Users\TU_USUARIO\AppData\Roaming\gdlauncher_next\data\instances` |

> ⚠️ **IMPORTANTE:** Nunca compartas tu `config.py` ni lo subas a GitHub, ya que contiene tu API Key privada. El archivo `.gitignore` de este repositorio ya está configurado para ignorarlo automáticamente.

---

## ▶️ Uso

Ejecutá el script principal desde la terminal:

```
python scanner.py
```

El programa va a mostrar un menú interactivo donde podés elegir qué instancia y qué mods analizar. Al finalizar cada análisis, los resultados quedan guardados en `resultados.json`.

---

## 🔒 Seguridad adicional — `.gitignore`

Para asegurarte de que nunca subas accidentalmente tu clave o tus resultados a GitHub, verificá que tu archivo `.gitignore` contenga estas líneas:

```
config.py
resultados.json
__pycache__/
*.pyc
```

Esto le indica a Git que ignore esos archivos en todos los commits.

---

## 📄 Licencia

Este proyecto es de uso personal. Revisá los términos de servicio de la API de VirusTotal antes de realizar escaneos masivos.

---

> 💡 **Nota del autor:** Posiblemente en el futuro este proyecto se integre con Django para visualizar los resultados desde el navegador, mostrando los datos del JSON en una interfaz web completa.
