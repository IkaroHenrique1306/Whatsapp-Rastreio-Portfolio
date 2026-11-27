document.addEventListener("submit", function (event) {
  const form = event.target;
  if (form instanceof HTMLFormElement && form.hasAttribute("data-confirm")) {
    if (!window.confirm(form.getAttribute("data-confirm"))) {
      event.preventDefault();
    }
  }
});
