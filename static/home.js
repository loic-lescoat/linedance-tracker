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

function normalize(str) {
  // strips punctuation and whitespace from string
  return str
    .toLowerCase()
    .replace(/[\s\W_]+/g, "");
}


const filterInput = document.getElementById("tableFilter");
const rows = document.querySelectorAll("tbody tr");

filterInput.addEventListener("input", () => {
  const q = normalize(filterInput.value);

  rows.forEach(row => {
    const dance  = normalize(row.dataset.dance);
    const song   = normalize(row.dataset.song);
    const artist = normalize(row.dataset.artist);

    const match =
      dance.includes(q) ||
      song.includes(q) ||
      artist.includes(q);

    row.style.display = match ? "" : "none";
  });
});
