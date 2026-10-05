(() => {
  'use strict';
  const cart = window.CCHCart;
  if (!cart) return;
  const form = document.getElementById('cch-estimate-form');
  const review = document.querySelector('[data-estimate-confirm]');
  const key = 'cch-estimate-draft-v1';
  const escape = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const money = value => value.toLocaleString('ja-JP') + '円';
  let draft;
  try { draft = JSON.parse(sessionStorage.getItem(key) || 'null'); } catch { draft = null; }

  function summary() {
    const result = cart.getSummary();
    return `<h2 class="c-bullet-heading">ご希望のサービス</h2><ul class="cch-estimate-items">${result.details.map(line => `<li><span>${escape(line.item.name)} × ${line.quantity}</span><strong>${line.amount === null ? '別途見積り' : money(line.amount)}</strong></li>`).join('')}</ul>
      <p class="cch-estimate-total">合計金額（税込） <strong>${money(result.total)}${result.approximate ? '〜' : ''}</strong></p>${result.quoteCount ? '<p>別途見積りの商品は合計に含まれていません。</p>' : ''}`;
  }
  function guard() {
    if (cart.getSummary().count) return true;
    const main = document.querySelector('.cch-estimate');
    main.innerHTML = '<h1 class="c-page-heading">お見積り</h1><div class="cch-cart-content"><p class="cch-cart-empty">カートが空です。ご希望のサービスをお選びください。</p><a class="c-button" href="/quick_cart/">サービスを選ぶ</a></div>';
    return false;
  }
  function toggleAddress() {
    const enabled = form.elements['separate-address'].checked;
    const section = form.querySelector('.service-address__contents');
    section.hidden = !enabled;
    section.style.display = enabled ? 'block' : 'none';
    section.querySelectorAll('input,select').forEach(input => { input.disabled = !enabled; });
  }
  if (form && guard()) {
    form.querySelector('[type="submit"]').disabled = false;
    for (const input of form.querySelectorAll('input[name],select[name]')) {
      if (draft?.fields && Object.hasOwn(draft.fields, input.name)) {
        if (input.type === 'checkbox') input.checked = draft.fields[input.name] === 'on';
        else input.value = draft.fields[input.name];
      }
    }
    toggleAddress();
    form.elements['separate-address'].addEventListener('change', toggleAddress);
    form.addEventListener('submit', event => {
      event.preventDefault();
      if (!guard() || !form.reportValidity()) return;
      const fields = Object.fromEntries(new FormData(form));
      const display = {};
      form.querySelectorAll('select[name]').forEach(select => { display[select.name] = select.selectedOptions[0].textContent.trim(); });
      try { sessionStorage.setItem(key, JSON.stringify({version:1, fields, display})); }
      catch { form.querySelector('.c-form-announce__text').textContent = '入力内容を保持できませんでした。ブラウザの保存設定をご確認ください。'; return; }
      location.assign('/cart/estimate/confirm/');
    });
  }
  function renderReview() {
    if (!review || !guard()) return;
    if (!draft?.fields || draft.version !== 1) {
      review.innerHTML = '<p>お客様情報をご入力ください。</p><a class="c-button" href="/cart/estimate/">情報入力に進む</a>';
      return;
    }
    const f = draft.fields;
    const address = prefix => `〒${f[prefix+'postal-code_01'] || ''}-${f[prefix+'postal-code_02'] || ''} ${draft.display?.[prefix+'address_01'] || ''} ${f[prefix+'address_02'] || ''} ${f[prefix+'address_03'] || ''} ${f[prefix+'address_04'] || ''}`;
    const details = [
      ['お名前', `${f['last-name'] || ''} ${f['first-name'] || ''}`],
      ['フリガナ', `${f['last-name_kana'] || ''} ${f['first-name_kana'] || ''}`],
      ['Eメールアドレス', f.email || ''],
      ['電話番号', [f.tel_01,f.tel_02,f.tel_03].join('-')],
      ['ご住所', address('')],
      ['サービスご提供先', f['separate-address'] === 'on' ? address('service_') : '上記のご住所と同じ'],
    ];
    review.innerHTML = `${summary()}<h2 class="c-bullet-heading">お客様情報</h2><dl class="cch-estimate-review">${details.map(([label, value]) => `<div><dt>${label}</dt><dd>${escape(value)}</dd></div>`).join('')}</dl>
      <p class="cch-estimate-notice">確認用画面のため、お申し込みは送信されません。</p><div class="action-buttons"><button class="c-button c-button--fill-red c-button--large" type="button" disabled>見積もりを申し込む</button><a class="c-button c-button--large" href="/cart/estimate/">入力内容を修正する</a><a class="c-button" href="/cart/">カートを修正する</a></div>`;
  }
  renderReview();
  window.addEventListener('cch:cart-updated', renderReview);
  window.addEventListener('pageshow', renderReview);
})();
