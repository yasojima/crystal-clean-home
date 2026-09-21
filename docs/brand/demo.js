(() => {
  'use strict';
  const messages = {
    phone: 'この電話番号はデモ用のサンプルです。実際の発信は行われません。',
    line: 'デモサイトのため、LINEの友だち追加・予約はご利用いただけません。外部のLINEアカウントには接続しません。',
    email: 'デモサイトのため、メールの送信先は設定されていません。メールアプリは起動せず、送信も行われません。',
    external: 'デモサイトのため、このリンクの接続先は設定されていません。外部サイトへの移動は行われません。',
    address: 'デモサイトのため、外部サービスによる住所検索は行いません。動作確認には架空の住所をご入力ください。',
    complete: 'デモの操作が完了しました。実際の送信・予約は行われていません。入力内容が店舗へ届くことはなく、店舗からの返信もありません。',
    form: '送信前の確認画面のサンプルです。このデモでは、入力内容を店舗へ送信しません。動作だけを確認できます。'
  };
  let modal;
  let previousFocus;
  function show(kind) {
    if (!modal) {
      modal = document.createElement('dialog');
      modal.className = 'demo-dialog';
      modal.setAttribute('aria-labelledby', 'demo-title');
      modal.setAttribute('aria-describedby', 'demo-message');
      modal.innerHTML = '<h2 id="demo-title">デモサイトのご案内</h2><p id="demo-message"></p><div class="demo-actions"><button type="button" data-demo-finish>送信を試す（デモ）</button><button type="button" data-demo-close>閉じる</button></div>';
      document.body.append(modal);
      modal.querySelector('[data-demo-close]').addEventListener('click', () => modal.close());
      modal.querySelector('[data-demo-finish]').addEventListener('click', () => show('complete'));
      modal.addEventListener('close', () => previousFocus?.focus());
      modal.addEventListener('click', e => { if (e.target === modal && (e.clientX < modal.getBoundingClientRect().left || e.clientX > modal.getBoundingClientRect().right || e.clientY < modal.getBoundingClientRect().top || e.clientY > modal.getBoundingClientRect().bottom)) modal.close(); });
    }
    modal.querySelector('#demo-message').textContent = messages[kind] || messages.external;
    modal.querySelector('[data-demo-finish]').hidden = kind !== 'form';
    if (!modal.open) { previousFocus = document.activeElement; modal.showModal(); }
    modal.querySelector(kind === 'form' ? '[data-demo-finish]' : '[data-demo-close]').focus();
  }
  function action(element) {
    if (element.dataset.demoAction) return element.dataset.demoAction;
    const href = (element.getAttribute('href') || '').trim();
    if (/^(tel|sms|fax):/i.test(href)) return 'phone';
    if (/^mailto:/i.test(href)) return 'email';
    if (/^https?:|^\/\//i.test(href)) return /lin\.ee|line\.me/.test(href) ? 'line' : 'external';
    if (element.hasAttribute('data-youtube-url')) return 'external';
    return null;
  }
  document.addEventListener('click', event => {
    const element = event.target.closest('a,area,[data-demo-action],[data-youtube-url]');
    const kind = element && action(element);
    if (!kind) return;
    event.preventDefault(); event.stopImmediatePropagation(); show(kind);
  }, true);
  document.addEventListener('keydown', event => {
    if ((event.key === 'Enter' || event.key === ' ') && event.target.matches('[data-demo-action]')) {
      event.preventDefault(); event.stopImmediatePropagation(); show(event.target.dataset.demoAction);
    }
  }, true);
  function demoSubmit(form) { if (form.id !== 'mitsumoriForm') show('form'); }
  document.addEventListener('submit', event => {
    event.preventDefault(); event.stopImmediatePropagation(); demoSubmit(event.target);
  }, true);
  HTMLFormElement.prototype.submit = function () { demoSubmit(this); };
  HTMLFormElement.prototype.requestSubmit = function () { if (this.reportValidity()) demoSubmit(this); };
})();
