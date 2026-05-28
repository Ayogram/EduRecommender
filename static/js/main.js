/* ── EduRecommender – JavaScript ───────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMobileNav();
  initFlashDismiss();
});

/* ── Theme Toggle ──────────────────────────────────────────── */
function initTheme() {
  document.documentElement.setAttribute('data-theme', 'light');
  localStorage.setItem('edu-theme', 'light');

  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('edu-theme', 'light');
    });
  });
}

/* ── Mobile Navigation ─────────────────────────────────────── */
function initMobileNav() {
  const toggle = document.querySelector('.mobile-toggle');
  const sidebar = document.querySelector('.sidebar');

  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') &&
          !sidebar.contains(e.target) &&
          !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }
}

/* ── Flash Message Auto-Dismiss ────────────────────────────── */
function initFlashDismiss() {
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-10px)';
      setTimeout(() => flash.remove(), 300);
    }, 5000);
  });
}

/* ── Confirm Actions ───────────────────────────────────────── */
function confirmAction(message) {
  return confirm(message);
}
