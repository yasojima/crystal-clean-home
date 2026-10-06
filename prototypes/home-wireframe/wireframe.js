(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('wf-data').textContent);
  const catalogue = window.CCH_CART_CATALOGUE;
  const core = window.CCHCartCore;
  const escape = value => String(value).replace(/[&<>"']/g, char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
  const money = value => value.toLocaleString('ja-JP');
  const image = (src, alt, className = '') => `<img class="${className}" src="${escape(src)}" alt="${escape(alt)}" loading="lazy" decoding="async">`;
  const guideLinks = guide => `<a class="wf-text-link" href="${guide.link}">${guide.action}<span aria-hidden="true"> →</span></a>${guide.extraLink ? `<a class="wf-text-link" href="${guide.extraLink}">${guide.extraAction}<span aria-hidden="true"> →</span></a>` : ''}`;
  const guideCopy = guide => `<span class="wf-eyebrow">${guide.eyebrow}</span><h3>${guide.title}</h3><p>${guide.description}</p>`;
  const guidePoints = guide => `<ul class="wf-chips">${guide.points.map(point => `<li>${point}</li>`).join('')}</ul>`;
  const products = data.productKeys.map(key => ({key, ...catalogue.items[key]}));
  let lines = [];

  const choose = {
    A: () => `<div class="wf-guide-editorial">${data.guides.map((guide, index) => `<article class="wf-guide-story ${index === 0 ? 'wf-guide-story--lead' : ''}"><div class="wf-guide-art">${image(guide.image, guide.alt)}</div><div>${guideCopy(guide)}${guidePoints(guide)}${guideLinks(guide)}</div></article>`).join('')}</div>`,
    B: () => `<div class="wf-guide-chapters">${data.guides.map((guide, index) => `<article class="wf-guide-chapter"><span class="wf-chapter-number">0${index + 1}</span>${image(guide.image, guide.alt)}<div>${guideCopy(guide)}${guidePoints(guide)}</div><div class="wf-chapter-links">${guideLinks(guide)}</div></article>`).join('')}</div>`,
    C: () => `<div class="wf-guide-folds"><div class="wf-fold-intro"><p class="wf-eyebrow">迷ったら、ここから</p><h3>気になる内容だけ<br>開いて確認。</h3><p>選び方のポイントを短くまとめました。</p></div><div>${data.guides.map((guide, index) => `<details class="wf-guide-fold" ${index === 0 ? 'open' : ''}><summary><span>0${index + 1}</span>${guide.title}<span class="wf-fold-sign" aria-hidden="true"></span></summary><div class="wf-fold-content">${image(guide.image, guide.alt)}<div><p class="wf-eyebrow">${guide.eyebrow}</p><p>${guide.description}</p>${guidePoints(guide)}${guideLinks(guide)}</div></div></details>`).join('')}</div></div>`
  };

  function counter(product, variant) {
    const id = `wf-quantity-${variant}-${product.key.replace(':', '-')}`;
    return `<div class="wf-counter"><button type="button" data-wf-step="-1" data-wf-key="${product.key}" aria-label="${escape(product.name)}の数量を減らす">−</button><label class="wf-sr-only" for="${id}">${escape(product.name)}の数量</label><input id="${id}" type="number" min="0" max="99" step="1" inputmode="numeric" value="0" data-wf-quantity="${product.key}"><span>${product.unit}</span><button type="button" data-wf-step="1" data-wf-key="${product.key}" aria-label="${escape(product.name)}の数量を増やす">＋</button></div>`;
  }
  function productCopy(product) {
    return `<h3>${escape(product.name)}</h3><p class="wf-unit-price"><span class="wf-unit-label">１${product.unit}の場合</span><span class="wf-money"><b>${money(product.tiers[0].price)}</b>円（税込）</span></p>`;
  }
  function total(className = '') {
    return `<div class="wf-budget-result ${className}"><div><p>選んだ内容の目安（税込）</p><strong aria-live="polite" aria-atomic="true"><span data-wf-total>0</span><small>円</small></strong><p class="wf-budget-count"><span data-wf-count>0</span>点を選択 <span data-wf-discount></span></p></div><a class="wf-primary" href="/quick_cart/">すべてのメニューで見積もる <span aria-hidden="true">→</span></a></div>`;
  }
  const estimateNote = `<p class="wf-small-note">ここでは代表３メニューを試算できます。すべてのメニュー・機種別の料金・オプションは、見積もりシミュレーションで選べます。</p><p class="wf-review wf-small-note">この比較画面の選択は保存されません。次の画面ではメニューを改めて選択します。</p>`;
  const budget = {
    A: () => `<div class="wf-budget-tiles">${products.map(product => `<article class="wf-budget-tile">${image(product.image, product.name)}${productCopy(product)}${counter(product, 'A')}</article>`).join('')}</div>${total('wf-total-band')}${estimateNote}`,
    B: () => `<div class="wf-budget-ledger"><div class="wf-budget-rows">${products.map(product => `<article class="wf-budget-row">${image(product.image, product.name)}<div>${productCopy(product)}</div>${counter(product, 'B')}</article>`).join('')}</div><aside class="wf-receipt" aria-label="試算の明細"><p class="wf-eyebrow">今回の試算</p><ul data-wf-receipt><li>メニューを選ぶと明細が表示されます。</li></ul>${total()}</aside></div>${estimateNote}`,
    C: () => `<div class="wf-budget-disclosure"><div><p class="wf-eyebrow">STEP 1 · 必要な数量を選ぶ</p>${products.map((product, index) => `<details class="wf-budget-fold" ${index === 0 ? 'open' : ''}><summary>${escape(product.name)}<span class="wf-fold-sign" aria-hidden="true"></span></summary><div>${image(product.image, product.name)}<div>${productCopy(product)}${counter(product, 'C')}</div></div></details>`).join('')}</div><div class="wf-result-poster"><p class="wf-eyebrow">STEP 2 · 予算と見比べる</p><h3>数量を変えると、<br>目安もすぐに変わります。</h3>${total()}</div></div>${estimateNote}`
  };

  function stepCopy(step, index) {
    return `<span class="wf-step-index">0${index + 1}</span><h3>${step.title}</h3><p>${step.text}</p><span class="wf-step-note">${step.note}</span>${step.link ? `<a class="wf-text-link" href="${step.link}">${step.action} →</a>` : ''}`;
  }
  const flowCTA = `<div class="wf-flow-cta"><p>まずは、気になるお掃除を選んでみませんか。</p><a class="wf-primary" href="/quick_cart/">見積もりシミュレーションへ <span aria-hidden="true">→</span></a></div>`;
  const flow = {
    A: () => `<ol class="wf-flow-track">${data.steps.map((step, index) => `<li>${stepCopy(step, index)}</li>`).join('')}</ol>${flowCTA}`,
    B: () => `<ol class="wf-flow-timeline">${data.steps.map((step, index) => `<li><div>${stepCopy(step, index)}</div></li>`).join('')}</ol>${flowCTA}`,
    C: () => `<div class="wf-flow-handoff"><div class="wf-flow-side"><p class="wf-eyebrow">お客様の操作</p><h3>選んで、確認して、送信。</h3><ol>${data.steps.slice(0, 3).map((step, index) => `<li>${stepCopy(step, index)}</li>`).join('')}</ol></div><div class="wf-flow-visit"><p class="wf-eyebrow">スタッフと確認</p>${image('/assets/images/cleaning-illustrations/pack.png', 'スタッフが訪問する住まい')}<div>${stepCopy(data.steps[3], 3)}</div></div></div>${flowCTA}`
  };

  for (const [key, variants] of Object.entries({choose, budget, flow})) {
    document.querySelector(`[data-wf-panels="${key}"]`).innerHTML = Object.entries(variants).map(([letter, render]) => `<div class="wf-panel" id="wf-${key}-${letter}" data-wf-panel="${letter}" ${letter !== 'A' ? 'hidden' : ''}>${render()}</div>`).join('');
  }

  function updateEstimate() {
    const summary = core.calculate(lines, catalogue);
    document.querySelectorAll('[data-wf-total]').forEach(node => { node.textContent = money(summary.total); });
    document.querySelectorAll('[data-wf-count]').forEach(node => { node.textContent = summary.count; });
    document.querySelectorAll('[data-wf-discount]').forEach(node => { node.textContent = summary.discount ? `複数台割引 −${money(summary.discount)}円` : ''; });
    document.querySelectorAll('[data-wf-quantity]').forEach(input => { input.value = lines.find(line => line.key === input.dataset.wfQuantity)?.quantity || 0; });
    const receipt = document.querySelector('[data-wf-receipt]');
    receipt.innerHTML = summary.details.length ? summary.details.map(detail => `<li><span>${escape(detail.item.name)} × ${detail.quantity}</span><b>${money(detail.amount)}円</b></li>`).join('') : '<li>メニューを選ぶと明細が表示されます。</li>';
  }

  function select(section, letter, persist = true) {
    section.querySelectorAll('[data-wf-panel]').forEach(panel => { panel.hidden = panel.dataset.wfPanel !== letter; });
    section.querySelectorAll('[data-wf-choice]').forEach(button => { button.setAttribute('aria-pressed', String(button.dataset.wfChoice === letter)); });
    if (persist) {
      const url = new URL(location.href);
      url.searchParams.set(section.dataset.wfSection, letter);
      history.replaceState(null, '', url);
    }
  }
  const params = new URLSearchParams(location.search);
  document.querySelectorAll('[data-wf-section]').forEach(section => {
    const letter = params.get(section.dataset.wfSection) || params.get('preset') || 'A';
    select(section, ['A', 'B', 'C'].includes(letter) ? letter : 'A', false);
  });
  document.addEventListener('click', event => {
    const choice = event.target.closest('[data-wf-choice]');
    if (choice) select(choice.closest('[data-wf-section]'), choice.dataset.wfChoice);
    const preset = event.target.closest('[data-wf-preset]');
    if (preset) document.querySelectorAll('[data-wf-section]').forEach(section => select(section, preset.dataset.wfPreset));
    const step = event.target.closest('[data-wf-step]');
    if (step) {
      const current = lines.find(line => line.key === step.dataset.wfKey)?.quantity || 0;
      lines = core.change(lines, step.dataset.wfKey, Math.max(0, Math.min(99, current + Number(step.dataset.wfStep))), catalogue);
      updateEstimate();
    }
    if (event.target.closest('[data-wf-clean]')) {
      document.body.classList.add('wf-clean-view');
      document.querySelector('[data-wf-return]').hidden = false;
    }
    if (event.target.closest('[data-wf-return]')) {
      document.body.classList.remove('wf-clean-view');
      document.querySelector('[data-wf-return]').hidden = true;
    }
    const floating = event.target.closest('[data-wf-floating]');
    if (floating) {
      const hidden = document.body.classList.toggle('wf-hide-floating');
      floating.textContent = hidden ? '固定見積もりを表示' : '固定見積もりを隠す';
      floating.setAttribute('aria-pressed', String(!hidden));
    }
  });
  function editQuantity(event) {
    if (!event.target.matches('[data-wf-quantity]')) return;
    const value = Number(event.target.value);
    lines = core.change(lines, event.target.dataset.wfQuantity, Number.isInteger(value) ? Math.max(0, Math.min(99, value)) : 0, catalogue);
    updateEstimate();
  }
  document.addEventListener('input', editQuantity);
  document.addEventListener('change', editQuantity);
  updateEstimate();
})();
