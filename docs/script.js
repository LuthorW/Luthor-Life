// Luthor Life — interações do site
(function () {
  "use strict";

  // ---------------------------------------------------------------- personagens
  const PEOPLE = [
    ["leticia", "Letícia Luthor", "CEO da Luthor Corp · você", "team"],
    ["sam", "Samantha Arias", "CFO", "team"],
    ["brainy", "Querl Dox", "CTO", "team"],
    ["jess", "Jess", "Assistente executiva", "team"],
    ["lucy", "Lucy Williams", "Repórter da CatCo", "romance"],
    ["vittoria", "Vittoria Ricci", "Chef da Ricci Trattoria", "romance"],
    ["rafa", "Rafa", "Barista do Grão Nobre", "city"],
    ["nia", "Nia Nal", "Repórter da CatCo", "city"],
    ["theo", "Theo", "Livreiro da Bayside Books", "city"],
    ["bea", "Bea", "Dona do Mercado Central", "city"],
    ["marco", "Marco", "Barman do Noonan's", "city"],
    ["joca", "Seu Joca", "Pescador do píer", "city"],
    ["milany", "Dra. Milany Moretti", "Centro Cardiovascular", "doc"],
    ["yang", "Dra. Cristina Yang", "Direção Médica", "doc"],
    ["meredith", "Dra. Meredith Grey", "Direção Médica", "doc"],
    ["lexie", "Dra. Lexie Grey", "Neurociências", "doc"],
    ["izzie", "Dra. Izzie Stevens", "Oncologia", "doc"],
    ["addison", "Dra. Addison Montgomery", "Materno-Infantil", "doc"],
  ];

  const people = document.getElementById("people");
  if (people) {
    people.innerHTML = PEOPLE.map(([k, name, role, grp]) =>
      `<article class="person ${grp === "romance" ? "romance" : ""} ${grp === "doc" ? "doc" : ""}" data-g="${grp}">
         <div class="sprite"><img src="img/chars/${k}.png" alt="Sprite de ${name}" loading="lazy"></div>
         <h4>${name}</h4><span>${role}</span>
       </article>`).join("");
  }
  document.querySelectorAll(".tabs button").forEach((b) => {
    b.addEventListener("click", () => {
      document.querySelectorAll(".tabs button").forEach((x) => x.setAttribute("aria-selected", x === b));
      const f = b.dataset.f;
      document.querySelectorAll(".person").forEach((p) => { p.hidden = !(f === "all" || p.dataset.g === f); });
    });
  });

  // ---------------------------------------------------------------- desfile de sprites
  const track = document.querySelector(".parade .track");
  if (track) {
    const order = ["leticia", "lucy", "cat", "sam", "brainy", "vittoria", "jess", "milany", "rafa", "nia", "dog",
      "theo", "yang", "bea", "meredith", "marco", "lexie", "joca", "izzie", "addison"];
    const html = order.map((k) =>
      `<img class="${k === "cat" || k === "dog" ? "pet" : ""}" src="img/chars/${k}.png" alt="">`).join("");
    track.innerHTML = html + html;
  }

  // ---------------------------------------------------------------- galeria
  const SHOTS = [
    ["city", "O calçadão Bayside numa manhã movimentada", true],
    ["park", "Parque central com chafariz e lago"],
    ["beach", "A orla no fim de tarde"],
    ["fishing", "Peixe mordendo no píer!"],
    ["terrace", "Terraço com horta e o gato Kiwi"],
    ["lab", "Laboratório da Luthor Corp"],
    ["dialog", "Conversa com a Vittoria na Trattoria"],
    ["karaoke", "Karaokê no Noonan's"],
    ["movie", "Sessão no Cine National"],
    ["hospital", "Conti Moretti Hospitais"],
    ["cutscene", "Cutscene no píer à noite"],
    ["relationships", "Relacionamentos e corações"],
  ];
  const gallery = document.getElementById("gallery");
  if (gallery) {
    gallery.innerHTML = SHOTS.map(([f, cap, wide], i) =>
      `<button type="button" class="${wide ? "wide" : ""}" data-i="${i}">
         <img src="img/${f}.png" alt="${cap}" loading="lazy"><span>${cap}</span></button>`).join("");
  }
  const lb = document.getElementById("lightbox");
  let cur = 0;
  function show(i) {
    cur = (i + SHOTS.length) % SHOTS.length;
    lb.querySelector("img").src = `img/${SHOTS[cur][0]}.png`;
    lb.querySelector("img").alt = SHOTS[cur][1];
    lb.querySelector("p").textContent = SHOTS[cur][1];
  }
  function open(i) { show(i); lb.classList.add("open"); lb.querySelector(".x").focus(); }
  function close() { lb.classList.remove("open"); }
  if (gallery && lb) {
    gallery.addEventListener("click", (e) => {
      const b = e.target.closest("button[data-i]");
      if (b) open(+b.dataset.i);
    });
    lb.querySelector(".x").addEventListener("click", close);
    lb.querySelector(".nav-l").addEventListener("click", () => show(cur - 1));
    lb.querySelector(".nav-r").addEventListener("click", () => show(cur + 1));
    lb.addEventListener("click", (e) => { if (e.target === lb) close(); });
    document.addEventListener("keydown", (e) => {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
    });
  }

  // ---------------------------------------------------------------- copiar comandos
  document.querySelectorAll(".code button").forEach((b) => {
    b.addEventListener("click", async () => {
      const txt = b.parentElement.querySelector("code").textContent;
      try { await navigator.clipboard.writeText(txt); } catch (e) { /* sem permissão: ignora */ }
      b.textContent = "copiado!";
      b.classList.add("ok");
      setTimeout(() => { b.textContent = "copiar"; b.classList.remove("ok"); }, 1600);
    });
  });

  // ---------------------------------------------------------------- menu no celular
  const menuBtn = document.querySelector(".menu-btn");
  const menu = document.getElementById("menu");
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", () => {
      const openNow = menu.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", openNow);
    });
    menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => menu.classList.remove("open")));
  }

  // ---------------------------------------------------------------- título e marca animados
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll(".brand span").forEach((el) => {
    const t = el.textContent;
    el.setAttribute("aria-label", t);
    el.innerHTML = [...t].map((ch, i) =>
      `<span class="bl" aria-hidden="true" style="--i:${i}">${ch === " " ? "&nbsp;" : ch}</span>`).join("");
  });

  const h1 = document.querySelector(".hero h1");
  if (h1) {
    const words = h1.innerHTML.split(/<br\s*\/?>/i).map((w) => w.trim());
    h1.setAttribute("aria-label", words.join(" "));
    let n = 0;
    h1.innerHTML = words.map((w, wi) =>
      `<span class="word w${wi + 1}" aria-hidden="true">` +
      [...w].map((ch) => `<span class="l" style="--i:${n++}"><span class="c" style="--i:${n}">${ch}</span></span>`).join("") +
      `</span>`).join("");
    h1.classList.add("anim");

    // letra pula e fica verde ao passar o mouse; clique faz girar
    h1.querySelectorAll(".c").forEach((c) => {
      c.addEventListener("mouseenter", () => {
        c.classList.remove("hop"); void c.offsetWidth; c.classList.add("hop");
      });
      c.addEventListener("animationend", (e) => {
        if (e.animationName === "hop") c.classList.remove("hop");
        if (e.animationName === "spin360") c.classList.remove("spin");
      });
      c.addEventListener("click", () => { c.classList.remove("spin"); void c.offsetWidth; c.classList.add("spin"); });
    });

    // faíscas roxas e verdes surgindo em volta do título
    if (!reduce) {
      const colors = ["#dfc5ff", "#b84cff", "#6ee78c", "#ffffff"];
      setInterval(() => {
        if (document.hidden) return;
        const r = h1.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight) return;
        const s = document.createElement("span");
        s.className = "spark";
        s.style.left = Math.random() * (r.width + 30) - 15 + "px";
        s.style.top = Math.random() * (r.height + 20) - 10 + "px";
        s.style.setProperty("--c", colors[(Math.random() * colors.length) | 0]);
        h1.appendChild(s);
        setTimeout(() => s.remove(), 1200);
      }, 450);
    }
  }

  // ---------------------------------------------------------------- entrada suave
  const els = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.12 });
    els.forEach((el) => io.observe(el));
  } else {
    els.forEach((el) => el.classList.add("in"));
  }
})();
