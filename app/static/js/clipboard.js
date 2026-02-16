(function () {
  async function copyTextFromElement(id, feedbackId) {
    const el = document.getElementById(id);
    if (!el) return;
    const text = el.innerText || el.value || "";
    const feedback = document.getElementById(feedbackId);
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      if (feedback) {
        feedback.textContent = "Copiado";
        setTimeout(function () {
          feedback.textContent = "";
        }, 1200);
      }
    } catch (_error) {
      if (feedback) {
        feedback.textContent = "Error al copiar";
        setTimeout(function () {
          feedback.textContent = "";
        }, 1600);
      }
    }
  }

  async function copyImageFromUrl(url, feedbackId) {
    const feedback = document.getElementById(feedbackId);
    try {
      const res = await fetch(url, { cache: "no-store" });
      const blob = await res.blob();
      if (!blob.type.startsWith("image/")) {
        throw new Error("El archivo no es una imagen");
      }
      if (!navigator.clipboard || !window.ClipboardItem) {
        throw new Error("Portapapeles de imagen no disponible");
      }
      await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
      if (feedback) {
        feedback.textContent = "Imagen copiada";
        setTimeout(function () {
          feedback.textContent = "";
        }, 1200);
      }
    } catch (_error) {
      if (feedback) {
        feedback.textContent = "No se pudo copiar; abre la imagen y copia manualmente";
        setTimeout(function () {
          feedback.textContent = "";
        }, 2500);
      }
    }
  }

  async function pasteImageToHidden(inputId, feedbackId) {
    const input = document.getElementById(inputId);
    const feedback = document.getElementById(feedbackId);
    if (!input) return;
    if (!navigator.clipboard || !navigator.clipboard.read) {
      if (feedback) {
        feedback.textContent = "El navegador no soporta pegar imagen";
      }
      return;
    }
    try {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        const type = item.types.find(function (it) {
          return it.startsWith("image/");
        });
        if (!type) continue;
        const blob = await item.getType(type);
        const reader = new FileReader();
        reader.onload = function () {
          input.value = String(reader.result || "");
          if (feedback) {
            feedback.textContent = "Imagen pegada y lista para guardar";
            setTimeout(function () {
              feedback.textContent = "";
            }, 1600);
          }
        };
        reader.readAsDataURL(blob);
        return;
      }
      if (feedback) {
        feedback.textContent = "No se detecto imagen en el portapapeles";
        setTimeout(function () {
          feedback.textContent = "";
        }, 1800);
      }
    } catch (_error) {
      if (feedback) {
        feedback.textContent = "No se pudo leer el portapapeles";
        setTimeout(function () {
          feedback.textContent = "";
        }, 1800);
      }
    }
  }

  window.copyTextFromElement = copyTextFromElement;
  window.copyImageFromUrl = copyImageFromUrl;
  window.pasteImageToHidden = pasteImageToHidden;
})();

