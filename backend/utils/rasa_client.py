"""
utils/rasa_client.py
~~~~~~~~~~~~~~~~~~~~
Pequeño wrapper sincrono para enviar mensajes a Rasa y
formatear la respuesta en el idioma del usuario.

Funciona junto con utils/translation.py
"""

from __future__ import annotations
import requests
from utils.translation import traducir

# URL base del webhook REST de Rasa
RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

__all__ = [
    "enviar_a_rasa",
    "extraer_respuesta_y_botones",
]


# ───────────────────────────────────────────────────────────
# 1) Enviar mensaje a Rasa
# ────────────────────────────────────────────────────────────

def enviar_a_rasa(mensaje: str) -> list:
    """
    Lanza una petición POST al webhook REST de Rasa
    y devuelve la lista JSON que incluye textos, botones, imágenes, etc.
    """
    payload = {"sender": "usuario", "message": mensaje}
    print(f"[DEBUG] Payload a Rasa: {payload}")
    response = requests.post(RASA_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    print(f"[DEBUG] Respuesta cruda de Rasa: {data!r}")
    return data



# ────────────────────────────────────────────────────────────
# 2) Procesar la respuesta y traducir si procede
# ────────────────────────────────────────────────────────────

def extraer_respuesta_y_botones(rasa_respuesta: list, idioma: str) -> tuple:
    '''
    Extrae el texto y los botones de la respuesta de Rasa y los traduce si es necesario
    '''
    # 1) Concatenar en orden todos los textos enviados por rasa
    respuestas = [m["text"] for m in rasa_respuesta if "text" in m]
    respuesta_original = "\n\n".join(respuestas)  # dos saltos define párrafos
    print(f"[DEBUG] Respuesta original: '{respuesta_original}'")
    # 2) Traducir todo junto
    respuesta_traducida = traducir(respuesta_original, destino=idioma, origen="es") if idioma != "es" else respuesta_original
    print(f"[DEBUG] Respuesta traducida: '{respuesta_traducida}'")
    # Extraer botones del último mensaje que tenga botones
    botones = []
    for m in reversed(rasa_respuesta):
        if "buttons" in m:
            botones = m["buttons"]
            break    
    # Traducir texto de los botones si es necesario
    if idioma != "es":
        for boton in botones:
            try:
                original = boton["title"]
                boton["title"] = traducir(original, destino=idioma, origen="es")
                print(f"[DEBUG] Botón traducido: '{original}' → '{boton['title']}'")
            except Exception as e:
                print(f"[ERROR] No se pudo traducir el botón '{original}': {e}")

    return respuesta_original, respuesta_traducida, botones