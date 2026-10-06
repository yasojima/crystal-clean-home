(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('wf-data').textContent);
  const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));
  const product = window.CCH_CART_CATALOGUE.items['product:1'];
  const saving = product.tiers[0].price - product.tiers.find(tier => tier.min === 2).price;
  const banners = data.banners.map(banner => banner.key === 'aircon' ? {
    ...banner, emphasis: '１台あたり ' + saving.toLocaleString('ja-JP') + '円 お得',
    note: '壁掛けタイプ（お掃除機能なし）／同時に２台以上のご注文時・税込'
  } : banner);
  function bannerMarkup(banner, extra = '') {
    return '<a class="wf-banner wf-banner--' + banner.key + ' ' + extra + '" href="' + banner.link + '"><div class="wf-banner-copy"><span class="wf-eyebrow">' + escape(banner.label) + '</span><h3>' + banner.title.map(line => '<span>' + escape(line) + '</span>').join('') + '</h3>' + (banner.emphasis ? '<p class="wf-emphasis">' + escape(banner.emphasis) + '</p>' : '<p class="wf-banner-text">' + escape(banner.description) + '</p>') + '<span class="wf-banner-action">' + escape(banner.action) + ' <span aria-hidden="true">→</span></span></div><div class="wf-banner-art" aria-hidden="true">' + Array.from({length: banner.key === 'aircon' ? 2 : 1}, () => '<img src="' + banner.image + '" alt="" loading="lazy" decoding="async">').join('') + '</div>' + (banner.note ? '<small class="wf-banner-note">' + escape(banner.note) + '</small>' : '') + '</a>';
  }
  const renderers = {
    A: () => bannerMarkup(banners[0], 'wf-banner-wide'),
    B: () => '<div class="wf-slider" role="region" aria-roledescription="カルーセル" aria-label="お掃除特集"><div class="wf-slides">' + banners.map((banner, index) => '<div class="wf-slide" data-wf-slide="' + index + '" role="group" aria-roledescription="スライド" aria-label="' + (index + 1) + ' / ' + banners.length + '" ' + (index ? 'hidden' : '') + '>' + bannerMarkup(banner, 'wf-banner-wide') + '</div>').join('') + '</div><div class="wf-slider-controls"><button type="button" data-wf-slide-step="-1" aria-label="前の特集">←</button><div class="wf-slide-dots">' + banners.map((banner, index) => '<button type="button" data-wf-slide-to="' + index + '" aria-label="' + escape(banner.label) + 'を表示" aria-pressed="' + (index === 0) + '">' + String(index + 1).padStart(2, '0') + '</button>').join('') + '</div><span class="wf-slide-status" aria-live="polite">1 / ' + banners.length + '</span><button type="button" data-wf-slide-step="1" aria-label="次の特集">→</button></div></div>',
    C: () => '<div class="wf-banner-mosaic">' + banners.map((banner, index) => bannerMarkup(banner, index === 0 ? 'wf-banner-main' : 'wf-banner-small')).join('') + '</div>'
  };
  const section = document.querySelector('[data-wf-section="pickup"]');
  section.querySelector('[data-wf-panels]').innerHTML = Object.entries(renderers).map(([letter, render]) => '<div class="wf-panel" id="wf-pickup-' + letter + '" data-wf-panel="' + letter + '" ' + (letter === 'A' ? '' : 'hidden') + '>' + render() + '</div>').join('');
  const newsSection = document.querySelector('[data-wf-section="news"]');
  const metadata = item => '<span class="wf-news-date">' + escape(item.date) + '</span><span class="wf-news-category">' + escape(item.category) + '</span>';
  const newsRow = item => '<li><button type="button" class="wf-news-row" data-wf-news-id="' + item.id + '">' + metadata(item) + '<span class="wf-news-title">' + escape(item.title) + '</span><span class="wf-news-arrow" aria-hidden="true">→</span></button></li>';
  const newsCard = (item, main = false) => '<button type="button" class="wf-news-card' + (main ? ' wf-news-card--main' : '') + '" data-wf-news-id="' + item.id + '">' + (main ? '<span class="wf-news-pick">注目のお知らせ</span>' : '') + '<span class="wf-news-meta">' + metadata(item) + '</span><span class="wf-news-title">' + escape(item.title) + '</span><span class="wf-news-summary">' + escape(item.summary) + '</span><span class="wf-news-card-action">詳しく見る <span aria-hidden="true">→</span></span></button>';
  const allNews = '<div class="wf-news-footer"><button type="button" class="wf-news-all" data-wf-news-list>お知らせ一覧を見る <span aria-hidden="true">→</span></button></div>';
  const newsRenderers = {
    A: () => '<ul class="wf-news-list">' + data.news.map(newsRow).join('') + '</ul>' + allNews,
    B: () => '<div class="wf-news-feature">' + newsCard(data.news[0], true) + '<div class="wf-news-secondary">' + data.news.slice(1).map(item => newsCard(item)).join('') + '</div></div>' + allNews,
    C: () => '<div class="wf-news-cards">' + data.news.map(item => newsCard(item)).join('') + '</div>' + allNews
  };
  newsSection.querySelector('[data-wf-panels]').innerHTML = Object.entries(newsRenderers).map(([letter, render]) => '<div class="wf-panel" id="wf-news-' + letter + '" data-wf-panel="' + letter + '" ' + (letter === 'A' ? '' : 'hidden') + '>' + render() + '</div>').join('');
  function select(target, letter, persist = true) {
    target.querySelectorAll('[data-wf-panel]').forEach(panel => { panel.hidden = panel.dataset.wfPanel !== letter; });
    target.querySelectorAll('[data-wf-choice]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.wfChoice === letter)));
    if (persist) {
      const url = new URL(location.href);
      ['choose','budget','flow','preset'].forEach(key => url.searchParams.delete(key));
      url.searchParams.set(target.dataset.wfSection, letter);
      history.replaceState(null, '', url);
    }
  }
  const params = new URLSearchParams(location.search);
  [section, newsSection].forEach(target => {
    const initial = params.get(target.dataset.wfSection) || 'A';
    select(target, ['A','B','C'].includes(initial) ? initial : 'A', false);
  });
  if (['#wf-choose','#wf-budget','#wf-flow'].includes(location.hash)) location.replace('#wf-pickup');
  let activeSlide = 0;
  const dialog = document.querySelector('.wf-news-dialog');
  const detail = dialog.querySelector('[data-wf-news-detail]');
  function openNews(id) {
    const item = data.news.find(entry => entry.id === id);
    if (!item) return;
    detail.innerHTML = '<p class="wf-news-draft">表示例・仮原稿</p><div class="wf-news-meta">' + metadata(item) + '</div><h2 id="wf-news-dialog-title">' + escape(item.title) + '</h2><p class="wf-news-body">' + escape(item.body) + '</p><button type="button" class="wf-news-back" data-wf-news-list>一覧に戻る</button>';
    if (!dialog.open) dialog.showModal();
    dialog.querySelector('[data-wf-news-close]').focus();
  }
  function openNewsList() {
    detail.innerHTML = '<p class="wf-news-draft">表示例・仮原稿</p><h2 id="wf-news-dialog-title">お知らせ一覧</h2><ul class="wf-news-list">' + data.news.map(newsRow).join('') + '</ul>';
    if (!dialog.open) dialog.showModal();
    dialog.querySelector('[data-wf-news-close]').focus();
  }
  function showSlide(index) {
    activeSlide = (index + banners.length) % banners.length;
    section.querySelectorAll('[data-wf-slide]').forEach(slide => { slide.hidden = Number(slide.dataset.wfSlide) !== activeSlide; });
    section.querySelectorAll('[data-wf-slide-to]').forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.wfSlideTo) === activeSlide)));
    section.querySelector('.wf-slide-status').textContent = (activeSlide + 1) + ' / ' + banners.length;
  }
  document.addEventListener('click', event => {
    const choice = event.target.closest('[data-wf-choice]');
    if (choice) select(choice.closest('[data-wf-section]'), choice.dataset.wfChoice);
    const news = event.target.closest('[data-wf-news-id]');
    if (news) openNews(news.dataset.wfNewsId);
    if (event.target.closest('[data-wf-news-list]')) openNewsList();
    if (event.target.closest('[data-wf-news-close]')) dialog.close();
    const step = event.target.closest('[data-wf-slide-step]');
    if (step) showSlide(activeSlide + Number(step.dataset.wfSlideStep));
    const dot = event.target.closest('[data-wf-slide-to]');
    if (dot) showSlide(Number(dot.dataset.wfSlideTo));
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
  section.querySelector('.wf-slider').addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      showSlide(activeSlide + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
})();
