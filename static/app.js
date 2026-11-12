// Tema claro/oscuro y buscador instantáneo
(function () {
  var root = document.documentElement;
  var themeBtn = document.getElementById('themeBtn');
  themeBtn && themeBtn.addEventListener('click', function () {
    var dark = root.dataset.theme === 'dark' ||
      (!root.dataset.theme && matchMedia('(prefers-color-scheme: dark)').matches);
    root.dataset.theme = dark ? 'light' : 'dark';
    try { localStorage.setItem('theme', root.dataset.theme); } catch (e) {}
  });

  var btn = document.getElementById('searchBtn');
  var panel = document.getElementById('searchPanel');
  var input = document.getElementById('searchInput');
  var out = document.getElementById('searchResults');
  var index = null;
  function norm(s) { return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  btn && btn.addEventListener('click', function () {
    panel.hidden = !panel.hidden;
    if (!panel.hidden) {
      input.focus();
      if (!index) fetch('/search.json').then(function (r) { return r.json(); }).then(function (d) { index = d; });
    }
  });
  input && input.addEventListener('input', function () {
    var q = norm(input.value.trim());
    if (!index || q.length < 2) { out.innerHTML = ''; return; }
    var words = q.split(/\s+/);
    var hits = index.filter(function (p) {
      var h = norm(p.t + ' ' + p.d + ' ' + p.c);
      return words.every(function (w) { return h.indexOf(w) > -1; });
    }).slice(0, 8);
    out.innerHTML = hits.length ? hits.map(function (p) {
      var a = document.createElement('a'); a.href = p.u; a.textContent = p.t;
      var s = document.createElement('small'); s.textContent = ' · ' + p.c; a.appendChild(s);
      return a.outerHTML;
    }).join('') : '<p style="color:var(--muted)">Sin resultados. ¡Pídenos esa guía!</p>';
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && panel && !panel.hidden) panel.hidden = true;
  });
})();
