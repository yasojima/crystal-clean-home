(() => {
  'use strict';
  const catalogue = window.CCH_CART_CATALOGUE;
  const core = window.CCHCartCore;
  if (!catalogue || !core) return;
  const STORAGE_KEY = 'cch-cart-v1';
  const format = value => value.toLocaleString('ja-JP');
  const escape = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const route = location.pathname.replace(/index\.html$/, '').replace(/\/?$/, '/');
  const quick = route.startsWith('/quick_cart/') && route !== '/quick_cart/option/';
  const bindings = new Map();
  const cards = [...document.querySelectorAll('.js-product-card')];
  for (const binding of catalogue.pages[route] || []) {
    const card = cards[binding.index];
    if (card) {
      bindings.set(card, binding.keys);
      card.dataset.cartKeys = JSON.stringify(binding.keys);
    }
  }
  let lines = [];
  let storageWarning = '';
  let triggerBeforeDialog;

  function load() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return [];
    const parsed = JSON.parse(saved);
    if (parsed.version !== 1) throw new Error('保存済みカートの形式を確認できません。');
    return core.removeOrphans(core.normalize(parsed.lines, catalogue), catalogue);
  }

  function read() {
    try { lines = load(); }
    catch { lines = []; storageWarning = '保存済みカートを読み込めませんでした。商品を選び直してください。'; }
    return lines;
  }

  function commit(next) {
    core.calculate(next, catalogue);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify({version: 1, lines: next})); }
    catch { throw new Error('カートを保存できませんでした。ブラウザの保存設定をご確認ください。'); }
    lines = next;
    refresh();
  }

  function update(key, count, additive = false) {
    commit(core.change(read(), key, count, catalogue, additive));
  }

  function keyFor(card) {
    const keys = bindings.get(card);
    return keys?.[card.querySelector('.js-room-types')?.selectedIndex || 0];
  }

  function countFor(card) {
    const index = card.querySelector('.js-room-types')?.selectedIndex || 0;
    const selects = card.querySelectorAll('.js-product-quantity select');
    const counters = card.querySelectorAll('.c-counter__input');
    return core.quantity(selects[index]?.value ?? counters[index]?.value ?? 1);
  }

  function priceLabel(item) {
    if (item.quote) return '別途見積り';
    return `${format(item.tiers[0].price)}円${item.approximate ? '〜' : ''}（税込）／${escape(item.unit)}`;
  }

  function totalLabel(result) {
    if (!result.total && result.quoteCount) return '別途見積り';
    return format(result.total) + (result.approximate ? '〜' : '');
  }

  function closeDialog() {
    const dialog = document.getElementById('cch-cart-dialog');
    if (dialog?.open) dialog.close();
  }

  function show(message, success = false) {
    let dialog = document.getElementById('cch-cart-dialog');
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.id = 'cch-cart-dialog';
      dialog.className = 'cch-cart-dialog';
      dialog.setAttribute('aria-labelledby', 'cch-cart-dialog-title');
      dialog.addEventListener('click', event => {
        if (event.target === dialog || event.target.closest('[data-cart-close]')) closeDialog();
      });
      dialog.addEventListener('close', () => triggerBeforeDialog?.focus({preventScroll: true}));
      document.body.append(dialog);
    }
    triggerBeforeDialog = document.activeElement;
    const result = core.calculate(lines, catalogue);
    dialog.innerHTML = `<h2 id="cch-cart-dialog-title">${success ? 'カートに追加しました' : 'ご確認ください'}</h2>
      <p>${escape(message)}</p>${success ? `<p class="cch-cart-dialog__total">合計金額（税込）：${totalLabel(result)}円</p>
      <a class="c-button c-button--fill-red" href="/cart/">カートを確認する</a>` : ''}
      <button type="button" class="cch-cart-close" data-cart-close>閉じる</button>`;
    if (!dialog.open) dialog.showModal();
  }

  function quantityInput(line, removable = true) {
    return `<label class="cch-cart-quantity">数量<input type="number" min="${removable ? 0 : 1}" max="${core.MAX_QUANTITY}" step="1"
      inputmode="numeric" value="${line.quantity}" data-cart-set="${escape(line.key)}" aria-label="${escape(catalogue.items[line.key].name)}の数量"></label>`;
  }

  function lineMarkup(line) {
    const parent = catalogue.items[line.item.parentKey];
    return `<li class="cch-cart-line cart-contents__item" data-cart-line="${escape(line.key)}"><div class="product-card__main cch-cart-line__main">
      ${line.item.image ? `<img class="cch-cart-line__image" src="${escape(line.item.image)}" alt="" loading="lazy" width="176" height="132">` : ''}<div class="cch-cart-line__description">
      ${parent ? `<p class="cch-cart-parent">${escape(parent.name)}のオプション</p>` : ''}
      <h3>${escape(line.item.name)}</h3><p>${line.unitPrice === null ? '別途見積り' : `${format(line.unitPrice)}円${line.item.approximate ? '〜' : ''}（税込）／${escape(line.item.unit)}`}</p>
      ${line.discount ? `<p class="cch-cart-discount">数量割引適用：−${format(line.discount)}円</p>` : ''}</div>
      </div><div class="product-card__footer cch-cart-line__footer">${quantityInput(line)}<p class="cch-cart-line__amount" data-cart-line-amount>${line.amount === null ? '別途見積り' : format(line.amount) + '円' + (line.item.approximate ? '〜' : '')}</p>
      <button type="button" class="cch-cart-remove" data-cart-remove="${escape(line.key)}" aria-label="${escape(line.item.name)}を削除">削除</button></div></li>`;
  }

  function summaryMarkup(result) {
    return `<dl class="cch-cart-summary"><div><dt>税抜金額</dt><dd>${format(result.subtotal)}円</dd></div>
      <div><dt>消費税（${catalogue.taxRate}%）</dt><dd>${format(result.tax)}円</dd></div>
      <div class="cch-cart-summary__total"><dt>合計金額（税込）</dt><dd data-cart-total>${totalLabel(result)}円</dd></div></dl>
      ${result.approximate ? '<p class="cch-cart-note">「〜」の付いたサービスは表示料金をもとにした概算です。</p>' : ''}
      ${result.quoteCount ? '<p class="cch-cart-note">別途見積りの商品は上記の合計金額に含まれていません。</p>' : ''}`;
  }

  function renderCart(result) {
    const mount = document.querySelector('[data-cart-content]');
    if (!mount) return;
    if (!result.details.length) {
      mount.innerHTML = '<p class="cch-cart-empty">カートが空です。<br>ご希望のサービスをお選びください。</p><a class="c-button" href="/quick_cart/">サービスを選ぶ</a>';
      return;
    }
    mount.innerHTML = `<div class="cart"><div class="cart__contents"><ul class="cch-cart-lines">${result.details.map(lineMarkup).join('')}</ul>
      <div class="cch-cart-actions"><a class="c-button" href="/quick_cart/">サービスを追加する</a><a class="c-button c-button--fill-blue" href="/quick_cart/option/">オプションを選ぶ</a></div></div>
      <aside class="cart__price-info"><div class="price-info-card"><h2 class="price-info-card-heading">現在 <span class="price-info-card-heading__count">${result.count}点</span> のメニューが入っています</h2>${summaryMarkup(result)}
      <a class="c-button c-button--fill-red" href="/cart/estimate/">お客様情報の入力に進む</a><p class="cch-cart-note">お見積もりは無料です。</p></div></aside></div>`;
  }

  function renderOptions(result) {
    const mount = document.querySelector('[data-cart-options]');
    if (!mount) return;
    const parents = [...new Set(result.details.flatMap(line => line.item.kind === 'option' ? [] : [line.key, ...(line.item.includes || [])]))];
    const groups = parents.map(key => {
      const options = Object.entries(catalogue.items).filter(([, item]) => item.parentKey === key);
      if (!options.length) return '';
      return `<section class="cch-cart-option-group"><h2>${escape(catalogue.items[key].name)}</h2><div class="cch-cart-options-grid">${options.map(([optionKey, item]) => {
        const line = lines.find(l => l.key === optionKey) || {key: optionKey, quantity: 0};
        return `<article class="cch-cart-option"><h3>${escape(item.name)}</h3><p>${priceLabel(item)}</p>${quantityInput(line)}</article>`;
      }).join('')}</div></section>`;
    }).join('');
    mount.innerHTML = result.count ? `${groups || '<p>選択中のサービスに追加オプションはありません。</p>'}${summaryMarkup(result)}<a class="c-button c-button--fill-red" href="/cart/">カートを確認する</a>` : '<p class="cch-cart-empty">サービスを選ぶと、対応するオプションを選択できます。</p><a class="c-button" href="/quick_cart/">サービスを選ぶ</a>';
  }

  function syncCounters() {
    for (const [card, keys] of bindings) {
      const counters = [...card.querySelectorAll('.c-counter__input')];
      counters.forEach((input, index) => {
        if (quick) input.value = String(lines.find(line => line.key === keys[index])?.quantity || 0);
        for (const button of input.closest('.js-counter').querySelectorAll('.js-counter-button')) {
          button.disabled = button.dataset.type === 'decrement' ? Number(input.value) <= Number(input.min || 0) : Number(input.value) >= Number(input.max || 30);
        }
      });
      if (quick) card.classList.toggle('is-selected', keys.some(key => lines.some(line => line.key === key)));
    }
  }

  function refresh() {
    const result = core.calculate(lines, catalogue);
    for (const node of document.querySelectorAll('#js-floating-total-quantity, #js-header-total-amount > span, .js-total-amount')) node.textContent = totalLabel(result);
    for (const node of document.querySelectorAll('#js-floating-total-amount')) node.dataset.cartCount = String(result.count);
    for (const node of document.querySelectorAll('#js-header-total-count > span')) node.textContent = String(result.count);
    for (const node of document.querySelectorAll('.cart-check-button__icon-container')) node.dataset.count = String(result.count);
    for (const node of document.querySelectorAll('#js-discount .discount__price')) node.textContent = result.discount ? '−' + format(result.discount) + '円' : '−';
    const next = document.getElementById('js-next-button');
    if (next) {
      next.classList.toggle('is-disabled', !result.count);
      next.setAttribute('aria-disabled', String(!result.count));
      next.href = '/quick_cart/option/';
    }
    for (const table of document.querySelectorAll('#cart-modal .cart-table')) {
      table.innerHTML = `<thead><tr><th>内容</th><th>数量</th><th>金額（税込）</th></tr></thead><tbody>${result.details.map(line => `<tr><td>${escape(line.item.name)}</td><td>${line.quantity}</td><td>${line.amount === null ? '別途見積り' : format(line.amount) + '円'}</td></tr>`).join('')}<tr><th colspan="2">合計金額（税込）</th><td>${totalLabel(result)}円</td></tr></tbody>`;
    }
    syncCounters();
    renderCart(result);
    renderOptions(result);
    window.cartData = {total_amount: result.total, total_quantity: result.count};
    window.dispatchEvent(new CustomEvent('cch:cart-updated', {detail: result}));
  }

  function switchVariant(select) {
    const card = select.closest('.js-product-card');
    const index = select.selectedIndex;
    const parentInput = card.querySelector('input[name="product-id"]');
    if (parentInput) parentInput.value = select.value;
    const wrapper = card.closest('.js-products') || card;
    for (const group of wrapper.querySelectorAll('[data-switch-target="prices"], [data-switch-target="options"], [data-switch-target="counters"], .js-price, .js-actions')) {
      [...group.children].forEach((child, i) => child.classList.toggle('is-active', i === index));
    }
    select.dispatchEvent(new Event('changeRoomType'));
  }

  function addCard(card) {
    const key = keyFor(card);
    const count = countFor(card);
    if (!count) throw new Error('数量を選択してください。');
    update(key, count, true);
    show(`${catalogue.items[key].name} × ${count}`, true);
  }

  function addOffice() {
    const entries = [...bindings].flatMap(([card, keys]) => {
      const count = countFor(card);
      return count ? [{key: keys[0], quantity: count}] : [];
    });
    if (!entries.length) throw new Error('商品と数量を選択してください。');
    let next = read();
    entries.sort((a, b) => Number(Boolean(catalogue.items[a.key].parentKey)) - Number(Boolean(catalogue.items[b.key].parentKey)));
    for (const entry of entries) next = core.change(next, entry.key, entry.quantity, catalogue, true);
    commit(next);
    show(entries.map(line => `${catalogue.items[line.key].name} × ${line.quantity}`).join('、'), true);
  }

  for (const button of document.querySelectorAll('.js-add-cart, #js-add-cart')) {
    button.removeAttribute('data-demo-dialog');
    button.removeAttribute('disabled');
  }
  for (const [card] of bindings) {
    const button = card.querySelector('.js-add-cart');
    if (!button || card.querySelector('.js-product-quantity select, .c-counter__input')) continue;
    const quantity = document.createElement('div');
    quantity.className = 'c-card-select js-product-quantity cch-cart-inline-quantity';
    quantity.innerHTML = `<select class="c-card-select__options" aria-label="${escape(catalogue.items[keyFor(card)].name)}の数量">${Array.from({length:30}, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}</select><div class="c-card-select__icon"></div>`;
    button.before(quantity);
    button.parentElement.classList.add('cch-cart-inline-controls');
    button.querySelector('.c-button__text').textContent = 'カートに追加';
  }
  for (const group of document.querySelectorAll('.js-options')) group.classList.remove('is-disabled');

  document.addEventListener('click', event => {
    const button = event.target.closest('.js-add-cart, #js-add-cart, .js-counter-button, [data-cart-remove], #js-next-button');
    if (!button) return;
    if (button.id === 'js-next-button') {
      if (!lines.length) event.preventDefault();
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    try {
      if (button.hasAttribute('data-cart-remove')) update(button.dataset.cartRemove, 0);
      else if (button.matches('.js-counter-button')) {
        const input = document.getElementById(button.getAttribute('aria-controls'));
        const count = Number(input.value) + (button.dataset.type === 'decrement' ? -1 : 1);
        if (count < Number(input.min || 0) || count > Number(input.max || 30)) return;
        const card = input.closest('.js-product-card');
        if (quick) {
          const index = [...card.querySelectorAll('.c-counter__input')].indexOf(input);
          update(bindings.get(card)[index], count);
        } else { input.value = String(count); syncCounters(); }
      } else if (button.id === 'js-add-cart') addOffice();
      else addCard(button.closest('.js-product-card'));
    } catch (error) { show(error.message); }
  }, true);

  document.addEventListener('change', event => {
    const input = event.target;
    try {
      if (input.matches('.js-room-types')) switchVariant(input);
      if (input.hasAttribute('data-cart-set')) update(input.dataset.cartSet, input.value);
    } catch (error) { refresh(); show(error.message); }
  });
  window.addEventListener('storage', event => { if (event.key === STORAGE_KEY || event.key === null) { read(); refresh(); } });
  window.addEventListener('pageshow', () => { read(); refresh(); });
  window.CCHCart = {refresh: () => { read(); refresh(); }, getSummary: () => core.calculate(read(), catalogue)};
  read();
  refresh();
  if (storageWarning) show(storageWarning);
})();
