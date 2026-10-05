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

  function priceMarkup(item, amount = item.tiers[0]?.price) {
    if (item.quote) return '<p class="cch-cart-quote">別途見積り</p>';
    return `<p class="c-price"><span class="c-price__text">${format(amount)}${item.approximate ? '〜' : ''}</span><span class="c-price__unit">（税込）／${escape(item.unit)}</span></p>`;
  }

  function counterMarkup(line) {
    const name = escape(line.item.name);
    const key = escape(line.key);
    const id = 'cart-quantity-' + key;
    return `<button type="button" id="cart-remove-${key}" class="cch-cart-remove" data-cart-remove="${key}" aria-label="${name}を削除">削除</button>
      <div class="c-counter cch-cart-counter">
        <button type="button" id="cart-minus-${key}" class="c-counter__button" data-cart-step="${key}" data-delta="-1" aria-controls="${id}" aria-label="${name}の数量を1つ減らす" ${line.quantity <= 1 ? 'disabled' : ''}><span class="c-icon c-icon--minus c-counter__icon"></span></button>
        <input id="${id}" class="c-counter__input" type="text" readonly value="${line.quantity}" aria-label="${name}の数量">
        <button type="button" id="cart-plus-${key}" class="c-counter__button" data-cart-step="${key}" data-delta="1" aria-controls="${id}" aria-label="${name}の数量を1つ増やす" ${line.quantity >= core.MAX_QUANTITY ? 'disabled' : ''}><span class="c-icon c-icon--plus c-counter__icon"></span></button>
      </div>`;
  }

  function selectedOptionMarkup(line) {
    return `<li class="option-card cch-cart-selected-option" data-cart-line="${escape(line.key)}"><div><h4 class="option-card__heading">${escape(line.item.name)}</h4>${priceMarkup(line.item, line.unitPrice)}</div><div class="cch-cart-selected-option__actions">${counterMarkup(line)}</div></li>`;
  }

  function optionCardMarkup(key, item, context) {
    const id = `${context}-${key}`;
    return `<article class="c-product-additional-card cch-cart-option-card" data-cart-option="${escape(key)}">
      <div class="c-product-additional-card__main">${item.image ? `<img class="c-flex-image c-product-additional-card__image" src="${escape(item.image)}" width="72" height="72" alt="" loading="lazy">` : ''}
        <div class="c-product-additional-card__content" style="--image-width:${item.image ? 72 : 0}px"><h4 class="c-product-additional-card__heading">${escape(item.name)}</h4>${priceMarkup(item)}</div>
        ${item.description ? `<p class="c-product-additional-card__description">${escape(item.description)}</p>` : ''}</div>
      <div class="c-product-additional-card__footer">
        <div class="c-card-select c-product-additional-card__quantity"><select id="cart-select-${escape(id)}" class="c-card-select__options" aria-label="${escape(item.name)}の追加数量">${Array.from({length: 30}, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}</select><div class="c-card-select__icon"></div></div>
        <button type="button" id="cart-add-${escape(id)}" class="c-button c-button--fill-red c-product-additional-card__cart-button" data-cart-add-option="${escape(key)}"><span class="c-button__text">カートに追加</span><span class="c-icon c-icon--circle-caret-right c-button__icon"></span></button>
      </div></article>`;
  }

  function optionsFor(key) {
    return Object.entries(catalogue.items).filter(([, item]) => item.parentKey === key);
  }

  function checkoutButton() {
    return '<a class="c-button c-button--fill-red cch-cart-checkout" href="/cart/estimate/"><span class="c-button__text">お客様情報の入力に進む</span><span class="c-icon c-icon--circle-caret-right c-button__icon"></span></a>';
  }

  function productMarkup(line, selected, parentKeys) {
    const options = parentKeys.flatMap(optionsFor);
    return `<li class="product-card cch-cart-product" data-cart-line="${escape(line.key)}"><div class="product-card__main">
      ${line.item.image ? `<img class="c-flex-image product-card__image" src="${escape(line.item.image)}" alt="" loading="lazy" width="176" height="132">` : ''}<div class="product-card__content">
      <h3 class="product-card__heading">${escape(line.item.name)}</h3>${priceMarkup(line.item, line.unitPrice)}
      ${line.discount ? `<p class="cch-cart-discount">数量割引適用：−${format(line.discount)}円（税込）</p>` : ''}</div></div>
      <div class="product-card__footer">${counterMarkup(line)}</div><div class="cch-cart-product__options">${checkoutButton()}
      ${selected.length ? `<div class="option-items cch-cart-selected-options"><h3 class="option-items__heading">■ オプション</h3><ul>${selected.map(selectedOptionMarkup).join('')}</ul></div>` : ''}
      ${options.length ? `<details class="cch-cart-extra" data-cart-disclosure="${escape(line.key)}"><summary>さらに追加できるオプションがあります！<span aria-hidden="true"></span></summary><div class="cch-cart-extra__cards">${options.map(([key, item]) => optionCardMarkup(key, item, 'inline-' + line.key)).join('')}</div></details>` : ''}</div></li>`;
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
      mount.innerHTML = '<div class="empty-cart cch-cart-empty"><h2 class="empty-cart__heading">カートが空です</h2><p>ご希望のサービスをお選びください。</p><a class="c-button" href="/">お買い物を続ける</a></div>';
      const recommendations = document.querySelector('[data-cart-recommendations]');
      if (recommendations) { recommendations.hidden = true; recommendations.innerHTML = ''; }
      return;
    }
    const activeId = document.activeElement?.id;
    const open = new Set([...document.querySelectorAll('[data-cart-disclosure][open]')].map(node => node.dataset.cartDisclosure));
    const scroll = new Map([...document.querySelectorAll('[data-cart-carousel]')].map(node => [node.dataset.cartCarousel, node.scrollLeft]));
    const selections = new Map([...document.querySelectorAll('.cch-cart-option-card select')].map(node => [node.id, node.value]));
    const claimedParents = new Set();
    const products = result.details.filter(line => line.item.kind !== 'option');
    const parentGroups = [];
    const grouped = products.map(line => {
      const parentKeys = [line.key, ...(line.item.includes || [])].filter(key => !claimedParents.has(key));
      parentKeys.forEach(key => { claimedParents.add(key); parentGroups.push(key); });
      const selected = result.details.filter(option => parentKeys.includes(option.item.parentKey));
      return productMarkup(line, selected, parentKeys);
    }).join('');
    const beforeTax = (result.total + result.discount) - Math.floor((result.total + result.discount) * catalogue.taxRate / (100 + catalogue.taxRate));
    const discount = beforeTax - result.subtotal;
    mount.innerHTML = `<div class="cart"><div class="cart__contents"><ul class="cch-cart-lines">${grouped}</ul></div>
      <aside class="cart__price-info" aria-label="お見積り金額"><div class="price-info-card"><h2 class="price-info-card-heading">現在 <span class="price-info-card-heading__count">${result.count}点</span> のメニューが入っています</h2>
      <div class="price-info-card__detail"><dl class="price-description"><dt class="price-description__term">合計金額（税抜）：</dt><dd class="price-description__price" data-cart-subtotal-before>${format(beforeTax)}</dd></dl>
      ${discount ? `<details class="cch-cart-discount-detail" data-cart-disclosure="discount"><summary><span>数量割引（税抜）：</span><strong>−${format(discount)}円</strong><small>内訳を見る <span aria-hidden="true">＋</span></small></summary><dl>${result.details.filter(line => line.discount).map(line => `<div><dt>${escape(line.item.name)}</dt><dd>−${format(line.discount)}円（税込）</dd></div>`).join('')}</dl></details>
      <dl class="price-description"><dt class="price-description__term">割引適用後金額（税抜）：</dt><dd class="price-description__price">${format(result.subtotal)}</dd></dl>` : ''}
      <dl class="price-description"><dt class="price-description__term">消費税（${catalogue.taxRate}%）：</dt><dd class="price-description__price">${format(result.tax)}</dd></dl></div>
      <dl class="price-info-card__total-amount total-amount"><dt class="c-label-tag c-label-tag--pill-shape total-amount__term">合計金額（税込）</dt><dd class="total-amount__price" data-cart-total>${totalLabel(result)}</dd></dl>
      ${result.approximate ? '<p class="cch-cart-note">「〜」の付いたサービスは表示料金をもとにした概算です。</p>' : ''}
      ${result.quoteCount ? '<p class="cch-cart-note">別途見積りの商品は上記の合計金額に含まれていません。</p>' : ''}</div>
      <div class="cch-cart-sidebar-actions">${checkoutButton()}<a class="c-button" href="/"><span class="c-button__text">お買い物を続ける</span><span class="c-icon c-icon--circle-caret-right c-button__icon"></span></a></div></aside></div>`;
    renderRecommendations(parentGroups);
    for (const node of document.querySelectorAll('[data-cart-disclosure]')) node.open = open.has(node.dataset.cartDisclosure);
    for (const node of document.querySelectorAll('.cch-cart-option-card select')) if (selections.has(node.id)) node.value = selections.get(node.id);
    for (const track of document.querySelectorAll('[data-cart-carousel]')) {
      track.scrollLeft = scroll.get(track.dataset.cartCarousel) || 0;
      syncCarousel(track);
      track.addEventListener('scroll', () => syncCarousel(track), {passive: true});
    }
    if (activeId) document.getElementById(activeId)?.focus({preventScroll: true});
  }

  function renderRecommendations(parents) {
    const mount = document.querySelector('[data-cart-recommendations]');
    if (!mount) return;
    const groups = parents.filter(key => optionsFor(key).length).map(key => {
      const item = catalogue.items[key];
      const id = 'cart-carousel-' + key;
      return `<section class="recommend-options" aria-labelledby="${id}-heading"><div class="recommend-options__head">
        ${item.image ? `<img class="c-flex-image" src="${escape(item.image)}" alt="" width="104" height="64" loading="lazy">` : ''}<h3 id="${id}-heading" class="recommend-options-heading">${escape(item.name)}<span class="recommend-options-heading__small">にオススメ</span></h3></div>
        <div class="cch-cart-carousel-container"><div id="${id}" class="cch-cart-carousel" data-cart-carousel="${escape(key)}" role="region" aria-label="${escape(item.name)}のオプション" tabindex="0">${optionsFor(key).map(([optionKey, option]) => optionCardMarkup(optionKey, option, 'recommend')).join('')}</div>
        <button type="button" class="cch-cart-carousel-arrow cch-cart-carousel-arrow--prev" data-cart-slide="${escape(key)}" data-direction="-1" aria-controls="${id}" aria-label="${escape(item.name)}の前のオプション" disabled><span aria-hidden="true">‹</span></button>
        <button type="button" class="cch-cart-carousel-arrow cch-cart-carousel-arrow--next" data-cart-slide="${escape(key)}" data-direction="1" aria-controls="${id}" aria-label="${escape(item.name)}の次のオプション"><span aria-hidden="true">›</span></button></div></section>`;
    }).join('');
    mount.hidden = !groups;
    mount.innerHTML = groups ? `<div class="cch-cart-recommendations__inner"><h2 id="cart-options-heading">カートに入れたサービスにオススメのオプション</h2>${groups}</div>` : '';
  }

  function syncCarousel(track) {
    const container = track.parentElement;
    const end = track.scrollWidth - track.clientWidth;
    container.querySelector('[data-direction="-1"]').disabled = track.scrollLeft <= 1;
    container.querySelector('[data-direction="1"]').disabled = track.scrollLeft >= end - 1;
    container.classList.toggle('cch-cart-carousel-container--more', track.scrollLeft < end - 1);
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
    const slide = event.target.closest('[data-cart-slide]');
    if (slide) {
      const track = document.getElementById(slide.getAttribute('aria-controls'));
      track.scrollBy({left: Number(slide.dataset.direction) * track.clientWidth * .85, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'});
      return;
    }
    const button = event.target.closest('.js-add-cart, #js-add-cart, .js-counter-button, [data-cart-remove], [data-cart-step], [data-cart-add-option], #js-next-button');
    if (!button) return;
    if (button.id === 'js-next-button') {
      if (!lines.length) event.preventDefault();
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    try {
      if (button.hasAttribute('data-cart-step')) {
        const line = read().find(line => line.key === button.dataset.cartStep);
        if (line) update(line.key, line.quantity + Number(button.dataset.delta));
      } else if (button.hasAttribute('data-cart-add-option')) {
        const key = button.dataset.cartAddOption;
        const count = button.closest('.cch-cart-option-card').querySelector('select').value;
        update(key, count, true);
        document.querySelector('[data-cart-status]').textContent = `${catalogue.items[key].name}を${count}点追加しました。`;
      } else if (button.hasAttribute('data-cart-remove')) update(button.dataset.cartRemove, 0);
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
  window.addEventListener('resize', () => document.querySelectorAll('[data-cart-carousel]').forEach(syncCarousel));
  window.addEventListener('pageshow', () => { read(); refresh(); });
  window.CCHCart = {refresh: () => { read(); refresh(); }, getSummary: () => core.calculate(read(), catalogue)};
  read();
  refresh();
  if (storageWarning) show(storageWarning);
})();
