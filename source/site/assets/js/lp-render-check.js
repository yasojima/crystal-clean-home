/* Opt-in, local-only paint isolation for the unresolved iPhone LP artifact. */
(() => {
  const params = new URLSearchParams(location.search);
  const selected = params.get('rendercheck');
  if (!/^[0-5]$/.test(selected || '')) return;

  const mode = Number(selected);
  const scope = '#cch-first-lp, #cch-first-lp *, #cch-first-lp *::before, #cch-first-lp *::after';
  const effects = [
    `${scope}{filter:none!important;-webkit-filter:none!important;box-shadow:none!important;text-shadow:none!important}`,
    `${scope}{mask-image:none!important;-webkit-mask-image:none!important;clip-path:none!important;-webkit-clip-path:none!important}
     #cch-first-lp .lp-sr{visibility:hidden!important}`,
    `#cch-first-lp svg,#cch-first-lp img[src*=".svg"]{visibility:hidden!important}
     #cch-first-lp .c-icon{background-image:none!important;mask-image:none!important;-webkit-mask-image:none!important}
     #cch-first-lp .icv__arrow-wrapper::before,#cch-first-lp .c-voice-card::before,#cch-first-lp .c-voice-card::after{display:none!important}`
  ];
  const style = document.createElement('style');
  style.id = 'lp-render-check-style';
  if (mode >= 1 && mode <= 3) style.textContent = effects[mode - 1];
  if (mode === 4) style.textContent = effects.join('\n');
  if (mode === 5) style.textContent = effects.join('\n') + '\n#cch-first-lp{display:none!important}body.c-beginner-lp>main{min-height:20000px!important}';
  style.textContent += `
    #lp-render-check-panel{position:fixed!important;right:12px!important;bottom:calc(24px + env(safe-area-inset-bottom,0px))!important;width:min(340px,calc(100vw - 24px))!important;z-index:2147483647!important;padding:10px!important;color:#123a60!important;background:#fff!important;border:1px solid #005bac!important;border-radius:8px!important;box-sizing:border-box!important;font:12px/1.5 sans-serif!important;filter:none!important;transform:none!important;mask-image:none!important;clip-path:none!important}
    #lp-render-check-panel p{margin:0 0 6px!important;padding:0!important;font:inherit!important}
    #lp-render-check-panel nav{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:6px!important}
    #lp-render-check-panel a{display:flex!important;align-items:center!important;justify-content:center!important;min-height:32px!important;padding:3px!important;border:1px solid #005bac!important;border-radius:4px!important;color:#005bac!important;background:#fff!important;font:inherit!important;text-decoration:none!important;white-space:nowrap!important}
    #lp-render-check-panel a[aria-current="page"]{color:#fff!important;background:#005bac!important}
  `;
  // This script runs in <head>, before LP elements can paint for the first time.
  document.head.appendChild(style);
  document.documentElement.dataset.lpRenderCheck = selected;

  function mount() {
    if (!document.getElementById('cch-first-lp')) return;
    const panel = document.createElement('aside');
    panel.id = 'lp-render-check-panel';
    panel.setAttribute('aria-label', 'LPの表示確認');
    const title = document.createElement('p');
    title.textContent = 'LP表示確認 2026100701 ／ 現在 ' + selected;
    const help = document.createElement('p');
    help.textContent = '切替後、少し下へスクロールして左上を確認';
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', '描画処理の切り替え');
    const labels = ['0 通常', '1 影なし', '2 切抜きなし', '3 SVGなし', '4 1〜3全部', '5 本文なし'];
    labels.forEach((label, index) => {
      const link = document.createElement('a');
      const url = new URL(location.href);
      url.searchParams.set('rendercheck', String(index));
      url.searchParams.delete('position');
      link.href = url.href;
      link.textContent = label;
      if (index === mode) link.setAttribute('aria-current', 'page');
      link.addEventListener('click', () => {
        // A fresh document prevents a stale composited layer from surviving a toggle.
        const next = new URL(link.href);
        next.searchParams.set('position', String(Math.round(scrollY)));
        link.href = next.href;
      });
      nav.appendChild(link);
    });
    panel.append(title, help, nav);
    // Remove the LP nodes as well: a hidden filter/mask is itself under investigation.
    if (mode === 5) document.getElementById('cch-first-lp').remove();
    document.body.appendChild(panel);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once: true});
  else mount();

  const position = Number(params.get('position'));
  if (Number.isFinite(position) && position > 0) {
    window.addEventListener('load', () => requestAnimationFrame(() => {
      window.scrollTo({top: Math.min(position, document.documentElement.scrollHeight - innerHeight), behavior: 'instant'});
    }), {once: true});
  }
})();
