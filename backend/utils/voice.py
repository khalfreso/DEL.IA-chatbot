# Función para identificar qué audio enviar
def voice_synthesis(text: str, diccionario_utters: dict, language_code: str) -> str:
    
    audio_file = diccionario_utters.get(text)

    # Condición: El texto se encuentra tal y como está en el diccionario
    if text in diccionario_utters:
        audio_file = diccionario_utters.get(text)

    # Si el texto no se encuentra en el diccionario (probablemente por motivos de formato o de slots de rasa),
    # se intenta matchear el principio o el final del texto
    elif text.startswith("Gracias por la información"):

        if text.endswith("que sea importante para ti?"):
            audio_file = "utter_inform_perfil_victima2_v1"

        else:
            audio_file = "utter_inform_perfil_victima2_v2"

    elif text.startswith("Si has sido testigo"):
        audio_file = "action_recursos_denuncia"

    elif text.endswith("y así ves el resultado?"):
        audio_file = "utter_recordatorio_redactar_informe"

    elif text.endswith("para ver los datos de contacto:"):
        audio_file = "utter_agradecer_no_denuncia"

    elif text.endswith("puede cambiar mucho las cosas."):
        audio_file = "utter_despedida"
    
    # Fallback por si no se encuentra audio
    else:
        audio_file = None
    
    # Archivo de audio en URL con condición de posible fallback
    audio_url = f"http://127.0.0.1:8000/audios/{language_code.upper()}/{audio_file}.wav" if audio_file else None

    return audio_url

# Diccionario de utters, lo usaremos para identificar qué audio hay que enviar en función del idioma y el texto

diccionario_utters = {

    """No pasa nada, seguimos con el cuestionario."""
    : "action_no_responde",

    """Es estupendo que quieras aprender más sobre este tema.
Un delito de odio se produce cuando alguien ataca, insulta o trata mal a otra persona solo por ser quien es. Normalmente, se utiliza como insulto el color de piel, las ideas, la religión, el país de procedencia, la orientación sexual, la situación económica, el sexo (hombre o mujer) o la existencia de una enfermedad o una discapacidad.
En cuanto al agresor, no se trata solo de lo que hace, sino también de lo que dice o comparte y si eso provoca odio o violencia hacia otras personas.
Si te ha pasado algo así o lo has visto, no dudes en pedir ayuda. Recuerda que estoy aquí para:"""
    : "action_delito_odio",

    """Si has sido testigo o te has enfrentado a una situación que crees que puede ser un delito de odio, puedes denunciar en tu comisaría más cercana o ponerte en contacto con Diaconía
a través del número +34 677 614 068 o mandando un correo electrónico a sinetiquetassinodio@diaconia.es, dónde abogados y psicólogos te apoyaran y explicarán los pasos a seguir.
 También puedes contar conmigo para:"""
    : "action_recursos_denuncia",

    """Agradezco mucho que hayas compartido tu relato de los hechos conmigo. Sé que no siempre es fácil hacerlo, pero este es un paso muy importante para conseguir justicia. No quiero despedirme sin antes ofrecerte algunos recursos que podrían serte de gran ayuda. En estas delegaciones de Diaconía encontrarás apoyo humano, como abogados, psicólogos y trabajadores sociales, que pueden escucharte, orientarte y explicarte los pasos a seguir teniendo en cuenta tu situación. Selecciona la comunidad que te quede más cerca para ver los datos de contacto:"""
    : "utter_agradecer_no_denuncia",

    """Agradezco mucho que hayas compartido tu relato de los hechos conmigo. Sé que no siempre es fácil hacerlo, pero este es un paso muy importante para conseguir justicia."""
    : "utter_agradecer_v1",
    
    """Gracias por tomarte el tiempo necesario y confiar en este espacio. Has compartido información muy importante, lo que es igual a dar un gran paso hacia adelante."""
    : "utter_agradecer_v2",

    """Tu documento está listo. Haz clic en el hipervínculo para descargarlo.
    Gracias por tomarte el tiempo necesario y confiar en este espacio. Has compartido información muy importante, lo que es igual a dar un gran paso hacia adelante."""
    : "utter_agradecimiento_final",

    """Gracias por haber compartido conmigo toda esta información, es muy valiosa. Ahora, para poder orientarte mejor, es importante saber si ya hay un proceso legal en curso. ¿Estos hechos ya han sido denunciados ante alguna autoridad u organismo oficial?"""
    : "utter_denuncia_hechos",

    "Ha sido un placer poder acompañarte, {nombre_victima}. No olvides que, si me necesitas otra vez, estaré disponible para ti en cualquier momento. ¡Y, por cierto! No dudes en hablarle de mí a otras personas que puedan haber pasado o estén pasando por una situación similar. Contarlo y actuar puede cambiar mucho las cosas."
    : "utter_despedida",

    """De acuerdo, podemos hablar en otro momento. Aun así, recuerda de que todas las personas merecen ser respetadas tal y como son. ¡Y, por cierto! No dudes en hablarle de mí a otras personas que puedan haber pasado o estén pasando por una situación similar. Contarlo y actuar puede cambiar mucho las cosas. Estoy aquí siempre que me necesites."""
    : "utter_despedida_concienciadora",

    """Entiendo, no pasa nada. Seguimos con el cuestionario."""
    : "utter_entiendo",

    """Lo siento, pero no te puedo ayudar con eso."""
    : "utter_fallback",

    """¿Cuándo ocurrió lo sucedido? Puede ser una fecha y hora específicos o un período aproximado."""
    : "utter_fecha_redes_v1",

    """¿En qué fecha o período tuvo lugar lo que pasó en redes? Si no lo recuerdas bien puedes darme datos aproximados."""
    : "utter_fecha_redes_v2",
    
    """Gracias por compartir todo esto conmigo. ¿Quieres que prepare un resumen con lo que me has contado para que puedas guardarlo como documento?"""
    : "utter_generar_informe_ofrecimiento",

    """Los testigos son una parte muy importante en procesos como este porque pueden aportar información que respalde tu versión de los hechos. Por eso, necesitamos detalles, por pequeños que sean, para ayudar a las autoridades a localizarlos. ¿Me podrías dar una descripción física de esa persona, o algún dato relevante como, por ejemplo, dónde se encontraba en el momento del incidente? ¿Estaba cerca de ti o lejos? ¿Qué hacía mientras pasaba este acontecimiento? ¿Trabajaba en el lugar donde sucedió todo?  Cualquier cosa que recuerdes, aunque no aparezca en estas preguntas, es útil."""
    : "utter_info_testigos",

    """Genial, antes de que me cuentes lo que ha pasado necesito conocerte mejor. ¿Podrías decirme tu nombre, edad, género y nacionalidad?"""
    : "utter_inform_perfil_victima1",

    """Gracias por la información, {nombre_victima}. Entender con qué grupo social te identificas puede ayudarme a comprender mejor lo que pasó.
       ¿Te reconoces como LGTBIQ+, formas parte de una comunidad religiosa o de algún otro colectivo que sea importante para ti?"""
    : "utter_inform_perfil_victima2_v1",

    """Gracias por la información, {nombre_victima}. ¿Te sientes parte de alguna comunidad, etnia o grupo, como por ejemplo LGTBIQ+, una comunidad religiosa u otro colectivo que pueda ser importante para lo sucedido? Esto me puede ayudar a entender mejor tu situación."""
    : "utter_inform_perfil_victima2_v2",

    """Está bien, no es una cosa que sea obligatoria. De todas formas, si cambias de idea más adelante, puedo ayudarte a generarlo."""
    : "utter_informe_no",

    """Perfecto, dentro de unos segundos estará listo para que te lo puedas descargar."""
    : "utter_informe_si",

    """Gracias por compartir todo esto conmigo. Si hay algo más que recuerdes y te gustaría añadir, puedes hacerlo ahora. Antes de que continuemos, me gustaría hacerte una pregunta más. ¿Crees que hubo algún motivo detrás de la agresión o el comportamiento de esas personas?"""
    : "utter_invita_relato_adicional_motivacion_plural_v1",

    """Lo que has contado hasta ahora es importante. Si sientes que quedó algo fuera o recuerdas algún otro detalle, puedes compartirlo ahora. Me gustaría preguntarte una cosa antes de que continuemos. ¿Te parece que había alguna razón específica por la que los agresores actuaron así?"""
    : "utter_invita_relato_adicional_motivacion_plural_v2",

    """Gracias por compartir todo esto conmigo. Si hay algo más que recuerdes y te gustaría añadir, puedes hacerlo ahora. Antes de que continuemos, me gustaría hacerte una pregunta más. ¿Crees que hubo algún motivo detrás de la agresión o el comportamiento de esa persona?"""
    : "utter_invita_relato_adicional_motivacion_v1",

    """Lo que has contado hasta ahora es importante. Si sientes que quedó algo fuera o recuerdas algún otro detalle, puedes compartirlo ahora. Me gustaría preguntarte una cosa antes de que continuemos. ¿Te parece que había alguna razón específica por la que el agresor actuó así?"""
    : "utter_invita_relato_adicional_motivacion_v2",

    """Agradezco que hayas compartido tu relato. Si se te ocurre algo más que quieras contar, puedes añadirlo ahora. Me gustaría preguntarte una cosa antes de que continuemos. ¿Te parece que había alguna razón específica por la que el agresor actuó así?"""
    : "utter_invita_relato_adicional_motivacion_v3",

    """Cuando quieras puedes empezar a contarme lo que te ha pasado. Para que todo sea más fácil, trata de seguir el orden en que ocurrió el incidente y, si puedes, reproduce mensajes o imágenes tal como las recuerdas."""
    : "utter_invita_relato_hechos_v1",

    """Este es un espacio seguro. Puedes contar todo lo que recuerdes sobre el incidente. Será todo más fácil si me lo cuentas en orden, incluyendo los mensajes o publicaciones, y describiendo cualquier contenido que te parezca relevante."""
    : "utter_invita_relato_hechos_v2",

    """¡Hola! Soy DEL.IA, un asistente virtual centrado en apoyarte si has vivido un acto de odio. Cuéntame, ¿con qué te gustaría que te ayude?"""
    : "utter_message",

    """¿Fueron una o varias las cuentas que participaron en lo sucedido?"""
    : "utter_num_agresores_redes",
    
    """¿Fue una sola persona o varias actuando juntas?"""
    : "utter_num_agresores_vida_real",

    """Entiendo, y está bien decir que no. Solo por si acaso, quiero que sepas que puede ser la forma de recibir un acompañamiento más ajustado a lo que necesitas, sin juzgarte y siempre con total confidencialidad. Tú decides el ritmo, ¿te animas a intentarlo?"""
    : "utter_pedir_confirmacion",

    """¿Podrías decirme en qué red o redes ocurrieron los hechos?"""
    : "utter_plataforma_redes_v1",

    """¿En qué redes sociales tuvo lugar lo sucedido?"""
    : "utter_plataforma_redes_v2",

    """¿A través de qué espacio digital sucedió el incidente?"""
    : "utter_plataforma_redes_v3",

    """¿Recuerdas el nombre de usuario, correo o perfil del agresor en la red social? (ej: @usuario, nombre en Facebook...) Si no te acuerdas no pasa nada, pero quizás puedas compartir detalles que son muy útiles para mí, por ejemplo: ¿sabías si esta cuenta seguía o estaba vinculada a grupos o páginas con ideologías de odio o compartía contenido de odio?"""
    : "utter_pregunta_cuenta_agresor_vinculacion_redes_v1",

    """¿Recuerdas el nombre de usuario, correo o perfil del agresor en la red social? (ej: @usuario, nombre en Facebook...) Si no te acuerdas no pasa nada, pero quizás puedas compartir detalles que son muy útiles para mí, por ejemplo: a veces los perfiles comparten contenido o usan imágenes de perfil o nombres relacionados con grupos extremistas. ¿Viste algo así?"""
    : "utter_pregunta_cuenta_agresor_vinculacion_redes_v2",

    """¿Recuerdas los nombres de usuario, correos o perfiles de los agresores en la red social? (ej: @usuario, nombre en Facebook...) Si no te acuerdas no pasa nada, pero quizás puedas compartir detalles que son muy útiles para mí, por ejemplo: ¿sabías si estas cuentas seguían o estaban vinculadas a grupos o páginas con ideologías de odio o compartían contenido de odio?"""
    : "utter_pregunta_cuenta_agresores_vinculacion_redes_v1",

    """¿Recuerdas los nombres de usuario, correos o perfiles de los agresores en la red social? (ej: @usuario, nombre en Facebook...) Si no te acuerdas no pasa nada, pero quizás puedas compartir detalles que son muy útiles para mí, por ejemplo: a veces los perfiles comparten contenido o usan imágenes de perfil o nombres relacionados con grupos extremistas. ¿Viste algo así?"""
    : "utter_pregunta_cuenta_agresores_vinculacion_redes_v2",

    """¿Me podrías decir cuándo ocurrió esto? Sería de gran ayuda si pudieras especificar el día y la hora a la que sucedió."""
    : "utter_pregunta_fecha_vida_real_v1",
    
    """¿Recuerdas el día exacto y la hora en que sucedió el incidente? Si lo compartes conmigo podremos contextualizar mejor todo lo que pasó."""
    : "utter_pregunta_fecha_vida_real_v2",

    """¿Puedes decirme el lugar o la zona donde ocurrió? Por ejemplo  la calle, local o si era algún sitio con un valor simbólico."""
    : "utter_pregunta_localizacion",

    """¿Hay algo más que quieras añadir sobre estas personas? (vestimenta, acento, cicatrices, piercings...). 
            Cualquier otro detalle, por pequeño que sea, podría ayudar. Antes de acabar con esta parte, me gustaría hacerte una pregunta más. ¿Sabes si esas personas estaban vinculadas a algún grupo con ideologías de odio o han mostrado con anterioridad otros actos de odio en persona o redes hacia alguien?"""
    : "utter_preguntar_caracteristicas_distintivas_grupo_odio_plural_v1",
    
    """Si hay algo más que quieras añadir sobre estas personas este es el momento (vestimenta, acento, cicatrices, piercings...). 
            Cualquier otro detalle, por pequeño que sea, podría ayudar. Antes de continuar, tengo una última pregunta sobre los agresores. ¿Sabes si estas personas ya habían actuado así con otras personas o pertenecían a algún grupo con idelogías de odio?"""
    : "utter_preguntar_caracteristicas_distintivas_grupo_odio_plural_v2",

    """¿Hay algo más que quieras añadir sobre esta persona? (vestimenta, acento, cicatrices, piercings...). 
            Cualquier otro detalle, por pequeño que sea, podría ayudar. Antes de acabar con esta parte, me gustaría hacerte una pregunta más. ¿Sabes si esa persona estaba vinculada a algún grupo con ideologías de odio o ha mostrado con anterioridad otros actos de odio en persona o redes hacia alguien?"""
    : "utter_preguntar_caracteristicas_distintivas_grupo_odio_v1",
    
    """Si hay algo más que quieras añadir sobre esta persona este es el momento (vestimenta, acento, cicatrices, piercings...). Cualquier otro detalle, por pequeño que sea, podría ayudar. Antes de continuar, tengo una última pregunta sobre el agresor. ¿Sabes si esta persona ya había actuado así con otras personas o pertenecía a algún grupo con ideologías de odio?"""
    : "utter_preguntar_caracteristicas_distintivas_grupo_odio_v2",

    """¿Ahora me podrías decir cómo era físicamente, si lo recuerdas? Cualquier detalle puede ser útil: pelo, complexión, altura, ropa... Además, es especialmente útil que me digas si llevaba tatuajes o algún símbolo que pudiera estar relacionado con el delito."""
    : "utter_preguntar_descripcion_agresor",
    
    """¿Ahora me podrías decir cómo eran físicamente, si lo recuerdas? Cualquier detalle puede ser útil: pelo, complexión, altura, ropa... Además, es especialmente útil que me digas si llevaban tatuajes o algún símbolo que pudiera estar relacionado con el delito."""
    : "utter_preguntar_descripcion_agresor_plural",

    """Para poder continuar ayudándote en este proceso voy a hacerte unas preguntas sobre los agresores. Recuerda que puedes compartir solo lo que te sientas cómodo/a mencionando, pero ten en cuenta que estas preguntas son muy útiles a la hora de poder estar más seguros sobre si se trata de un delito de odio o, por el contrario, hablamos de otro tipo de ofensa o delito. Para empezar, ¿podrías compartir los nombres o los apodos de las personas, si las conoces, y la edad o una aproximación?"""
    : "utter_preguntar_detalles_iniciales_plural",

    """Para poder continuar ayudándote en este proceso voy a hacerte unas preguntas sobre el agresor. Recuerda que puedes compartir solo lo que te sientas cómodo/a mencionando, pero ten en cuenta que estas preguntas son muy útiles a la hora de poder estar más seguros sobre si se trata de un delito de odio o, por el contrario, hablamos de otro tipo de ofensa o delito. Para empezar, ¿podrías compartir el nombre o el apodo de esa persona, si lo conoces, y la edad o una aproximación?"""
    : "utter_preguntar_detalles_iniciales_unico",

    """Este cuestionario se ha creado teniendo en cuenta factores que me ayudan a entender si has vivido una situación que podría ser un delito de odio. Todo esto me sirve para saber cómo poder guiarte y qué tipo de apoyo podrías necesitar. Sin embargo, si en algúm momento prefieres no contestar a una pregunta, podemos seguir adelante con el cuestionario sin ningún problema. Ahora que hemos aclarado el fin de este cuestionario, ¿quieres responder a la anterior pregunta o continuar con la siguiente?"""
    : "utter_proposito_cuestionario",

    """Estupendo. Ahora es primordial que conserves cualquier prueba que tengas: mensajes, fotos, capturas de pantalla, audios… Podrían ser útiles si decides denunciar. Antes de terminar con nuestra conversación, me gustaría ofrecerte un resumen estructurado con todo lo que me has contado. Este documento podría servirte si decides dar un paso más y denunciar. ¿Te gustaría que lo prepare para que te lo puedas descargar y así ves el resultado?"""
    : "utter_recordatorio_redactar_informe",

    """¿Conoces o identificas a la persona que actuó como agresor? Es decir, ¿tenías una relación previa con el agresor? ¿Había algún amigo, familiar, compañero de trabajo o, por el contrario, hablamos de un desconocido?"""
    : "utter_relacion_agresor",
    
    """¿Conoces o identificas a las personas que actuaron como agresores? Es decir, ¿tenías una relación previa con los agresores? ¿Había algún amigo, familiar, compañero de trabajo o, por el contrario, hablamos de desconocidos?"""
    : "utter_relacion_agresor_plural",

    """Perfecto. ¿Conoces a alguien que fuese testigo de lo que pasó en ese momento? Es decir, ¿había algún amigo, familiar, compañero de trabajo o, por el contrario, hablamos de desconocidos?"""
    : "utter_relacion_testigo",

    """Hola de nuevo. ¿En qué puedo ayudarte esta vez?"""
    : "utter_saludo",

    "Soy un bot, hecho con Rasa. Mi propósito es acompañar a personas que han podido ser víctimas de delitos de odio, ofreciéndoles un espacio seguro donde poder contar lo sucedido y poniendo a su alcance diferentes recursos dependiendo de sus necesidades."
    : "utter_soydelia",

    """De acuerdo, esta información es muy valiosa. Continuemos. A veces, en estas situaciones hay personas que han presenciado lo ocurrido y que pueden apoyar tu versión. ¿Sabes si había alguien presente durante el incidente que pudiera ver u oír lo que sucedió?"""
    : "utter_testigos",
    
    """Hablar de ello es el primer paso para que se haga justicia. Durante este proceso te haré algunas preguntas personales para crear un informe detallado y ayudarte a entender si lo que has vivido se trata de un delito de odio. Es importante tener en cuenta que cuanta más información me des, más fácil será poder ayudarte, pero no tienes por qué contestar a todo. Tu espacio y tu seguridad son lo más importante, por eso, esta conversación no quedará registrada en ningún lado. ¿Quieres que empecemos el cuestionario? Solo te llevará unos 10 minutos."""
    : "utter_testimonio",

    """¿El incidente sucedió a través de internet o en un lugar físico?"""
    : "utter_ubicar_medio"

}