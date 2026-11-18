const toggle = document.querySelector('.menu-toggle');
const header = document.querySelector('.site-header');
const mobile = window.matchMedia('(max-width: 800px)');

function showMenu(open) {
  toggle.setAttribute('aria-expanded', String(open));
  header.classList.toggle('menu-open', open);
}

header.classList.add('has-toggle');
toggle.addEventListener('click', () => showMenu(toggle.getAttribute('aria-expanded') !== 'true'));
mobile.addEventListener('change', () => showMenu(false));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && header.classList.contains('menu-open')) {
    showMenu(false);
    toggle.focus();
  }
});
