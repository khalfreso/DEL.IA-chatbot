"""
translation.py
Módulo principal de traducción para el chatbot.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional
import os, re, shutil
from datetime import datetime
from dotenv import load_dotenv
from docx import Document
from openai import OpenAI
from utils.glosario import GLOSARIO

# ---------------------------------------------------------------------------
# Configuración básica (rutas, cliente, constantes)
# ---------------------------------------------------------------------------
BACKEND_URL   = os.getenv("BACKEND_URL", "http://localhost:8000")
PROJECT_ROOT  = Path(__file__).resolve().parents[2]  # Raíz del repo
ROOT_DIR      = Path(__file__).resolve().parents[1]  # backend/
load_dotenv(PROJECT_ROOT / ".env")

DOCS_DIR = Path(os.getenv("DOCS_DIR", ROOT_DIR / "docs")).expanduser()
DOCS_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()

IDIOMA_USUARIO = "es"   # Idioma por defecto del usuario

# ---------------------------------------------------------------------------
# Utilidades de glosario
# ---------------------------------------------------------------------------

def _bloque_glosario() -> str:
    """Devuelve una representación en columnas del glosario global."""
    return "\n".join(f"{k:<12}→ {v}" for k, v in GLOSARIO.items())


def _matches_glosario(src: str) -> Dict[str, str]:
    """Busca los términos del glosario que aparecen en *src* (ignorando mayúsculas)."""    
    found: Dict[str, str] = {}
    for term, esp in GLOSARIO.items():
        if re.search(rf"\b{re.escape(term)}\b", src, flags=re.I):
            found[term] = esp
    return found


def _forzar_glosario(rep: Dict[str, str], text: str) -> str:
    """Aplica las sustituciones de *rep* dentro de *text* respetando mayúsculas.
    Se usa tras la traducción para obligar a que determinados slurs/insultos se
    mantengan con la traducción exacta indicada en el glosario.
    """
    for k, v in rep.items():
        text = re.sub(rf"\b{re.escape(k)}\b", v, text, flags=re.I)
    return text

# ---------------------------------------------------------------------------
# Construcción de prompts
# ---------------------------------------------------------------------------

def _construir_prompt(texto: str, destino: str, origen: Optional[str]) -> tuple[str, Dict[str,str]]:
    """Construye el prompt para la API de openAI y devuelve términos detectados en el glosario.
    Devuelve:
        prompt: Prompt completo para enviar a OpenAI.
        pares:  Diccionario con las entradas de glosario encontradas.
    """    
    prefijo = ""
    if texto.startswith("##INFORME##"):
        prefijo, texto = "##INFORME##", texto.split("##INFORME##", 1)[1].strip()

    # Determina idioma de origen si no se especifica
    if not origen:
        origen = "es" if destino != "es" else IDIOMA_USUARIO

    # Detecta slurs del glosario solo si origen no es español
    pares = _matches_glosario(texto) if origen != "es" else {}
    glosario   = _bloque_glosario() if pares else ""

    # Prompt template
    # ----------------- Español → otro idioma -----------------
    if origen == "es":
        prompt = f"""
### Rol ###
Eres un traductor profesional y trabajas en un chatbot de denuncia de delitos de odio.
Tu trabajo es traducir los mensajes generados por el asistente y deben transmitir cercanía, empatía y respaldo a la persona que habla.

### Objetivo ###
Convertir al idioma «{destino}» los mensajes de respuesta del asistente originales en español, usando un tono claro, cálido y de apoyo, sin alterar su contenido ni añadir elementos extra.

## Traducción: español → «{destino}»

### Instrucciones ###
1. Traduce del español al idioma «{destino}» **de manera fiel** al contenido original.
2. Mantén el tono y el estilo del texto en el idioma original (español)
3. No modifiques URLs, ni nombres de usuario con @  
4. Conserva comillas, guiones y saltos de línea tal como en el original.  
5. Si el texto original contiene emojis, mantenlos, pero no añadas emojis nuevos.
6. No añadas comillas ni signos de puntuación que no estén presentes en el original
7. Traduce SIEMPRE al idioma «{destino}» y responde exclusivamente en ese idioma.
8. **No añadas ni elimines** ninguna palabra ni frase que no esté presente en el original.
9. Devuelve únicamente el texto traducido, bajo ningún concepto añadas prefijos como "FR:" o explicaciones como "Traducción:", "Texto traducido", etc.  

──────────────
### Ejemplos ###
ES: “Hola, ¿cómo te sientes hoy? Estoy aquí para ayudarte.”  
{destino}: “Hi, how are you feeling today? I’m here to support you.”

ES: “Lamento mucho lo ocurrido. Tienes todo mi respaldo.”  
{destino}: “I’m really sorry for what happened. You have my full support.”

──────────────
Ahora traduce el siguiente texto siguiendo las reglas:

{texto}

Traducción:
"""
    # ----------------- Origen ≠ es → español -----------------
    else:
        prompt = f"""
### Rol ###
Eres un traductor profesional, con amplia experiencia en la traducción fiel de mensajes sensibles y lenguaje ofensivo.
Vas a traducir los mensajes que provienen del usuario (en el idioma {origen}). 
Estos mensajes pueden incluir relatos de casos de actos de odio, insultos fuertes, lenguaje malsonante o slurs.

### Objetivo ###
Mantener el tono y la literalidad de los textos del usuario. 
No suavizar ni censurar en los casos en los que se incluyan insultos, slurs o lenguaje malsonante. 
La versión traducida al español debe conservar exactamente la misma carga emocional.

### Glosario controlado de slurs ###
Usa **exactamente** estas correspondencias; no inventes sinónimos ni suavices:
{glosario}

---
## Traducción: «{origen}» → español

### Instrucciones generales ###
1. Traduce **literalmente** al español, respetando cada matiz del original.
2. Conserva la **intensidad** y **gravedad** de cada término, insulto o slur:  
   - Si el original contiene un término ofensivo, elige un término igual de ofensivo en español. **No suavices** ni censures bajo ningún concepto. 
   - Si el original contiene un término neutro (como "lesbienne", "homosexuel"...), elige también un término neutro en español ("lesbiana", "homosexual"...).
3. No modifiques URLs, ni nombres de usuario con @  
4. Mantén comillas, guiones y saltos de línea idénticos al original.  
5. Si el texto original contiene emojis, mantenlos, pero no añadas emojis nuevos.
6. No cambies la puntuación innecesariamente.  
7. Devuelve únicamente el texto traducido, bajo ningún concepto añadas prefijos como "ES:" o explicaciones como "Traducción:", "Texto traducido", etc.  
8. **No añadas ni elimines** ninguna palabra que no esté en el original.

──────────────
### Ejemplo 1###
EN: Faggots like you are not welcome here. Go back to your fucking country.  
ES (esperado): Los maricones como tú no deberían estar aquí. Vete a tu puto país.

### Ejemplo 2###
FR:  Je suis lesbienne.  
ES (esperado): Soy lesbiana.

──────────────
Ahora traduce el siguiente texto siguiendo las reglas:

{texto}

Traducción:"""
    # Añade prefijo si procede (marca de informe)
    return ((prefijo + " " + prompt) if prefijo else prompt, pares)


def _construir_prompt_documento(texto: str, destino: str) -> str:
    instrucciones = [
        f"Traduce fielmente el siguiente texto del español al {destino}.",
        "Instrucciones estrictas:",
        "1. No elimines ninguna palabra ni frase del contenido original.",
        "2. No añadas ninguna palabra ni frase que no aparezca en el original.",
        "3. Mantén la estructura y formato del texto.",
        "4. No añadas explicaciones como \"Traducción:\", \"Texto traducido:\", \"EN:\", \"FR:\", etc.",
        "5. Devuelve únicamente el texto traducido, con la misma disposición y formato que el original.",
    ]
    if destino.lower().startswith("en"):
        instrucciones.append('6. Si encuentras el término "Documento de manifestación personal", tradúcelo siempre como "Personal statement document".')
    elif destino.lower().startswith("fr"):
        instrucciones.append('6. Si encuentras el término "Documento de manifestación personal", tradúcelo siempre como "Document de déclaration personnelle".')
    prompt = "\n".join(instrucciones) + "\nTexto a traducir:\n" + texto + "\n"
    return prompt
    

# ---------------------------------------------------------------------------
# Función principal de traducción
# ---------------------------------------------------------------------------

def traducir(texto: str, destino: str, origen: Optional[str] = None, *, dry_run: bool=False) -> str:
    """Traduce *texto* al idioma *destino* usando la API de OpenAI.
    Args:
        texto:    Texto a traducir.
        destino:  Idioma objetivo.
        origen:   Idioma de origen (opcional). Si None, se deduce heurísticamente.
        dry_run:  Si True, devuelve sólo el prompt generado.
    Devuelve:
        Cadena con la traducción (o el prompt si dry_run=True).
    """
    # Casos en los que no se debe traducir
    if not texto or destino == origen or texto.strip().startswith("/"):
        return texto
    
    # Construimos el prompt y detectamos slurs (pares) en un único paso
    prompt, pares = _construir_prompt(texto, destino, origen)

    # "Dry run": devolvemos el prompt sin pegar a la API (debug / tests)
    if dry_run:
        return prompt

    try:
        # Llamada a la API de Chat Completions de OpenAI
        rsp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1500,
        )
        out = rsp.choices[0].message.content.strip()
        out = _forzar_glosario(pares, out)
        if prompt.startswith("##INFORME##"):
            return "##INFORME## " + out
        return out
    except Exception as e:
        print("[ERROR] Traducción GPT:", e)
        return texto

# ---------------------------------------------------------------------------
# Funciones auxiliares para informes DOCX (idénticas a la versión anterior)
# ---------------------------------------------------------------------------

def traducir_informe_original(nombre_docx: str, idioma_destino: str) -> str | None:
    """
    Crea una versión traducida del documento en formato DOCX,
    preservando estructura y formato principal de cada párrafo/celda.
    """
    try:
        # Comprobar existencia del original
        src = DOCS_DIR / nombre_docx
        if not src.exists():
            raise FileNotFoundError("Documento original no encontrado")
        # Copiar con nombre único
        stamp      = datetime.now().strftime("%Y%m%d_%H%M%S")
        nuevo_name = f"document_{idioma_destino}_{stamp}.docx"  
        target = DOCS_DIR / nuevo_name
        shutil.copy(src, target)

        doc = Document(str(target))

        def traducir_y_reemplazar(parrafo):
            texto = parrafo.text
            if texto.strip():
                prompt = _construir_prompt_documento(texto, idioma_destino)
                rsp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    max_tokens=1000,
                )
                traduccion = rsp.choices[0].message.content.strip()
                # Guardar formato principal del primer run
                if parrafo.runs:
                    run_fmt = parrafo.runs[0]
                    bold = run_fmt.bold
                    italic = run_fmt.italic
                    underline = run_fmt.underline
                    font_name = run_fmt.font.name
                    font_size = run_fmt.font.size
                else:
                    bold = italic = underline = font_name = font_size = None
                # Limpiar todos los runs y poner traducción en uno solo
                for run in parrafo.runs:
                    run.text = ""
                nuevo_run = parrafo.add_run(traduccion)
                nuevo_run.bold = bold
                nuevo_run.italic = italic
                nuevo_run.underline = underline
                if font_name:
                    nuevo_run.font.name = font_name
                if font_size:
                    nuevo_run.font.size = font_size

        # --- Párrafos principales ---
        for p in doc.paragraphs:
            traducir_y_reemplazar(p)
        # --- Tablas ---
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        traducir_y_reemplazar(p)
        # Guardar y devolver URL        
        doc.save(target)
        return f"{BACKEND_URL}/docs/{target.name}"
    except Exception as e:
        print("[ERROR] traducir_informe_original:", e)
        return None



def generar_mensaje_informe(msg_base: str, nombre_docx: str, idioma: str) -> str:
    """
    Devuelve el mensaje al usuario con enlaces al documento de manifestación personal para mostrar en el front.
    """
    idioma = idioma.strip().lower()
    if idioma == "es":
        return msg_base # Si el idioma es español no hay que hacer nada con el mensaje
    url_original  = f"{BACKEND_URL}/docs/{nombre_docx}"
    url_traducida = traducir_informe_original(nombre_docx, idioma)
    if not url_traducida:
        raise RuntimeError("No se pudo traducir el informe.")
    # Plantillas de mensaje por idioma
    if idioma == "en":
        return (
            f"Your document is ready. <a href=\"{url_traducida}\" target=\"_blank\">Click here</a> to download it.\n"
            f"You can also download the <a href=\"{url_original}\" target=\"_blank\">Spanish version</a>."
        )
    if idioma == "fr":
        return (
            f"Votre document est prêt. <a href=\"{url_traducida}\" target=\"_blank\">Cliquez ici</a> pour le télécharger.\n"
            f"Vous pouvez également télécharger la <a href=\"{url_original}\" target=\"_blank\">version espagnole</a>."
        )
    # fallback
    return msg_base