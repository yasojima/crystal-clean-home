(() => {
  const section = document.querySelector('.home-concerns');
  if (!section) return;
  const places = [...section.querySelectorAll('[data-concern-place]')];
  const groups = [...section.querySelectorAll('.home-concerns__group')];

  const selectPlace = place => {
    places.forEach(button => {
      button.setAttribute('aria-selected', String(button === place));
      button.tabIndex = button === place ? 0 : -1;
    });
    const groupId = place.getAttribute('aria-controls');
    groups.forEach(group => { group.hidden = group.id !== groupId; });
  };

  section.addEventListener('click', event => {
    const place = event.target.closest('[data-concern-place]');
    if (!place || !section.contains(place) || place.getAttribute('aria-selected') === 'true') return;
    selectPlace(place);
  });

  section.addEventListener('keydown', event => {
    const index = places.indexOf(event.target);
    if (index < 0) return;
    const targets = { ArrowRight: (index + 1) % places.length,
      ArrowLeft: (index + places.length - 1) % places.length,
      Home: 0, End: places.length - 1 };
    if (!(event.key in targets)) return;
    event.preventDefault();
    const place = places[targets[event.key]];
    selectPlace(place);
    place.focus();
  });
})();
