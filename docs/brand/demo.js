(() => {
  'use strict';
  const messages = {
    phone: 'こちらはデモサイトです。\n実際の電話発信は行われません。',
    line: 'こちらはデモサイトです。\n実際のご予約・LINEへの接続は行っていません。',
    email: 'こちらはデモサイトです。\n実際のメール送信は行われません。',
    external: 'こちらはデモサイトです。\n外部サイトへの接続は行っていません。',
    address: 'こちらはデモサイトです。\n実際の住所検索は行われません。',
    complete: 'こちらはデモサイトです。\n実際のお問い合わせ・お見積もりは送信されません。',
    form: '入力内容をご確認のうえ、「送信する」を押してください。'
  };
  const titles = {phone:'お電話について',line:'ご予約について',email:'メールについて',external:'リンクについて',address:'住所検索について',complete:'お問い合わせについて',form:'入力内容の確認'};
  let modal;
  let previousFocus;
  function show(kind) {
    if (!modal) {
      modal = document.createElement('dialog');
      modal.className = 'demo-dialog';
      modal.setAttribute('aria-labelledby', 'demo-title');
      modal.setAttribute('aria-describedby', 'demo-message');
      modal.innerHTML = '<span class="demo-eyebrow">INFORMATION</span><h2 id="demo-title"></h2><p id="demo-message"></p><dl class="demo-confirm-fields" hidden></dl><div class="demo-actions"><button type="button" data-demo-finish>送信する</button><button type="button" data-demo-close>閉じる</button></div>';
      document.body.append(modal);
      modal.querySelector('[data-demo-close]').addEventListener('click', () => modal.close());
      modal.querySelector('[data-demo-finish]').addEventListener('click', () => show('complete'));
      modal.addEventListener('close', () => previousFocus?.focus());
      modal.addEventListener('click', e => { if (e.target === modal && (e.clientX < modal.getBoundingClientRect().left || e.clientX > modal.getBoundingClientRect().right || e.clientY < modal.getBoundingClientRect().top || e.clientY > modal.getBoundingClientRect().bottom)) modal.close(); });
    }
    modal.querySelector('#demo-message').textContent = messages[kind] || messages.external;
    modal.querySelector('#demo-title').textContent = titles[kind] || titles.external;
    modal.querySelector('[data-demo-finish]').hidden = kind !== 'form';
    modal.querySelector('[data-demo-close]').textContent = kind === 'form' ? '入力内容を修正' : '閉じる';
    modal.querySelector('.demo-confirm-fields').hidden = kind !== 'form';
    if (kind !== 'form') modal.querySelector('.demo-confirm-fields').replaceChildren();
    if (!modal.open) { previousFocus = document.activeElement; modal.showModal(); }
    modal.querySelector(kind === 'form' ? '[data-demo-finish]' : '[data-demo-close]').focus();
  }
  function action(element) {
    if (element.dataset.demoAction) return element.dataset.demoAction;
    if (element.matches('.cart-button')) return 'complete';
    const href = (element.getAttribute('href') || element.getAttribute('data-url') || '').trim();
    if (/^(tel|sms|fax):/i.test(href)) return 'phone';
    if (/^mailto:/i.test(href)) return 'email';
    if (/^https?:|^\/\//i.test(href)) return /lin\.ee|line\.me/.test(href) ? 'line' : 'external';
    if (element.hasAttribute('data-youtube-url') || element.hasAttribute('data-youtubeurl')) return 'external';
    return null;
  }
  document.addEventListener('click', event => {
    const element = event.target.closest('a,area,[data-demo-action],[data-youtube-url],[data-youtubeurl],[data-url],.cart-button');
    const kind = element && action(element);
    if (!kind) return;
    event.preventDefault(); event.stopImmediatePropagation(); show(kind);
  }, true);
  document.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('[data-demo-action]')) {
      event.preventDefault(); event.stopImmediatePropagation(); show(event.target.dataset.demoAction);
    }
  }, true);
  function demoSubmit(form) {
    if (form.id === 'mitsumoriForm') return;
    if (form.id === 'mitsumoriSendForm') { show('complete'); return; }
    show('form');
    const fields = modal.querySelector('.demo-confirm-fields');
    fields.replaceChildren();
    for (const field of form.elements) {
      if (!field.name || !field.value || ['hidden','submit','button'].includes(field.type)) continue;
      if (['radio','checkbox'].includes(field.type) && !field.checked) continue;
      const name = document.createElement('dt');
      name.textContent = field.closest('tr')?.querySelector('th')?.textContent.trim() || field.name;
      const value = document.createElement('dd');
      value.textContent = field.value;
      fields.append(name, value);
    }
  }
  document.addEventListener('submit', event => {
    event.preventDefault(); event.stopImmediatePropagation(); demoSubmit(event.target);
  }, true);
  HTMLFormElement.prototype.submit = function () { demoSubmit(this); };
  HTMLFormElement.prototype.requestSubmit = function () { if (this.reportValidity()) demoSubmit(this); };
})();
