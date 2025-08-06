# backend/main.py
from fastapi import FastAPI, UploadFile, File, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
import tempfile, whisper
from utils.translation import traducir, generar_mensaje_informe
from utils.rasa_client import enviar_a_rasa, extraer_respuesta_y_botones
from utils.voice import voice_synthesis, diccionario_utters

# ───────────────── CONFIGURACIÓN DE ENTORNO ───────────────

load_dotenv()

# ───────────────── CONFIGURACIÓN DE RUTAS ─────────────────

DOCS_DIR = Path(__file__).resolve().parent / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


# ───────── FastAPI ─────────
app = FastAPI()
# Monta los .docx estáticos en /docs
app.mount("/docs", StaticFiles(directory=str(DOCS_DIR)), name="docs")
# Convertir los archivos de audio de la carpeta /audios en URLs para poder enviarlos al front-end
app.mount("/audios", StaticFiles(directory="audios"), name="audios")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────── MODELOS DE DATOS ─────────────────
class MensajeUsuario(BaseModel):
    mensaje: str

class IdiomaSeleccionado(BaseModel):
    idioma: str

# ───────── globals ─────────
IDIOMA_USUARIO = "es"       # español por defecto
whisper_model = whisper.load_model("medium")

# ───────────────── ENDPOINTS ─────────────────

# Establece el idioma del usuario y devuelve un mensaje de bienvenida
@app.post("/establecer-idioma-y-welcome/")
async def establecer_idioma_y_welcome(data: IdiomaSeleccionado):
    global IDIOMA_USUARIO
    IDIOMA_USUARIO = data.idioma.strip().lower()
    print(f"[DEBUG] Idioma establecido: {IDIOMA_USUARIO}")

    try:
        respuesta_rasa = enviar_a_rasa("/iniciar_sesion")
        texto, respuesta_traducida, botones = extraer_respuesta_y_botones(respuesta_rasa, IDIOMA_USUARIO)

        # Especificar mensaje de audio
        archivo_audio = voice_synthesis(texto, diccionario_utters, IDIOMA_USUARIO)
        print(f"""[DEBUG] Audio que se envía al front-end: {archivo_audio}""")

        return {
            "mensaje": f"Idioma establecido: {IDIOMA_USUARIO.upper()}",
            "respuesta_rasa": texto,
            "respuesta_traducida": respuesta_traducida,
            "botones": botones,
            "audio_url": archivo_audio
        }
    except Exception as e:
        print(f"[ERROR] Fallo al establecer idioma: {e}")
        return {"error": str(e)}


@app.post("/procesar-y-enviar/")
async def procesar_y_enviar(request: Request, audio: UploadFile = File(None)):
    # 1. Obtener mensaje en español (texto o audio)
    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        resultado = whisper_model.transcribe(tmp_path, language=IDIOMA_USUARIO)
        print(f"""[DEBUG] Audio recibido y transcrito, precisión: {resultado['segments'][0]['avg_logprob']}""")
        resultado_texto = resultado.get("text", "").strip()
        mensaje_es = traducir(resultado_texto, "es", IDIOMA_USUARIO) if IDIOMA_USUARIO != "es" else msg_usr
          
    else:
        body = await request.json()
        msg_usr = body.get("mensaje", "")
        mensaje_es = traducir(msg_usr, "es", IDIOMA_USUARIO) if IDIOMA_USUARIO != "es" else msg_usr

    # 2. Mandar a Rasa y traducir respuesta
    rsp_rasa = enviar_a_rasa(mensaje_es)
    texto, trad, botones = extraer_respuesta_y_botones(rsp_rasa, IDIOMA_USUARIO)

    # 2.1 Síntesis de voz
    archivo_audio = voice_synthesis(texto, diccionario_utters, IDIOMA_USUARIO)
    print(f"""[DEBUG] Audio que se envía al front-end: {archivo_audio}""")

    # 3. Si es informe, completar mensaje sin llamada HTTP
    if trad and trad.strip().startswith("##INFORME##"):
        # Eliminamos la marca de informe y quitamos espacios iniciales
        cont = trad.replace("##INFORME##", "").strip()
        # Separar mensaje de informe de mensaje de agradecimiento posterior
        informe_line, _, rest = cont.partition("\n\n")
        # Extraer mensaje base y nombre_docx
        msg_base, nombre_docx = (p.strip() for p in informe_line.split("|||", 1))
        # Generar HTML del informe con <a> embebido
        informe_html = generar_mensaje_informe(msg_base, nombre_docx, IDIOMA_USUARIO)
        # Utter de agradecimiento
        agradecimiento = rest.strip()
        # Volvemos a juntar ambas piezas
        respuesta_final = f"{informe_html}\n\n{agradecimiento}"
        return {
            "idioma_usuario":    IDIOMA_USUARIO,
            "mensaje_traducido": mensaje_es,
            "respuesta_rasa":    texto,
            "respuesta_traducida": respuesta_final,
            "botones":           botones,
        }
    # 4. Respuesta normal
    return {"idioma_usuario": IDIOMA_USUARIO,
            "mensaje_traducido": mensaje_es,
            "respuesta_rasa": texto,
            "respuesta_traducida": trad,
            "botones": botones,
            "audio_url": archivo_audio}
