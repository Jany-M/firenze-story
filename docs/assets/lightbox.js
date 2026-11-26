/* Shared image lightbox for /docs/ and /library/ — intercepts linked images (galleries + content). */
(function () {
  const EXT = /\.(jpe?g|png|webp|gif)(?:[?#].*)?$/i;
  let links = [];
  let index = 0;
  let ui, img, cap, btnPrev, btnNext;
  let keysBound = false;

  function collect(root) {
    const out = [];
    root.querySelectorAll('a[href]').forEach((a) => {
      const href = a.getAttribute('href') || '';
      if (!EXT.test(href)) return;
      if (!a.querySelector('img')) return;
      if (a.dataset.fsLightboxBound === '1') return;
      a.dataset.fsLightboxBound = '1';
      out.push(a);
    });
    return out;
  }

  function ensureUi() {
    let el = document.getElementById('fs-lightbox');
    if (el) return el;
    el = document.createElement('div');
    el.id = 'fs-lightbox';
    el.className = 'fs-lightbox';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.innerHTML =
      '<button type="button" class="fs-lightbox__btn fs-lightbox__close" aria-label="Close">&times;</button>' +
      '<button type="button" class="fs-lightbox__btn fs-lightbox__prev" aria-label="Previous">‹</button>' +
      '<img class="fs-lightbox__img" alt="" />' +
      '<button type="button" class="fs-lightbox__btn fs-lightbox__next" aria-label="Next">›</button>' +
      '<p class="fs-lightbox__cap" hidden></p>';
    document.body.appendChild(el);
    return el;
  }

  function captionFor(a) {
    const fig = a.closest('figure');
    const fc = fig && fig.querySelector('figcaption');
    if (fc) return fc.textContent.trim();
    const im = a.querySelector('img');
    return (im && (im.getAttribute('alt') || '')) || '';
  }

  function show(i) {
    if (!links.length) return;
    index = (i + links.length) % links.length;
    const a = links[index];
    img.src = a.href;
    img.alt = (a.querySelector('img') || {}).alt || '';
    const text = captionFor(a);
    if (text) {
      cap.textContent = text;
      cap.hidden = false;
    } else {
      cap.textContent = '';
      cap.hidden = true;
    }
    const many = links.length > 1;
    btnPrev.hidden = !many;
    btnNext.hidden = !many;
    ui.classList.add('is-open');
    document.documentElement.style.overflow = 'hidden';
  }

  function close() {
    ui.classList.remove('is-open');
    img.removeAttribute('src');
    document.documentElement.style.overflow = '';
  }

  function bindPage() {
    ui = ensureUi();
    img = ui.querySelector('.fs-lightbox__img');
    cap = ui.querySelector('.fs-lightbox__cap');
    btnPrev = ui.querySelector('.fs-lightbox__prev');
    btnNext = ui.querySelector('.fs-lightbox__next');

    const fresh = collect(document);
    if (fresh.length) {
      // Rebuild list from all bound gallery links still in the document
      links = Array.from(document.querySelectorAll('a[data-fs-lightbox-bound="1"]')).filter((a) =>
        document.body.contains(a)
      );
      fresh.forEach((a) => {
        a.addEventListener('click', (ev) => {
          ev.preventDefault();
          links = Array.from(document.querySelectorAll('a[data-fs-lightbox-bound="1"]')).filter((x) =>
            document.body.contains(x)
          );
          const i = links.indexOf(a);
          show(i >= 0 ? i : 0);
        });
      });
    }

    if (!ui.dataset.fsUiBound) {
      ui.dataset.fsUiBound = '1';
      ui.querySelector('.fs-lightbox__close').addEventListener('click', close);
      btnPrev.addEventListener('click', () => show(index - 1));
      btnNext.addEventListener('click', () => show(index + 1));
      ui.addEventListener('click', (ev) => {
        if (ev.target === ui) close();
      });
    }

    if (!keysBound) {
      keysBound = true;
      document.addEventListener('keydown', (ev) => {
        if (!ui || !ui.classList.contains('is-open')) return;
        if (ev.key === 'Escape') close();
        if (ev.key === 'ArrowLeft') show(index - 1);
        if (ev.key === 'ArrowRight') show(index + 1);
      });
    }
  }

  function init() {
    bindPage();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  if (typeof document$ !== 'undefined' && document$.subscribe) {
    document$.subscribe(init);
  }
})();
