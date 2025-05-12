document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("search-form");
  const loadingScreen = document.getElementById("loading-screen");
  const loadingText = document.getElementById("loading-text");

  const messages = [
    "Artisti otsimine…",
    "Andmete kogumine…",
    "Lugude analüüsimine…",
    "Akordide tuvastamine…",
    "Sobivuse hindamine…"
  ];

  form.addEventListener("submit", () => {
    loadingScreen.classList.remove("hidden");

    let i = 0;
    loadingText.textContent = messages[i];

    setInterval(() => {
      i = (i + 1) % messages.length;   // lõpmatu tsükkel teadete kuvamiseks (kuniks otsingut töödeldakse)
      loadingText.textContent = messages[i];
    }, 1500);
  });

});
