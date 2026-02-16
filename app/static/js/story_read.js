(function () {
  function onAfterSwap(event) {
    const target = event.target;
    if (!target || !(target instanceof HTMLElement)) return;
    if (target.id === "story-shell") {
      const top = target.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top, behavior: "smooth" });
    }
  }

  document.body.addEventListener("htmx:afterSwap", onAfterSwap);
})();

