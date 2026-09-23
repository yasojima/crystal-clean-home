(() => {
  const media = matchMedia('(max-width:992px)');
  const originals = new WeakMap();
  function apply(root) {
    const elements = root.matches?.('img,source,video') ? [root] : [...root.querySelectorAll('img,source,video')];
    const choices = window.CCHDeviceImages[media.matches ? 'mobile' : 'desktop'];
    for (const element of elements) {
      let attrs = originals.get(element);
      if (!attrs) {
        attrs = {};
        for (const key of ['src','data-src','srcset','data-srcset','poster']) {
          const value = element.getAttribute(key);
          if (value && !value.startsWith('data:')) attrs[key] = value;
        }
        originals.set(element, attrs);
      }
      for (const [key, value] of Object.entries(attrs)) {
        const selected = choices[value] ?? value;
        if (element.getAttribute(key) !== selected) element.setAttribute(key, selected);
        if (key === 'data-src' && element.complete && element.naturalWidth && element.src !== selected) element.setAttribute('src', selected);
      }
    }
  }
  apply(document);
  media.addEventListener('change', () => apply(document));
  new MutationObserver(records => {
    for (const record of records) for (const node of record.addedNodes) if (node.nodeType === 1) apply(node);
  }).observe(document.body, {childList:true, subtree:true});
})();
