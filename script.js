/* =========================================================
   Clouding Media — site script
   Handles: language toggle, mobile nav, FAQ, fade-in animations
   ========================================================= */

(function () {
  'use strict';

  // ----- Language toggle -----
  const STORAGE_KEY = 'cm-lang';
  const SUPPORTED = ['zh', 'en'];

  function getInitialLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && SUPPORTED.includes(stored)) return stored;
    const browser = (navigator.language || 'zh').toLowerCase();
    return browser.startsWith('zh') ? 'zh' : 'en';
  }

  function setLang(lang) {
    if (!SUPPORTED.includes(lang)) return;
    document.documentElement.lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    document.querySelectorAll('.lang-toggle button').forEach((b) => {
      b.classList.toggle('active', b.dataset.lang === lang);
    });
    // Update <title> if pageTitle data exists
    const titleEl = document.querySelector('title');
    if (titleEl && titleEl.dataset.zh && titleEl.dataset.en) {
      titleEl.textContent = lang === 'zh' ? titleEl.dataset.zh : titleEl.dataset.en;
    }
    // Update <option> text (since <option> can't hold HTML children)
    document.querySelectorAll('option[data-zh][data-en]').forEach((o) => {
      o.textContent = lang === 'zh' ? o.dataset.zh : o.dataset.en;
    });
    // Update placeholders if any
    document.querySelectorAll('[data-placeholder-zh][data-placeholder-en]').forEach((el) => {
      el.placeholder = lang === 'zh' ? el.dataset.placeholderZh : el.dataset.placeholderEn;
    });
  }

  function bindLangToggle() {
    document.querySelectorAll('.lang-toggle button').forEach((btn) => {
      btn.addEventListener('click', () => setLang(btn.dataset.lang));
    });
  }

  // ----- Mobile nav -----
  function bindMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const links = document.querySelector('.nav-links');
    if (!toggle || !links) return;
    toggle.addEventListener('click', () => links.classList.toggle('open'));
    links.querySelectorAll('a').forEach((a) =>
      a.addEventListener('click', () => links.classList.remove('open'))
    );
  }

  // ----- FAQ accordion -----
  function bindFaq() {
    document.querySelectorAll('.faq-item').forEach((item) => {
      const q = item.querySelector('.faq-q');
      if (!q) return;
      q.addEventListener('click', () => item.classList.toggle('open'));
    });
  }

  // ----- Scroll fade-in -----
  function bindScrollFade() {
    if (!('IntersectionObserver' in window)) return;
    const els = document.querySelectorAll('.fade-up');
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('visible');
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    els.forEach((el) => io.observe(el));
  }

  // ----- Footer year -----
  function setYear() {
    const y = document.getElementById('footer-year');
    if (y) y.textContent = new Date().getFullYear();
  }

  // ----- Init -----
  document.addEventListener('DOMContentLoaded', () => {
    setLang(getInitialLang());
    bindLangToggle();
    bindMobileMenu();
    bindFaq();
    bindScrollFade();
    setYear();
  });
})();
