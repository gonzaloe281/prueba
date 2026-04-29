# ModScanner VT 🛡️

Este script de Python permite escanear de forma automática todos los archivos `.jar` (mods) de tus instancias de Modrinth utilizando la API de VirusTotal. Está diseñado para funcionar con cuentas gratuitas, respetando los límites de velocidad de la API.

## 🚀 Características

- **Escaneo Recursivo:** Busca automáticamente carpetas `/mods` dentro de las instancias de Modrinth.
- **Respeto de API Rate Limits:** Pausas automáticas de 25 segundos entre archivos.
- **Manejo de Errores:** Detecta si un archivo ya fue enviado o si el análisis tarda demasiado.
- **Guardado en tiempo real:** Los resultados se escriben en `resultados.json` mod tras mod.

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instalado:

- [Python 3.x](https://www.python.org/downloads/)
- Una cuenta en [VirusTotal](https://www.virustotal.com/) para obtener tu API Key gratuita.

## 🛠️ Instalación

1. **Clonar el repositorio:**

   ```gh repo clone gonzaloe281/prueba
   cd prueba
   ```

````
Instalar dependencias:
Este proyecto utiliza la librería oficial vt-py. Instálala usando pip:

    ```pip install vt-py
````

⚙️ Configuración

Para que el script funcione, debes crear un archivo llamado config.py en la carpeta raíz del proyecto.

Crea el archivo config.py.

Copia y pega el siguiente código, reemplazando los valores con los tuyos:

    ```Python

# config.py - Tu configuración personal

API_KEY = "TU_API_KEY_AQUI"

# Ruta donde Modrinth guarda las instancias (ajusta según tu usuario)

MODRINTH_PATH = r"C:\Users\TU_USUARIO\AppData\Roaming\ModrinthApp\profiles"

````
⚠️ IMPORTANTE: Nunca compartas tu config.py ni lo subas a GitHub, ya que contiene tu API Key privada. El archivo .gitignore de este repo ya está configurado para ignorarlo.

🚀 Uso

Ejecuta el script principal:
Bash

```python scanner.py
```

El script te preguntará cuántos archivos deseas analizar en la sesión actual. Al finalizar, verás los detalles en el archivo generado resultados.json.
📄 Licencia

Este proyecto es de uso personal. Revisa los términos de servicio de la API de VirusTotal antes de realizar escaneos masivos.

---

### Pasos adicionales recomendados:

1.  **Crea un archivo `.gitignore`**: Para evitar que por error subas tu clave a GitHub algún día, crea un archivo llamado `.gitignore` (literalmente así, empieza con un punto) en la misma carpeta y escribe esto adentro:

    ```text
    config.py
    resultados.json
    __pycache__/
    *.pyc
    ```

    Esto le dice a GitHub: "Ignora mi clave y mis resultados personales".

¿Te gustaría que agreguemos alguna sección más, como una tabla de cómo leer los resultados del JSON? Posiblemente en el futuro conmbine este codigo con DJango para hacerlo bonito,
si descubro como tirar los resultados del JSON a un HTML en principio, y si puedo tambien que se ejecute todo desde un navegador...
````
