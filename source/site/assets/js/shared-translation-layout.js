const stylesheet = new URL("../css/translation-layout.css", import.meta.url).href;
const observedFrames = new WeakSet();
let scheduled = 0;

function styleRoot(root, target, language) {
  if (!root.querySelector("[data-translation-layout-style]")) {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = stylesheet;
    link.dataset.translationLayoutStyle = "";
    (root.head || root).append(link);
  }
  if (language) {
    if (target.dataset.translationActive !== language) target.dataset.translationActive = language;
    if (target.lang !== language) target.lang = language;
  } else {
    target.removeAttribute("data-translation-active");
    if (target !== document.documentElement) target.lang = "ja";
  }
}

function update() {
  scheduled = 0;
  const html = document.documentElement;
  const translated = html.classList.contains("translated-ltr") || html.classList.contains("translated-rtl");
  const language = translated && html.lang !== "ja" ? html.lang : "";
  const restored = html.hasAttribute("data-translation-active") && !language;
  styleRoot(document, html, language);
  for (const host of document.querySelectorAll(".shared-bottom-ui-root, #shared-bottom-ui-root")) {
    const root = host.shadowRoot;
    const component = root?.querySelector("[data-shared-bottom-ui-component]");
    if (component) styleRoot(root, component, language);
  }
  for (const frame of document.querySelectorAll("#price-frame")) {
    if (!observedFrames.has(frame)) {
      observedFrames.add(frame);
      frame.addEventListener("load", schedule);
    }
    try {
      const doc = frame.contentDocument;
      if (doc?.head) styleRoot(doc, doc.documentElement, language);
    } catch { /* Only same-origin price documents share layout rules. */ }
  }
  window.dispatchEvent(new Event("crystal-translation-layout"));
  if (restored) window.dispatchEvent(new Event("crystal-translation-restored"));
}

function schedule() {
  if (!scheduled) scheduled = window.setTimeout(update, 100);
}

export function bindTranslationLayout() {
  if (document.documentElement.dataset.translationLayoutBound) return;
  document.documentElement.dataset.translationLayoutBound = "true";
  for (const brand of document.querySelectorAll(".c-header__logo, .c-brand-banner__logo")) {
    brand.setAttribute("translate", "no");
    brand.classList.add("notranslate");
  }
  new MutationObserver(schedule).observe(document.documentElement, { attributes: true, attributeFilter: ["class", "lang"] });
  // Google inserts wrapper nodes asynchronously, including after the selected language changes.
  new MutationObserver(schedule).observe(document.body, { childList: true, characterData: true, subtree: true });
  update();
}
