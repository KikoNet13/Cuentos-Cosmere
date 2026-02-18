(function () {
  function setFeedback(feedbackId, message, timeoutMs) {
    const feedback = document.getElementById(feedbackId);
    if (!feedback) return;
    feedback.textContent = message;
    if (timeoutMs && timeoutMs > 0) {
      setTimeout(function () {
        feedback.textContent = "";
      }, timeoutMs);
    }
  }

  async function copyTextFromElement(id, feedbackId) {
    const el = document.getElementById(id);
    if (!el) return;
    const text = el.innerText || el.value || "";
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
      setFeedback(feedbackId, "Copiado", 1200);
    } catch (_error) {
      setFeedback(feedbackId, "Error al copiar", 1600);
    }
  }

  async function copyImageFromUrl(url, feedbackId) {
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
      setFeedback(feedbackId, "Imagen copiada", 1200);
    } catch (_error) {
      setFeedback(feedbackId, "No se pudo copiar; abre la imagen y copia manualmente", 2500);
    }
  }

  async function _readClipboardImageBlob() {
    if (!navigator.clipboard || !navigator.clipboard.read) {
      throw new Error("unsupported");
    }

    const items = await navigator.clipboard.read();
    for (const item of items) {
      const type = item.types.find(function (it) {
        return it.startsWith("image/");
      });
      if (!type) continue;

      const blob = await item.getType(type);
      if (blob && blob.size > 0) return blob;
    }
    throw new Error("no_image");
  }

  async function _readClipboardImageDataUrl() {
    const blob = await _readClipboardImageBlob();
    const dataUrl = await new Promise(function (resolve, reject) {
      const reader = new FileReader();
      reader.onload = function () {
        resolve(String(reader.result || ""));
      };
      reader.onerror = function () {
        reject(new Error("read_error"));
      };
      reader.readAsDataURL(blob);
    });
    if (!dataUrl) {
      throw new Error("read_error");
    }
    return dataUrl;
  }

  async function pasteImageToHidden(inputId, feedbackId, options) {
    const opts = options || {};
    const input = document.getElementById(inputId);
    if (!input) {
      setFeedback(feedbackId, "No se encontro el campo de imagen", 1800);
      return false;
    }

    try {
      const dataUrl = await _readClipboardImageDataUrl();
      input.value = dataUrl;
      setFeedback(feedbackId, opts.successMessage || "Imagen pegada y lista para guardar", opts.successTimeoutMs || 1600);
      return true;
    } catch (_error) {
      if (_error && _error.message === "unsupported") {
        setFeedback(feedbackId, "El navegador no soporta pegar imagen", 1800);
        return false;
      }
      if (_error && _error.message === "no_image") {
        setFeedback(feedbackId, "No se detecto imagen en el portapapeles", 1800);
        return false;
      }
      setFeedback(feedbackId, "No se pudo leer el portapapeles", 1800);
      return false;
    }
  }

  async function pasteImageAndSubmit(inputId, feedbackId, formId) {
    const form = document.getElementById(formId);
    if (!form) {
      setFeedback(feedbackId, "No se encontro el formulario de subida", 1800);
      return false;
    }

    // Fallback legacy: if fetch/FormData are unavailable, keep old submit flow.
    if (!window.fetch || !window.FormData) {
      const pasted = await pasteImageToHidden(inputId, feedbackId, {
        successMessage: "Imagen pegada. Guardando alternativa...",
        successTimeoutMs: 1200,
      });
      if (!pasted) {
        return false;
      }
      if (typeof form.requestSubmit === "function") {
        form.requestSubmit();
      } else {
        form.submit();
      }
      return true;
    }

    try {
      const blob = await _readClipboardImageBlob();
      const hiddenInput = document.getElementById(inputId);
      if (hiddenInput) {
        hiddenInput.value = "";
      }

      setFeedback(feedbackId, "Imagen pegada. Guardando alternativa...", 1200);

      const formData = new FormData(form);
      formData.delete("pasted_image_data");

      const mimeType = blob.type || "image/png";
      const extByMime = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
      };
      const fileExt = extByMime[mimeType] || "png";
      const filename = "pasted-" + String(Date.now()) + "." + fileExt;
      formData.append("image_file", blob, filename);

      const response = await fetch(form.action || window.location.href, {
        method: (form.method || "POST").toUpperCase(),
        body: formData,
        credentials: "same-origin",
      });

      if (!response.ok) {
        if (response.status === 413) {
          setFeedback(feedbackId, "La imagen supera el limite permitido", 2400);
          return false;
        }
        setFeedback(feedbackId, "No se pudo guardar la alternativa", 2400);
        return false;
      }

      window.location.assign(response.url || window.location.href);
      return true;
    } catch (_error) {
      if (_error && _error.message === "unsupported") {
        setFeedback(feedbackId, "El navegador no soporta pegar imagen", 1800);
        return false;
      }
      if (_error && _error.message === "no_image") {
        setFeedback(feedbackId, "No se detecto imagen en el portapapeles", 1800);
        return false;
      }
      setFeedback(feedbackId, "No se pudo leer el portapapeles", 1800);
      return false;
    }
  }

  window.copyTextFromElement = copyTextFromElement;
  window.copyImageFromUrl = copyImageFromUrl;
  window.pasteImageToHidden = pasteImageToHidden;
  window.pasteImageAndSubmit = pasteImageAndSubmit;
})();
