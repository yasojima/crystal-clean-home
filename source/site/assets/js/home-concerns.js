(() => {
  const section = document.querySelector('.home-concerns');
  if (!section) return;
  const places = [...section.querySelectorAll('[data-concern-place]')];
  const groups = [...section.querySelectorAll('.home-concerns__group')];
  const results = [...section.querySelectorAll('.home-concerns__result')];

  function selectQuestion(button) {
    const group = button.closest('.home-concerns__group');
    group.querySelectorAll('[data-concern-question]').forEach(item => {
      item.setAttribute('aria-pressed', String(item === button));
    });
    const resultId = button.getAttribute('aria-controls');
    results.forEach(result => { result.hidden = result.id !== resultId; });
  }

  section.addEventListener('click', event => {
    const place = event.target.closest('[data-concern-place]');
    if (place && section.contains(place)) {
      if (place.getAttribute('aria-pressed') === 'true') return;
      places.forEach(button => button.setAttribute('aria-pressed', String(button === place)));
      const groupId = place.getAttribute('aria-controls');
      groups.forEach(group => { group.hidden = group.id !== groupId; });
      const group = groups.find(item => item.id === groupId);
      selectQuestion(group.querySelector('[data-concern-question]'));
      return;
    }
    const question = event.target.closest('[data-concern-question]');
    if (question && section.contains(question)) selectQuestion(question);
  });
})();
