// -------------- DOM Elements --------------
const input = document.getElementById("input");
const chatWindow = document.getElementById("ventana-chat");


let indicadorActual = null;
let isMuted = false;
let currentAudio = null;

function mostrarIndicadorDeEspera() {
  if (indicadorActual) return; // evita duplicados
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "mensaje bot typing-indicator";
  typingIndicator.innerHTML = `
    <span class="bot-dot"></span>
    <span class="bot-dot"></span>
    <span class="bot-dot"></span>`;
  chatWindow.appendChild(typingIndicator);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  indicadorActual = typingIndicator;
}

function reproducirAudio(url) {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }

  if (isMuted) return;

  const audio = new Audio(url);
  currentAudio = audio;

  const perfilImg = document.getElementById("perfil-img");

  audio.addEventListener("play", () => {
    perfilImg.src = "images/DELIA-HABLANDO1.gif";
  });

  audio.addEventListener("ended", () => {
    perfilImg.src = "images/DELIA_SALUDANDO-nobg.png";
  });

  audio.play().catch((e) => {
    console.warn("No se pudo reproducir el audio automáticamente:", e);
  });
}



// -------------- Show Bot Response and Buttons --------------
// Muestra la respuesta del bot
function mostrarRespuestaDelBot(data) {
  if (indicadorActual) {
    indicadorActual.remove();
    indicadorActual = null;
  }

  // Crear contenedor del mensaje del bot
  const botmensaje = document.createElement("div");
  botmensaje.className = "mensaje bot";

  // Obtener texto, si no hay, mensaje por defecto
  let texto = data.respuesta_traducida || data.respuesta_rasa || "Sin respuesta del bot.";

  // ── Convertir los saltos de línea en <br> para que se vean ──
  const htmlConSaltos = texto
    .replace(/\r\n/g, "\n")         // normaliza CRLF
    .replace(/\n\n/g, "<br><br>")   // dobles saltos como párrafos
    .replace(/\n/g, "<br>");        // saltos simples

  // Volcar HTML ya preparado (con los <a> que vienen del backend)
  botmensaje.innerHTML = htmlConSaltos;
  chatWindow.appendChild(botmensaje);
  chatWindow.scrollTop = chatWindow.scrollHeight;

    // Reproducir el audio
  if (data.audio_url) {
    reproducirAudio(data.audio_url);
  }

  // Si el backend envía botones, pintarlos bajo el mensaje
  if (data.botones && data.botones.length > 0) {
    const cont = document.createElement("div");
    cont.className = "botones-opciones";

    data.botones.forEach((boton) => {
      const btn = document.createElement("button");
      btn.className = "boton-opcion";
      btn.textContent = boton.title;

      // Al pulsar un botón:
      // - quitar los botones
      // - pintar mensaje del usuario
      // - enviar payload
      btn.onclick = () => {
        cont.remove();

        const usermsg = document.createElement("div");
        usermsg.className = "mensaje user";
        usermsg.textContent = boton.title;
        chatWindow.appendChild(usermsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        mostrarIndicadorDeEspera();

        fetch("http://127.0.0.1:8000/procesar-y-enviar/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mensaje: boton.payload }),
        })
          .then((r) => r.json())
          .then((data) => {
            if (indicadorActual) {
              indicadorActual.remove();
              indicadorActual = null;
            }
            mostrarRespuestaDelBot(data);
          })
          .catch(() => {
            if (indicadorActual) {
              indicadorActual.remove();
              indicadorActual = null;
            }
            const err = document.createElement("div");
            err.className = "mensaje bot";
            err.textContent = "❌ Error al conectar con el servidor.";
            chatWindow.appendChild(err);
            chatWindow.scrollTop = chatWindow.scrollHeight;
          });
      };

      cont.appendChild(btn);
    });

    chatWindow.appendChild(cont);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
}


// -------------- Envío de mensajes --------------
input.addEventListener("keypress", function (e) {
  if (e.key === "Enter" && input.value.trim() !== "") {
    const usermensaje = document.createElement("div");
    usermensaje.className = "mensaje user";
    usermensaje.textContent = input.value.trim();
    chatWindow.appendChild(usermensaje);

    //Mostrar puntos animados como mensaje del bot
    mostrarIndicadorDeEspera();

    chatWindow.scrollTop = chatWindow.scrollHeight;

    const mensaje = input.value.trim();
    input.value = "";

    fetch("http://127.0.0.1:8000/procesar-y-enviar/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje })
    })
    .then((response) => response.json())
    .then((data) => {
      if (indicadorActual) {
        indicadorActual.remove();
        indicadorActual = null;
      } //Asegurarse de quitarlo también en caso de error

      mostrarRespuestaDelBot(data); // Show actual bot response
    })
    .catch((error) => {
      if (indicadorActual) {
        indicadorActual.remove();
        indicadorActual = null;
      }     //Asegurarse de quitarlo también en caso de error

      console.error("Error al enviar mensaje:", error);
      const err = document.createElement("div");
      err.className = "mensaje bot";
      err.textContent = "❌ Error al conectar con el servidor.";
      chatWindow.appendChild(err);
      chatWindow.scrollTop = chatWindow.scrollHeight;
      });
  }
});

// -------------- Grabación de audio --------------
let isRecording = false;
let mediaRecorder;
let audioChunks = [];

async function toggleRecording() {
  if (isRecording) {
    mediaRecorder.stop();
    document.getElementById('recordButton').innerHTML = '<img id="recordIcon" src="images/mic.svg" style="width: 30px; height: 30px" />';
    isRecording = false;
  } else {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);

        const audiomensaje = document.createElement('div');
        audiomensaje.classList.add('mensaje', 'user');

        const audioElement = document.createElement('audio');
        audioElement.controls = true;
        audioElement.src = audioUrl;

        audiomensaje.appendChild(audioElement);
        chatWindow.appendChild(audiomensaje);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        sendAudioToServer(audioBlob);
      };

      mediaRecorder.start();
      document.getElementById('recordButton').innerHTML = '<img id="recordIcon" src="images/arrow-right-short.svg" style="width: 30px; height: 30px" />';
      isRecording = true;
    } catch (err) {
      console.error('Error accessing the microphone:', err);
    }
  }
}

// Enviar audio al backend
function sendAudioToServer(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recorded_audio.wav');

    // ✅ Mostrar puntos animados
  mostrarIndicadorDeEspera();

  fetch('http://127.0.0.1:8000/procesar-y-enviar/', {
    method: 'POST',
    body: formData
  })
  .then((response) => response.json())
  .then((data) => {
    if (indicadorActual) {
      indicadorActual.remove();
      indicadorActual = null;
    } // Quitar los puntos animados  //Quitar los puntos animados            
    mostrarRespuestaDelBot(data);
  })
  .catch((error) => {
    if (indicadorActual) {
      indicadorActual.remove();
      indicadorActual = null;
    } //Asegurarse de quitarlo también en caso de error
    
    console.error("Error al enviar audio:", error);
    const botmensaje = document.createElement("div");
    botmensaje.className = "mensaje bot";
    botmensaje.textContent = "❌ Error al conectar con el servidor.";
    chatWindow.appendChild(botmensaje);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  });
}

// -------------- Mic Button Event Listener --------------
document.getElementById('recordButton').addEventListener('click', toggleRecording);

// -------------- Botón de silenciar --------------
document.getElementById("mute-button").addEventListener("click", () => {
  isMuted = !isMuted;

  const muteIcon = document.getElementById("mute-button").querySelector("img");
  muteIcon.src = isMuted ? "images/volume-mute.svg" : "images/volume-up.svg";

  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
    const perfilImg = document.getElementById("perfil-img");
    perfilImg.src = "images/DELIA_SALUDANDO-nobg.png";
  }
});

// -------------- Activar modo oscuro --------------
function toggleDarkMode() {
  document.body.classList.toggle("modo-oscuro");

  const isDark = document.body.classList.contains("modo-oscuro");
  document.querySelectorAll(".dark-toggle-icon").forEach(el => {
    el.style.filter = isDark ? "invert(1)" : "none";
  });
}

// -------------- Abrir panel de ajustes --------------
function toggleSettings() {
  document.getElementById("panel-ajustes").classList.toggle("open");
}

// -------------- Incrementar/Reducir el área de input de texto en función de las líneas escritas --------------
const textarea = document.getElementById("input");

textarea.addEventListener("input", () => {
  textarea.rows = 1;
  const lines = textarea.value.split("\n").length;
  textarea.rows = Math.min(lines, 10);
});

// -------------- Selección de idioma de conversación (no aplicable al texto estático) --------------
function setLanguageAndShowWelcome(lang, button) {

  // Poner puntos animados
  mostrarIndicadorDeEspera();

  fetch("http://127.0.0.1:8000/establecer-idioma-y-welcome/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idioma: lang })
  })
  .then((response) => response.json())
  .then((data) => {
    if (indicadorActual) {
      indicadorActual.remove();
      indicadorActual = null;
    } // Quitar los puntos animados

    mostrarRespuestaDelBot(data);
    const allButtons = document.querySelectorAll(".flag-button");
    allButtons.forEach(btn => {
      btn.classList.add("disabled");
      btn.classList.remove("selected");
    });
    button.classList.add("selected");
  })
  .catch((error) => {
    if (indicadorActual) {
      indicadorActual.remove();
      indicadorActual = null;
    } // Quitar los puntos animados
    console.error("Error al establecer idioma:", error);
  });
}


// Detectar idioma del navegador para traducir el texto estático
const langCode = (navigator.language || navigator.userLanguage).split('-')[0];

// Traducciones
// Título en la pestaña del navegador
const titles = {
  en: "DEL.IA Virtual Assistant",
  es: "Asistente Virtual DEL.IA",
  fr: "Assistant Virtuel DEL.IA"
};
// Descripción en barra lateral 1
const descripcion1 = {
  en: "DEL.IA is a virtual assistant that helps to detect and reduce unreported cases of hate in Spain. It listens to you, accompanies you and guides you on whether what you have experienced is a crime. In addition, you can access support services and receive a document that records your experience.",
  es: "DEL.IA es un asistente virtual que ayuda a detectar y reducir los casos de odio no denunciados en España. Te escucha, te acompaña y te orienta sobre si lo que has vivido es delito. Además, puedes acceder a servicios de apoyo y recibir un documento que recoja tu experiencia.",
  fr: "DEL.IA est un assistant virtuel qui aide à détecter et à réduire les cas de haine non signalés en Espagne. Il vous écoute, vous accompagne et vous aide à déterminer si ce que vous avez vécu est un crime. En outre, vous pouvez accéder à des services d'assistance et recevoir un document attestant de votre expérience.",
};
// Descripción en barra lateral 2
const descripcion2 = {
  en: "This is a project developed by the students of LeIA. Find out more about us and our project on social media:",
  es: "Este es un proyecto desarrollado por los alumnos de LeIA (2024/2025). Puedes descubrir más sobre nosotros y nuestro proyecto en nuestras redes sociales:",
  fr: "Il s'agit d'un projet développé par les étudiants de LeIA. Découvrez-nous et notre projet sur les médias sociaux :",
};
// Texto estático Seleccionar idioma
const idiomas_mensaje = {
  en: "Select your language:",
  es: "Selecciona un idioma:",
  fr: "Sélectionnez votre langue:",
};
// Disclaimer
const disclaimer = {
  en: "<strong>This conversation is private</strong>. All information you share during this conversation will be treated in strict confidence and will be used for support purposes only. We do <strong>not</strong> collect personally identifiable information; your participation will remain <strong>anonymous</strong>.\n\nAny assessment made by DEL.IA regarding hate crimes\nis for guidance only and <strong>has no legal validity</strong>.",
  es: "<strong>Esta conversación es privada</strong>. Toda la información que compartas durante esta conversación será tratada con estricta confidencialidad y se utilizará únicamente con fines de asistencia. <strong>No</strong> recopilamos información que permita identificarte personalmente; tu participación se mantendrá <strong>anónima</strong>.\n\nCualquier valoración realizada por DEL.IA en relación con los delitos de odio\nes meramente orientativa y <strong>carece de validez jurídica</strong>.",
  fr: "<strong>Cette conversation est privée</strong>. Toutes les informations que vous partagerez au cours de cette conversation seront traitées de manière strictement confidentielle et ne seront utilisées qu'à des fins d'assistance. Nous <strong>ne</strong> recueillons pas d'informations personnelles identifiables; votre participation restera <strong>anonyme</strong>.\n\nToute évaluation faite par DEL.IA concernant les crimes de haine\nest donnée à titre indicatif et <strong>n'a aucune valeur juridique</strong>."
}
// Placeholder de input
const placeholders = {
  en: "Type a message...",
  es: "Escribe un mensaje...",
  fr: "Tapez un message..."
};

// Función de traducción. Idioma fallback inglés
document.title = titles[langCode] || titles["en"];
document.getElementById("descripcion1-bot").textContent = descripcion1[langCode] || descripcion1["en"];
document.getElementById("descripcion2-bot").textContent = descripcion2[langCode] || descripcion2["en"];
document.getElementById("seleccion-idioma").textContent = idiomas_mensaje[langCode] || idiomas_mensaje["en"];
document.getElementById("disclaimer").innerHTML = (disclaimer[langCode] || disclaimer["en"]).replace(/\n/g, '<br>');
document.getElementById("input").placeholder = placeholders[langCode] || placeholders["en"];
