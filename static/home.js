  function toggleChanged(element) {
    const url = element.dataset.actionUrl;
    fetch(url)
    .then(response => response.text())
    .then(data => console.log("Response length:", data.length))
    .catch(error => console.error("Error:", error));
  }
