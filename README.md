
# DEL.IA – Asistente Virtual para la Detección de Delitos de Odio

**DEL.IA** es un asistente virtual desarrollado con el framework **Rasa** para ayudar a identificar y documentar posibles casos de delitos de odio. Incluye:

- Un chatbot multilingüe con Rasa.
- Una interfaz web sencilla conectada a un backend con FastAPI.

Este README está dividido en tres partes:

- [✨ Instalación por primera vez (paso a paso)](#✨-instalación-por-primera-vez)
- [🚀 Uso diario: cómo lanzar el sistema](#-uso-diario-cómo-lanzar-el-sistema)
- [🔁 Rutina de trabajo con Git](#-rutina-de-trabajo-con-git)

---

## ✨ Instalación por primera vez

### 1. Clonar el repositorio

```bash
git clone https://github.com/proyectoDELIA/DEL.IA-chatbot.git
cd DEL.IA-chatbot
git checkout tu-rama-de-trabajo  
```

### 2. Preparar estructura local (sugerida)

Crea una carpeta externa para tus entornos virtuales (por ejemplo `C:\Envs`) y descomprime dentro cualquier ZIP con datos (si aplica).

### 3. Crear entorno virtual para Rasa
**Este entorno debe ser creado con Python 3.9**

```bash
cd C:\Envs
py -3.9 -m venv rasa_env
rasa_env\Scripts\activate
```

#### ⚠️ NOTAS
- Si usas Windows y hay errores con permisos al activar entornos, puedes usar:

  ```bash
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

- Para macOS/Linux

  ```bash
  python3.9 -m venv rasa_env
  source rasa_env/bin/activate
  ```

#### Instalar dependencias de Rasa

```bash
cd C:\ruta\al\proyecto\DEL.IA-chatbot
pip install -r requirements.txt
python -m spacy download es_core_news_md
```

### 4. Crear entorno virtual separado para servidor de acciones
**Este entorno debe ser creado con Python 3.9**

Rasa y LangChain requieren librerías incompatibles, por eso se utiliza un entorno aparte para el servidor de acciones.


```bash
cd C:\Envs
py -3.9 -m venv action_server_env
action_server_env\Scripts\activate
```

#### Instalar dependencias para acciones

```bash
cd C:\ruta\al\proyecto\DEL.IA-chatbot
pip install -r requirements_actions.txt
```

### 5. Crear entorno virtual para el backend (FastAPI)

**Este entorno debe ser creado con Python 3.10 o 3.11** para garantizar la compatibilidad con FastAPI y sus dependencias.

```bash
cd C:\Envs
py -3.10 -m venv backend_env  # o usa -3.11 si tienes esa versión instalada
backend_env\Scripts\activate
```

#### Instalar dependencias del backend

```bash
cd C:\ruta\al\proyecto\DEL.IA-chatbot
pip install -r requirements_backend.txt
```

#### ⚠️ NOTA
- También es necesario instalar FFMPEG en tu sistema (para el reconocimiento de voz). Para ello sigue estos pasos:
  1. Descarga `ffmpeg-git-full.7z` de https://www.gyan.dev/ffmpeg/builds/
  2. Descomprime el zip en una carpeta de tu sistema (por ejemplo, C:\ffmpeg).
  3. Dentro de la carpeta descomprimida, localiza el subdirectorio bin (por ejemplo, C:\ffmpeg\bin).
  4. Copia la ruta completa de esa carpeta (C:\ffmpeg\bin).
  5. Abre el Panel de Control y ve a Sistema > Configuración avanzada del sistema > Variables de entorno.
  6. En la sección "Variables del sistema", selecciona la variable Path y haz clic en Editar.
  7. Haz clic en Nuevo y pega la ruta C:\ffmpeg\bin (o la que corresponda en tu sistema).
  8. Acepta todos los cambios y cierra las ventanas.
  9. Abre una nueva terminal (cmd o PowerShell) y escribe ffmpeg -version para comprobar que se ha instalado correctamente.


### 6. Entrenar el chatbot

Con el entorno `rasa_env` activado y en la carpeta del chatbot:

```bash
cd C:\ruta\al\proyecto\DEL.IA-chatbot\chatbot
rasa train
```

---

## 🚀 Uso diario: cómo lanzar el sistema

Una vez instalado todo, cada vez que quieras ejecutar DEL.IA debes abrir 3 terminales y seguir estos pasos.

### 🔀 1. Lanzar el backend (FastAPI)

#### Terminal 1 (activar entorno del backend y lanzar servidor):

```bash
cd ruta/del/entorno/
backend_env\Scripts\activate 
cd ruta/del/proyecto/DEL.IA-chatbot/backend
uvicorn main:app --reload
```

Disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)\
Deja esta terminal abierta.

### ⚙️ 2. Lanzar servidor de acciones

#### Terminal 2 (activar entorno `action_server_env` y lanzar servidor de actions):

```bash
cd ruta/del/entorno/
action_server_env\Scripts\activate 
cd ruta/del/proyecto/DEL.IA-chatbot/chatbot
python -m rasa_sdk --actions actions
```

Disponible en: [http://localhost:5055](http://localhost:5055)
Deja esta terminal abierta.

### 🤖 3. Lanzar Rasa (core)

#### Terminal 3 (activar entorno `rasa_env` y lanzar rasa):

```bash
cd ruta/del/entorno/
rasa_env\Scripts\activate 
cd ruta/del/proyecto/DEL.IA-chatbot/chatbot
rasa run --enable-api
```

Disponible en: [http://localhost:5005/webhooks/rest/webhook](http://localhost:5005/webhooks/rest/webhook)
Deja esta terminal abierta.

### 🌐 4. Abrir el frontend

Abre el archivo `index.html` en `DEL.IA-chatbot\frontend` con tu navegador (solo abre la carpeta y haz doble clic sobre este).

---

### ⚠️ Notas adicionales

- Tienes que crear en la carpeta raíz `DEL.IA-chatbot\` un archivo .env que contenga la clave de OpenAI del proyecto. Deberá quedar algo así:

  ```
  OPENAI_API_KEY=tu_clave_aqui
  ```

- Para detener cualquiera de los servicios mientras se están ejecutando: pulsa `Ctrl + C` en la terminal correspondiente.

---


## 🔁 Rutina de trabajo con Git

Antes de empezar a trabajar cada día:

1. Abre una terminal y entra en el proyecto:

```bash
cd ruta/del/proyecto/DEL.IA-chatbot
```

2. Asegúrate de estar en tu rama:

```bash
git checkout tu-rama-de-trabajo
```

3. Trae los cambios del repositorio remoto:

```bash
git pull origin tu-rama-de-trabajo
```

4. Trabaja y haz cambios localmente.

5. Guarda y sube tus cambios:

```bash
git add .
git commit -m "Mensaje claro del cambio realizado"
git push origin tu-rama-de-trabajo
```

Si trabajas con ramas distintas y quieres integrar cambios de otra rama:

```bash
git fetch origin
git merge origin/otra-rama  # estando en tu rama actual
```

Si hay conflictos, resuélvelos en el editor y luego:

```bash
git add .
git commit  # finaliza el merge
```

> Consejo: trabaja con una rama propia y crea ramas nuevas cuando vayas a probar algo importante. Así evitas perder el trabajo estable que ya tenías.

---

## 📚 Licencia

En revisión. Actualmente uso interno en el contexto del máster. No redistribuir sin permiso.
