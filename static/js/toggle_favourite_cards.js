document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".favourite-toggle").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const songId = btn.dataset.songId;
      const img = btn.querySelector("img");

      const response = await fetch("/toggle-favourite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ song_id: songId }),
      });

      const data = await response.json();
      img.src = data.is_favourite
        ? "/static/img/fav_on.png"
        : "/static/img/fav_off.png";
    });
  });
});
