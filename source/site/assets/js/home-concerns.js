(() => {
  const section = document.querySelector('.home-concerns');
  if (!section) return;
  const places = [...section.querySelectorAll('[data-concern-place]')];
  const groups = [...section.querySelectorAll('.home-concerns__group')];

  section.addEventListener('click', event => {
    const place = event.target.closest('[data-concern-place]');
    if (!place || !section.contains(place) || place.getAttribute('aria-pressed') === 'true') return;
    places.forEach(button => button.setAttribute('aria-pressed', String(button === place)));
    const groupId = place.getAttribute('aria-controls');
    groups.forEach(group => { group.hidden = group.id !== groupId; });
  });
})();
