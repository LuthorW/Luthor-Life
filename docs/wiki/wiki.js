// Wiki do Luthor Life: busca, menu no celular, tema claro/escuro, tabelas ordenáveis e página aleatória.
(function () {
  "use strict";
  var IDX = window.WIKI_INDEX || [];

  // ---- busca ----
  function semAcento(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  var input = document.querySelector(".busca input");
  var lista = document.querySelector(".resultados");
  var achados = [];
  var ativo = -1;

  function buscar(q) {
    q = semAcento(q.trim());
    if (!q) return [];
    var palavras = q.split(/\s+/);
    var res = [];
    IDX.forEach(function (p) {
      var t = semAcento(p.t);
      var ok = palavras.every(function (w) { return t.indexOf(w) >= 0 || semAcento(p.c).indexOf(w) >= 0; });
      if (!ok) return;
      var nota = t.indexOf(q) === 0 ? 0 : (t.indexOf(q) >= 0 ? 1 : 2);
      if (p.c === "Personagem") nota -= 0.5;
      if (p.c === "Página") nota -= 0.3;
      res.push({ p: p, n: nota });
    });
    res.sort(function (a, b) { return a.n - b.n || a.p.t.localeCompare(b.p.t); });
    return res.slice(0, 12).map(function (r) { return r.p; });
  }

  function mostrar() {
    lista.innerHTML = "";
    if (!input.value.trim()) { lista.hidden = true; return; }
    if (!achados.length) {
      lista.innerHTML = '<li class="vazio">Nada encontrado.</li>';
    }
    achados.forEach(function (p, i) {
      var li = document.createElement("li");
      if (i === ativo) li.className = "ativo";
      var a = document.createElement("a");
      a.href = p.u;
      if (p.i) {
        var img = document.createElement("img");
        img.src = "img/" + p.i; img.alt = "";
        a.appendChild(img);
      }
      a.appendChild(document.createTextNode(p.t));
      var s = document.createElement("small");
      s.textContent = p.c;
      a.appendChild(s);
      li.appendChild(a);
      lista.appendChild(li);
    });
    lista.hidden = false;
  }

  if (input && lista) {
    input.addEventListener("input", function () { achados = buscar(input.value); ativo = -1; mostrar(); });
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { ativo = Math.min(achados.length - 1, ativo + 1); mostrar(); e.preventDefault(); }
      else if (e.key === "ArrowUp") { ativo = Math.max(0, ativo - 1); mostrar(); e.preventDefault(); }
      else if (e.key === "Enter") {
        var p = achados[ativo >= 0 ? ativo : 0];
        if (p) location.href = p.u;
      } else if (e.key === "Escape") { input.value = ""; achados = []; mostrar(); }
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".busca")) lista.hidden = true;
    });
    input.addEventListener("focus", function () { if (input.value.trim()) mostrar(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== input) { e.preventDefault(); input.focus(); }
    });
  }

  // ---- menu no celular ----
  var menu = document.querySelector(".menu");
  if (menu) menu.addEventListener("click", function () { document.body.classList.toggle("menu-aberto"); });
  document.addEventListener("click", function (e) {
    if (document.body.classList.contains("menu-aberto") && !e.target.closest(".lateral") && !e.target.closest(".menu")) {
      document.body.classList.remove("menu-aberto");
    }
  });

  // ---- tema ----
  var tema = document.querySelector(".tema");
  if (tema) tema.addEventListener("click", function () {
    var root = document.documentElement;
    var escuro = root.dataset.theme ? root.dataset.theme === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.dataset.theme = escuro ? "light" : "dark";
    try { localStorage.setItem("wiki-tema", root.dataset.theme); } catch (e) { /* sem armazenamento */ }
  });

  // ---- página aleatória ----
  var al = document.getElementById("aleatoria");
  if (al) al.addEventListener("click", function (e) {
    e.preventDefault();
    if (IDX.length) location.href = IDX[Math.floor(Math.random() * IDX.length)].u;
  });

  // ---- tabelas ordenáveis ----
  function valor(td) {
    var t = td.textContent.trim();
    var d = td.querySelector(".dific");
    if (d) return parseFloat(d.title) || 0;
    var m = t.replace(/\./g, "").match(/^[$+−-]?\s*(\d+)/);
    if (m && /^[$+−\-\d]/.test(t)) return parseFloat(m[1]) * (/^[−-]/.test(t) ? -1 : 1);
    return semAcento(t);
  }
  document.querySelectorAll("table.ordenavel").forEach(function (tb) {
    var ths = tb.querySelectorAll("thead th");
    ths.forEach(function (th, col) {
      th.addEventListener("click", function () {
        var asc = !th.classList.contains("asc");
        ths.forEach(function (o) { o.classList.remove("asc", "desc"); });
        th.classList.add(asc ? "asc" : "desc");
        var body = tb.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        rows.sort(function (a, b) {
          var x = valor(a.cells[col]), y = valor(b.cells[col]);
          var r = (typeof x === "number" && typeof y === "number") ? x - y : String(x).localeCompare(String(y));
          return asc ? r : -r;
        });
        rows.forEach(function (r) { body.appendChild(r); });
      });
    });
  });
})();
