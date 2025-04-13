// Mobile menu toggle
document.addEventListener('click', function (e) {
    if (e.target.id === 'mobile-menu-button' || e.target.closest('#mobile-menu-button')) {
      const menu = document.getElementById('mobile-menu');
      menu.classList.toggle('hidden');
    }
  });
  