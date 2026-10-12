/* 全站語系切換器
   資料庫頁（data.html）有自己的字典，直接呼叫其 setLang；
   其餘靜態頁沒有翻譯版本，改導向 Google 翻譯代理網域。 */
(function () {
  var LANGS = [['zh', '繁中'], ['en', 'EN'], ['my', 'မြန်မာ']];
  var GT = { zh: 'zh-TW', en: 'en', my: 'my' };
  var KEY = 'cmlang';
  var onProxy = /\.translate\.goog$/i.test(location.hostname);

  var GLOBE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"' +
    ' stroke-linecap="round" aria-hidden="true">' +
    '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>' +
    '<path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18"/></svg>';

  function current() {
    if (onProxy) {
      var tl = new URLSearchParams(location.search).get('_x_tr_tl') || '';
      if (tl.indexOf('zh') === 0) return 'zh';
      if (tl === 'my' || tl === 'en') return tl;
    }
    try {
      var v = localStorage.getItem(KEY);
      if (v) return v;
    } catch (e) { /* 無痕視窗 */ }
    return (document.documentElement.lang || 'zh').slice(0, 2);
  }

  // 由 translate.goog 的主機名還原本站網址：-- 代表連字號，- 代表句點
  function origin() {
    var h = location.hostname.replace(/\.translate\.goog$/i, '');
    return 'https://' + h.replace(/--/g, '\u0000').replace(/-/g, '.').replace(/\u0000/g, '-');
  }

  function proxyUrl(tl) {
    var base = onProxy ? origin() : location.origin;
    var h = new URL(base).hostname.replace(/-/g, '--').replace(/\./g, '-');
    return 'https://' + h + '.translate.goog' + location.pathname +
      '?_x_tr_sl=zh-TW&_x_tr_tl=' + tl + '&_x_tr_hl=' + tl;
  }

  function pick(l) {
    try { localStorage.setItem(KEY, l); } catch (e) { /* 無痕視窗 */ }
    if (typeof window.setLang === 'function') { window.setLang(l); draw(); return; }
    if (typeof window.applyPageLang === 'function') { window.applyPageLang(l); draw(); return; }
  }

  function draw() {
    var box = document.getElementById('langbar');
    if (!box) return;
    var c = current();
    box.innerHTML = GLOBE + LANGS.map(function (p) {
      return '<button type="button" data-l="' + p[0] + '"' +
        (p[0] === 'my' ? ' lang="my"' : '') +
        (p[0] === c ? ' class="on" aria-current="true"' : '') +
        '>' + p[1] + '</button>';
    }).join('');
    Array.prototype.forEach.call(box.querySelectorAll('button'), function (b) {
      b.onclick = function () { pick(b.dataset.l); };
    });
  }

  function boot() {
    draw();
    var c = current();
    if (c !== 'zh' && typeof window.applyPageLang === 'function') window.applyPageLang(c);
  }

  window.LangBar = { draw: draw, pick: pick, current: current };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
