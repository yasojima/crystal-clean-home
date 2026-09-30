(() => {
  'use strict';

  const message = 'デモ表示のためリンク未設定です。';
  const blockedPath = /^\/(?:contact(?:\/|$)|business\/contact(?:\/|$)|campaign\/180223-01(?:\/|$)|reservation(?:\/|$)|reserve(?:\/|$)|booking(?:\/|$)|carts\/add_product_from_campaign(?:\/|$))/i;
  const blockedHost = /^(?:form\.osoujihonpo\.com|reg18\.smp\.ne\.jp)$/i;
  const submitLabel = /(?:予約|送信|申し込|申込|注文|購入|資料請求|今すぐ電話)/;

  function show(event) {
    event.preventDefault();
    event.stopImmediatePropagation();
    window.alert(message);
  }

  document.addEventListener('click', (event) => {
    const control = event.target.closest('a, button, input[type="submit"], [data-demo-dialog]');
    if (!control) return;
    if (control.hasAttribute('data-demo-dialog')) return show(event);
    if (control.matches('button, input[type="submit"]')) {
      if (control.closest('form') || submitLabel.test(control.textContent || control.value || '')) show(event);
      return;
    }
    const href = control.getAttribute('href') || '';
    if (/^(?:tel:|mailto:)/i.test(href)) return show(event);
    let url;
    try { url = new URL(href, location.href); } catch { return; }
    if (blockedHost.test(url.hostname) ||
        (url.origin === location.origin && blockedPath.test(url.pathname))) show(event);
  }, true);

  document.addEventListener('submit', (event) => show(event), true);
})();
