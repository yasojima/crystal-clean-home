import {
  ensureGoogleTranslate,
  mountGoogleTranslateWidgets,
  selectTranslationTarget,
  storedTranslationLanguage,
} from './shared-translation.js';

const toggles = [...document.querySelectorAll('.c-footer-sns .translate-toggle')];

function setOpen(button, open) {
  for (const candidate of toggles) {
    const control = candidate.closest('.translate-control');
    const menu = control?.querySelector('.translate-menu');
    const active = candidate === button && open;
    candidate.setAttribute('aria-expanded', String(active));
    control?.classList.toggle('is-open', active);
    if (menu instanceof HTMLElement) {
      menu.setAttribute('aria-hidden', String(!active));
      menu.inert = !active;
    }
  }
}

function targetFor(button) {
  return button.closest('.translate-control')?.querySelector('[data-google-translate]')?.id;
}

for (const button of toggles) {
  button.addEventListener('click', (event) => {
    event.stopPropagation();
    const willOpen = button.getAttribute('aria-expanded') !== 'true';
    setOpen(button, willOpen);
    if (willOpen) {
      selectTranslationTarget(targetFor(button));
      ensureGoogleTranslate();
      mountGoogleTranslateWidgets();
    }
  });
}

document.addEventListener('click', (event) => {
  if (event.target instanceof Element && event.target.closest('.translate-control')) return;
  const openButton = toggles.find(button => button.getAttribute('aria-expanded') === 'true');
  setOpen(null, false);
  if (openButton?.contains(document.activeElement)) openButton.focus();
});

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  const openButton = toggles.find(button => button.getAttribute('aria-expanded') === 'true');
  if (!openButton) return;
  setOpen(null, false);
  openButton.focus();
});

if (storedTranslationLanguage()) {
  const visible = toggles.find(button => button.getClientRects().length) || toggles[0];
  if (visible) {
    selectTranslationTarget(targetFor(visible));
    ensureGoogleTranslate();
  }
}
