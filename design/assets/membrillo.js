/* El Membrillo — helpers de interacción compartidos */
(function () {
  // Ripple en cualquier elemento .ripple
  document.addEventListener("pointerdown", function (e) {
    const t = e.target.closest(".ripple");
    if (!t) return;
    const r = t.getBoundingClientRect();
    const s = document.createElement("span");
    s.className = "rip";
    const size = Math.max(r.width, r.height);
    s.style.width = s.style.height = size + "px";
    s.style.left = e.clientX - r.left - size / 2 + "px";
    s.style.top = e.clientY - r.top - size / 2 + "px";
    t.appendChild(s);
    setTimeout(() => s.remove(), 650);
  });

  // Toasts
  function toastWrap() {
    let w = document.querySelector(".toast-wrap");
    if (!w) { w = document.createElement("div"); w.className = "toast-wrap"; document.body.appendChild(w); }
    return w;
  }
  window.membrilloToast = function (opts) {
    opts = opts || {};
    const el = document.createElement("div");
    el.className = "toast " + (opts.type || "");
    const icon = opts.icon || (opts.type === "ok" ? "check_circle" : opts.type === "warn" ? "notifications_active" : "shopping_basket");
    const color = opts.type === "ok" ? "#4CAF50" : opts.type === "warn" ? "#FFA726" : "#8B0000";
    el.innerHTML =
      '<div style="background:' + color + '1f;color:' + color + ';width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex-shrink:0">' +
      '<span class="material-symbols-outlined">' + icon + '</span></div>' +
      '<div style="flex:1;min-width:0"><p style="font-weight:700;font-size:14px;color:#2C1810;margin:0">' + (opts.title || "") + '</p>' +
      (opts.body ? '<p style="font-size:12px;color:#6B5B4F;margin:2px 0 0">' + opts.body + '</p>' : "") + '</div>' +
      '<span class="material-symbols-outlined" style="color:#b9a79f;font-size:18px;cursor:pointer">close</span>';
    el.querySelector("span:last-child").onclick = () => dismiss(el);
    toastWrap().appendChild(el);
    const ttl = opts.ttl || 4200;
    setTimeout(() => dismiss(el), ttl);
    return el;
  };
  function dismiss(el) { if (!el) return; el.classList.add("leaving"); setTimeout(() => el.remove(), 350); }

  // Count-up
  window.countUp = function (el, to, opts) {
    opts = opts || {};
    const dur = opts.dur || 900;
    const dec = opts.dec || 0;
    const prefix = opts.prefix || "";
    const suffix = opts.suffix || "";
    const from = opts.from != null ? opts.from : 0;
    const start = performance.now();
    function frame(now) {
      const p = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      const val = from + (to - from) * eased;
      el.textContent = prefix + val.toLocaleString("es-GT", { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suffix;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  };

  // Confeti membrillo (vino, dorado, crema)
  window.membrilloConfetti = function (opts) {
    opts = opts || {};
    const N = opts.count || 120;
    const colors = ["#8B0000", "#D4A574", "#FFE082", "#610000", "#b52619", "#F5E6D3"];
    const cv = document.createElement("canvas");
    cv.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:200";
    document.body.appendChild(cv);
    const ctx = cv.getContext("2d");
    function size() { cv.width = innerWidth; cv.height = innerHeight; }
    size();
    const parts = [];
    for (let i = 0; i < N; i++) {
      parts.push({
        x: Math.random() * cv.width,
        y: -20 - Math.random() * cv.height * 0.4,
        r: 4 + Math.random() * 7,
        c: colors[(Math.random() * colors.length) | 0],
        vx: -1.5 + Math.random() * 3,
        vy: 2 + Math.random() * 3.5,
        rot: Math.random() * Math.PI,
        vr: -0.15 + Math.random() * 0.3,
        shape: Math.random() > 0.4 ? "rect" : "circ",
      });
    }
    let frames = 0;
    function tick() {
      ctx.clearRect(0, 0, cv.width, cv.height);
      parts.forEach((p) => {
        p.x += p.vx; p.y += p.vy; p.vy += 0.04; p.rot += p.vr;
        ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.fillStyle = p.c;
        if (p.shape === "rect") ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 1.6);
        else { ctx.beginPath(); ctx.arc(0, 0, p.r / 1.6, 0, 7); ctx.fill(); }
        ctx.restore();
      });
      frames++;
      if (frames < 220) requestAnimationFrame(tick);
      else cv.remove();
    }
    tick();
  };
})();
