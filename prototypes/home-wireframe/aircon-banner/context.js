(() => {
  const choices = [...document.querySelectorAll('[data-ab-choice]')];
  const panels = [...document.querySelectorAll('[data-ab-panel]')];
  function select(letter, updateUrl) {
    if (!['A', 'B', 'C'].includes(letter)) letter = 'A';
    choices.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.abChoice === letter)));
    panels.forEach(panel => { panel.hidden = panel.dataset.abPanel !== letter; });
    if (updateUrl) {
      const url = new URL(location.href);
      url.searchParams.set('banner', letter);
      history.replaceState(null, '', url);
    }
  }
  choices.forEach(button => button.addEventListener('click', () => select(button.dataset.abChoice, true)));
  select(new URLSearchParams(location.search).get('banner'), false);
})();
