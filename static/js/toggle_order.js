document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.getElementById('toggle-ordering');
  const songCards = document.querySelector('.song-cards');
  const arrow = document.getElementById('arrow');

  if (toggleBtn && songCards) {
    toggleBtn.addEventListener('click', () => {
      songCards.classList.toggle('reversed');
      arrow.textContent = songCards.classList.contains('reversed') ? '↑' : '↓';
    });
  }
});
