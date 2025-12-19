  function toggleChanged(element) {
    element.classList.remove('animate-check');
    element.classList.remove('before:animate-checkmark');
    if (element.checked) {
      element.offsetWidth;
      element.classList.add('animate-check');
      element.classList.add('before:animate-checkmark');
    }
    const url = element.dataset.actionUrl;
    fetch(url)
    .then(response => response.text())
    .catch(error => console.error("Error:", error));
  }
