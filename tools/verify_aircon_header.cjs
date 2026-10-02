const fs = require('fs');
const path = require('path');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve(__dirname, '..');
const local = process.argv.includes('--local');
const origin = process.env.SITE_ORIGIN || 'https://yasojima.github.io';
const output = process.env.SCREENSHOT_DIR;

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const page = await browser.newPage();
  const errors = [];
  const checks = [];
  page.on('pageerror', error => errors.push(error.message));
  if (local) {
    for (const [url, file, contentType] of [
      ['**/house-cleaning/aircon/', 'house-cleaning/aircon/index.html', 'text/html'],
      ['**/assets/css/aircon-header.css*', 'assets/css/aircon-header.css', 'text/css'],
      ['**/assets/css/aircon-hero.css*', 'assets/css/aircon-hero.css', 'text/css'],
      ['**/assets/css/aircon-layout.css*', 'assets/css/aircon-layout.css', 'text/css'],
      ['**/assets/css/aircon-voice-bubbles.css*', 'assets/css/aircon-voice-bubbles.css', 'text/css'],
      ['**/assets/images/voices/reference-rating.webp', 'assets/images/voices/reference-rating.webp', 'image/webp'],
      ['**/assets/images/common-parts/decoration/section-arrows-black.svg', 'assets/images/common-parts/decoration/section-arrows-black.svg', 'image/svg+xml'],
      ['**/assets/js/aircon-header.js*', 'assets/js/aircon-header.js', 'text/javascript'],
    ]) {
      await page.route(url, route => route.fulfill({ contentType, body: fs.readFileSync(path.join(root, 'source/site', file)) }));
    }
  }
  if (output) fs.mkdirSync(output, { recursive: true });
  try {
    for (const [width, height] of [[1441, 799], [1581, 1326], [1024, 768], [390, 844], [320, 700]]) {
      await page.setViewportSize({ width, height });
      await page.goto(`${origin}/house-cleaning/aircon/`, { waitUntil: 'load' });
      await page.evaluate(() => document.fonts.ready);
      const geometry = await page.evaluate(() => {
        const hero = document.querySelector('.c-house-cleaning-mv--check').getBoundingClientRect();
        const check = document.querySelector('.c-house-cleaning-mv__check');
        const rect = check.getBoundingClientRect();
        const button = document.querySelector('.c-header__menu').getBoundingClientRect();
        return {
          heroBottom: hero.bottom,
          checkBottom: rect.bottom,
          checkCenter: rect.x + rect.width / 2,
          contentCenter: hero.x + hero.width / 2,
          label: check.textContent,
          nextHeadingTop: document.querySelector('.p-page-anchors__heading').getBoundingClientRect().top,
          buttonSize: button.width,
          overflow: document.documentElement.scrollWidth > innerWidth + 1,
        };
      });
      assert.ok(Math.abs(geometry.heroBottom - height) < 1, 'Hero ends at the viewport bottom');
      assert.ok(Math.abs(geometry.checkBottom - height) < 1, 'Circular Check edge fits the viewport');
      assert.ok(Math.abs(geometry.checkCenter - geometry.contentCenter) < 1, 'Check is centered');
      assert.equal(geometry.label, 'Check！');
      assert.ok(geometry.nextHeadingTop >= height, 'Service selector starts after the first view');
      assert.equal(geometry.buttonSize, width < 768 ? 44 : 48);
      assert.equal(geometry.overflow, false);
      assert.equal(await page.locator('.c-issue-list__heading').textContent(), 'こんなお悩みはありませんか？');
      assert.equal(await page.locator('.c-voice-card__star').count(), 30);
      assert.equal(await page.locator('.c-voice-card__star--empty').count(), 3);
      assert.equal(await page.locator('.c-voice-card__nickname,.c-voice-card__demographic,.c-voice-bubbles .c-voice-card__heading,.c-voice-bubbles .c-voice-card__text').evaluateAll(nodes => nodes.every(node => getComputedStyle(node).color === 'rgb(0, 0, 0)')), true);
      if (output) await page.screenshot({ path: path.join(output, `aircon-fv-check-${width}.png`) });

      const layout = await page.evaluate(() => ({
        markers: [...document.querySelectorAll('.c-service-page .l-section--blue-bubbles')].map(node => {
          const style = getComputedStyle(node, '::before');
          return { width: style.width, height: style.height, top: style.top, image: style.backgroundImage };
        }),
        cards: [...document.querySelectorAll('.c-reasons__card')].map(card => {
          const rect = card.getBoundingClientRect();
          const title = card.querySelector('h3').getBoundingClientRect();
          const body = card.querySelector('p').getBoundingClientRect();
          return {
            width: rect.width, height: rect.height, radius: getComputedStyle(card).borderRadius,
            centerOffset: (title.top + body.bottom - rect.top - rect.bottom) / 2,
            textAlign: getComputedStyle(card).textAlign,
            background: getComputedStyle(card.nextElementSibling).backgroundColor,
          };
        }),
      }));
      assert.equal(layout.markers.length, 6);
      for (const marker of layout.markers) {
        assert.equal(marker.width, '12px');
        assert.equal(marker.height, '36px');
        assert.equal(marker.top, '-22px');
        assert.ok(marker.image.includes('section-arrows-black.svg'));
      }
      assert.equal(layout.cards.length, 3);
      for (const card of layout.cards) {
        assert.ok(Math.abs(card.width - card.height) < 1, 'Reason cards are true circles');
        assert.equal(card.radius, '50%');
        assert.ok(Math.abs(card.centerOffset) < 1, 'Reason text is vertically centered');
        assert.equal(card.textAlign, 'center');
        assert.equal(card.background, 'rgb(38, 69, 116)');
      }
      if (output) {
        await page.locator('.c-voice-section--bubble-preview').evaluate(node => window.scrollTo({
          top: scrollY + node.getBoundingClientRect().top - document.querySelector('.c-header').getBoundingClientRect().height,
          behavior: 'instant',
        }));
        await page.screenshot({ path: path.join(output, `aircon-review-stars-${width}.png`) });
        await page.locator('.p-reasons').evaluate(node => window.scrollTo({
          top: scrollY + node.getBoundingClientRect().top - document.querySelector('.c-header').getBoundingClientRect().height - 20,
          behavior: 'instant',
        }));
        await page.screenshot({ path: path.join(output, `aircon-reasons-circles-${width}.png`) });
        const marker = page.locator('.l-section--blue-bubbles').first();
        await marker.scrollIntoViewIfNeeded();
        const box = await marker.boundingBox();
        if (box.y >= 22 && box.y < height - 50) {
          await page.screenshot({ path: path.join(output, `aircon-section-arrows-${width}.png`), clip: {
            x: box.x + box.width / 2 - 40, y: box.y - 30, width: 80, height: 70,
          } });
        }
      }

      if (width >= 1400) {
        await page.locator('.c-main-menu__item').nth(6).hover();
        await page.waitForTimeout(450);
        assert.equal(await page.locator('.aircon-mega').getAttribute('aria-hidden'), 'false');
        assert.equal(await page.locator('.c-main-menu__link svg').count(), 9);
        await page.locator('.aircon-mega__link').first().hover();
        await page.waitForTimeout(450);
        assert.equal(await page.locator('.aircon-mega__link').first().evaluate(node => getComputedStyle(node).color), 'rgb(45, 136, 239)');
        await page.mouse.move(5, 400);
      }

      await page.evaluate(() => window.scrollTo({ top: 1800, behavior: 'instant' }));
      await page.waitForTimeout(100);
      const button = page.locator('.c-header__menu');
      const before = await button.boundingBox();
      const scrollBefore = await page.evaluate(() => scrollY);
      await button.hover();
      await button.click();
      await page.waitForTimeout(450);
      await button.click();
      await page.waitForTimeout(100);
      await button.click();
      await page.waitForTimeout(700);
      const state = await page.locator('#menu').evaluate(menu => ({
        visible: getComputedStyle(menu).visibility === 'visible' && Number(getComputedStyle(menu).opacity) > .99,
        expanded: document.querySelector('.c-header__menu').getAttribute('aria-expanded'),
        links: menu.querySelectorAll('.aircon-full-menu__body a[href]').length,
        inert: menu.inert,
        parent: menu.parentElement.tagName,
      }));
      assert.equal(state.visible, true, 'Reopening during close keeps the menu visible');
      assert.equal(state.expanded, 'true');
      assert.equal(state.links, 50);
      assert.equal(state.inert, false);
      assert.equal(state.parent, 'BODY');
      const after = await button.boundingBox();
      assert.ok(Math.abs(before.x - after.x) < 1 && Math.abs(before.y - after.y) < 1, 'MENU does not jump');
      assert.equal(await page.evaluate(() => scrollY), scrollBefore, 'Page scroll position is retained');
      if (output) await page.screenshot({ path: path.join(output, `aircon-menu-stable-${width}.png`) });
      await page.keyboard.press('Escape');
      await page.waitForTimeout(450);
      assert.equal(await page.locator('#menu').evaluate(node => node.inert && getComputedStyle(node).visibility === 'hidden'), true);
      assert.equal(await button.getAttribute('aria-expanded'), 'false');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
      checks.push({ width, height, geometry, layout, rapidReopen: true, menuPositionStable: true, scrollPreserved: true });
    }
    assert.deepEqual(errors, []);
    const report = { checked_at: new Date().toISOString(), origin, local_overrides: local, checks, errors, passed: true };
    if (output) fs.writeFileSync(path.join(output, 'aircon-header-verification.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
