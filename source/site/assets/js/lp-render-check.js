/* Opt-in, local-only paint isolation for the unresolved iPhone LP artifact. */
(() => {
  const params = new URLSearchParams(location.search);
  const selected = params.get('rendercheck');
  if (!/^[0-6]$/.test(selected || '')) return;

  const mode = Number(selected);
  const version = '2026100703';
  const filterTargets = ['#cch-first-lp #first-comparison .lp-table-scroll', '#cch-first-lp .cta-final .lp-closing-logo'];
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
  if (mode === 0) style.textContent = `@media(max-width:767.98px){${filterTargets.join(',')}{filter:var(--lp-shadow-filter)!important;-webkit-filter:var(--lp-shadow-filter)!important}}`;
  if (mode === 6) style.textContent = `@media(max-width:767.98px){${filterTargets.join(',')}{filter:none!important;-webkit-filter:none!important}}`;
  if (mode === 5) style.textContent = effects.join('\n') + '\n#cch-first-lp{display:none!important}body.c-beginner-lp>main{min-height:20000px!important}';
  style.textContent += `
    #lp-render-check-panel{position:fixed!important;right:12px!important;bottom:calc(24px + env(safe-area-inset-bottom,0px))!important;width:min(340px,calc(100vw - 24px))!important;z-index:2147483647!important;padding:10px!important;color:#123a60!important;background:#fff!important;border:1px solid #005bac!important;border-radius:8px!important;box-sizing:border-box!important;font:12px/1.5 sans-serif!important;filter:none!important;transform:none!important;mask-image:none!important;clip-path:none!important}
    #lp-render-check-panel p{margin:0 0 6px!important;padding:0!important;font:inherit!important}
    #lp-render-check-panel nav{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:6px!important}
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
    panel.setAttribute('aria-label', '黒い表示の確認');
    const title = document.createElement('p');
    const name = mode === 0 ? 'A' : mode === 6 ? 'B' : String(mode);
    title.textContent = '黒い表示の確認 ' + name + ' ／ ' + version;
    const help = document.createElement('p');
    help.textContent = 'A→B→Aの順で、左上の黒い表示を確認';
    const status = document.createElement('p');
    status.id = 'lp-render-check-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    status.textContent = '適用確認中';
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', '確認表示の切り替え');
    const choices = [[0, 'A 元の表示'], [6, 'B 確認用の表示']];
    if (mode >= 1 && mode <= 5) {
      ['1 影なし', '2 切抜きなし', '3 SVGなし', '4 1〜3全部', '5 本文なし'].forEach((label, index) => choices.push([index + 1, label]));
    }
    choices.forEach(([index, label]) => {
      const link = document.createElement('a');
      const url = new URL(location.href);
      url.searchParams.set('rendercheck', String(index));
      url.searchParams.set('check', version);
      url.searchParams.delete('position');
      link.href = url.href;
      link.textContent = label;
      if (index === mode) link.setAttribute('aria-current', 'page');
      link.addEventListener('click', () => {
        // Reload the document so a stale composited layer cannot survive a toggle.
        const next = new URL(link.href);
        next.searchParams.set('position', String(Math.round(scrollY)));
        link.href = next.href;
      });
      nav.appendChild(link);
    });
    panel.append(title, help, status, nav);
    // Remove the LP nodes too: a hidden filter/mask is itself under investigation.
    if (mode === 5) document.getElementById('cch-first-lp').remove();
    document.body.appendChild(panel);

    function verifyApplied() {
      if (mode !== 0 && mode !== 6) {
        status.textContent = '追加の確認表示です。AかBを選んでください';
        status.dataset.applied = 'other-mode';
        return;
      }
      const mobile = matchMedia('(max-width:767.98px)').matches;
      const values = filterTargets.map(selector => {
        const element = document.querySelector(selector);
        if (!element) return {selector, found: false};
        const computed = getComputedStyle(element);
        return {selector, found: true, filter: computed.filter, webkitFilter: computed.webkitFilter || ''};
      });
      status.dataset.targetValues = JSON.stringify(values);
      if (!mobile) {
        status.textContent = 'PC表示：切替対象外';
        status.dataset.applied = 'desktop';
        return;
      }
      const applied = values.every(value => value.found && (mode === 6
        ? value.filter === 'none' && (!value.webkitFilter || value.webkitFilter === 'none')
        : value.filter.startsWith('drop-shadow(')));
      status.textContent = applied ? '適用OK' : '適用未確認：この状態では判定できません';
      status.dataset.applied = applied ? 'ok' : 'unconfirmed';
    }
    const verifyAfterPaint = () => requestAnimationFrame(() => requestAnimationFrame(verifyApplied));
    verifyAfterPaint();
    window.addEventListener('load', verifyAfterPaint, {once: true});
    window.addEventListener('pageshow', verifyAfterPaint);
    window.addEventListener('resize', verifyAfterPaint);
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
