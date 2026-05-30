/* El Membrillo — Admin shell compartido.
   Cada página admin define en <body data-page="dashboard" data-title="...">.
   Requiere contenedores #admin-sidebar y #admin-topbar en el HTML. */
(function () {
  const page = document.body.dataset.page || "dashboard";
  const title = document.body.dataset.title || "";
  const eyebrow = document.body.dataset.eyebrow || "Administración";

  const items = [
    { key: "dashboard", label: "Dashboard", icon: "dashboard", href: "dashboard.html" },
    { key: "inventario", label: "Inventario", icon: "inventory_2", href: "inventario.html" },
    { key: "productos", label: "Productos", icon: "category", href: "productos.html" },
    { key: "pedidos", label: "Pedidos", icon: "receipt_long", href: "pedidos.html" },
    { key: "usuarios", label: "Usuarios", icon: "group", href: "usuarios.html" },
  ];

  // ---------- Sidebar ----------
  const aside = document.getElementById("admin-sidebar");
  if (aside) {
    aside.innerHTML =
      '<div class="flex flex-col h-full">' +
        '<div class="px-6 pt-7 pb-6">' +
          '<div class="flex items-center gap-3">' +
            '<div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shrink-0">' +
              '<span class="material-symbols-outlined text-gold ms-fill">local_florist</span></div>' +
            '<div><p class="font-display text-lg leading-none text-[#FFE7DE]">El Membrillo</p>' +
            '<p class="eyebrow text-gold/80 mt-1" style="font-size:9px">Admin Console</p></div>' +
          '</div>' +
          '<div class="mt-5 flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5">' +
            '<span class="dot-pulse w-2 h-2 rounded-full bg-success-green text-success-green inline-block"></span>' +
            '<span class="text-[11px] text-[#E9D9CF] font-medium tracking-wide">SSE conectado</span>' +
            '<span class="ml-auto text-[10px] text-[#9c8678]">tiempo real</span>' +
          '</div>' +
        '</div>' +
        '<nav class="px-3 flex-1 space-y-1">' +
          items.map(function (it) {
            const active = it.key === page;
            return '<a href="' + it.href + '" class="admin-nav-item ' + (active ? "active" : "") +
              ' flex items-center gap-3 px-3 py-2.5 rounded-xl ' + (active ? "" : "text-[#D9C6BA]") + '">' +
              '<span class="material-symbols-outlined ' + (active ? "ms-fill" : "text-gold") + '" style="font-size:21px">' + it.icon + '</span>' +
              '<span class="text-sm font-medium">' + it.label + '</span>' +
              (active ? '<span class="ml-auto w-1.5 h-1.5 rounded-full bg-gold"></span>' : "") +
              '</a>';
          }).join("") +
        '</nav>' +
        '<div class="px-3 pb-5 pt-3 mt-2 border-t border-white/8">' +
          '<div class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 cursor-pointer transition">' +
            '<div class="w-9 h-9 rounded-full bg-gold/90 flex items-center justify-center text-sidebar font-bold text-sm shrink-0">SG</div>' +
            '<div class="min-w-0"><p class="text-sm text-[#F2E5DC] font-medium truncate">Sofía Guzmán</p>' +
            '<p class="text-[10px] text-[#9c8678]">Administradora</p></div>' +
            '<span class="material-symbols-outlined ml-auto text-[#9c8678]" style="font-size:18px">logout</span>' +
          '</div>' +
          '<p class="text-[10px] text-[#7c6557] px-3 mt-3">v2.0 · © 1962 El Membrillo</p>' +
        '</div>' +
      '</div>';
  }

  // ---------- Topbar ----------
  const top = document.getElementById("admin-topbar");
  if (top) {
    top.innerHTML =
      '<div class="flex items-center gap-4">' +
        '<button id="admin-burger" class="lg:hidden w-10 h-10 rounded-xl bg-card-cream flex items-center justify-center text-primary">' +
          '<span class="material-symbols-outlined">menu</span></button>' +
        '<div><p class="eyebrow text-primary">' + eyebrow + '</p>' +
        '<h1 class="font-display text-2xl md:text-3xl text-text-dark leading-tight">' + title + '</h1></div>' +
      '</div>' +
      '<div class="flex items-center gap-2 md:gap-3">' +
        '<div class="hidden md:flex items-center gap-2 bg-white rounded-full pl-3 pr-1 py-1 border border-outline-variant/40">' +
          '<span class="material-symbols-outlined text-text-muted" style="font-size:19px">search</span>' +
          '<input placeholder="Buscar…" class="bg-transparent text-sm w-32 focus:w-44 transition-all outline-none placeholder:text-text-muted/70"/>' +
        '</div>' +
        '<button class="relative w-10 h-10 rounded-full bg-white border border-outline-variant/40 flex items-center justify-center text-primary lift">' +
          '<span class="material-symbols-outlined" style="font-size:20px">notifications</span>' +
          '<span class="absolute top-1.5 right-2 w-2 h-2 rounded-full bg-error-red"></span></button>' +
        '<a href="../index.html" class="w-10 h-10 rounded-full bg-white border border-outline-variant/40 flex items-center justify-center text-primary lift" title="Salir al hub">' +
          '<span class="material-symbols-outlined" style="font-size:20px">grid_view</span></a>' +
      '</div>';
  }

  // ---------- Drawer móvil ----------
  function bindBurger() {
    const b = document.getElementById("admin-burger");
    const sb = document.getElementById("admin-sidebar");
    const ov = document.getElementById("admin-overlay");
    if (!b || !sb) return;
    b.addEventListener("click", function () {
      sb.classList.toggle("-translate-x-full");
      if (ov) ov.classList.toggle("hidden");
    });
    if (ov) ov.addEventListener("click", function () {
      sb.classList.add("-translate-x-full");
      ov.classList.add("hidden");
    });
  }
  bindBurger();

  // ---------- Simulación SSE: nuevas ventas ----------
  const sucursales = ["Guatemala", "Quetzaltenango", "Mazatenango", "Escuintla", "Puerto Barrios", "Jutiapa"];
  const productos = ["Jalea de Membrillo", "Mermelada de Naranja", "Membrillo en Barra", "Pack Regalo Trío", "Dúo de Jaleas"];
  function emitSale() {
    const suc = sucursales[(Math.random() * sucursales.length) | 0];
    const prod = productos[(Math.random() * productos.length) | 0];
    const qty = 1 + ((Math.random() * 3) | 0);
    const total = (qty * (45 + Math.random() * 40)).toFixed(2);
    const evt = { sucursal: suc, producto: prod, qty: qty, total: total };
    if (window.membrilloToast) {
      window.membrilloToast({ type: "ok", icon: "shopping_basket", title: "Nueva venta · " + suc, body: qty + "× " + prod + " · Q" + total });
    }
    document.dispatchEvent(new CustomEvent("membrillo:sale", { detail: evt }));
  }
  // primera venta a los 4.5s, luego cada 11–17s
  let t = setTimeout(function loop() {
    emitSale();
    t = setTimeout(loop, 11000 + Math.random() * 6000);
  }, 4500);
  window.addEventListener("beforeunload", () => clearTimeout(t));
})();
