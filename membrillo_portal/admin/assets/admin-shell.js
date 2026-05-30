/* El Membrillo — Admin shell compartido.
   Cada página admin define <body data-page="..." data-title="..." data-eyebrow="...">
   y contiene #admin-sidebar y #admin-topbar. Requiere admin-api.js cargado antes. */
(function () {
  // Guard de acceso
  if (window.AdminAPI && !AdminAPI.requireAdmin()) return;
  const me = (window.AdminAPI && AdminAPI.user()) || { nombre: "Administrador", rol: "admin" };
  const iniciales = me.nombre.split(" ").map((x) => x[0]).join("").slice(0, 2).toUpperCase();

  const page = document.body.dataset.page || "dashboard";
  const title = document.body.dataset.title || "";
  const eyebrow = document.body.dataset.eyebrow || "Administración";

  const items = [
    { key: "dashboard", label: "Dashboard", icon: "dashboard", href: "index.html" },
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
            '<span id="sse-dot" class="dot-pulse w-2 h-2 rounded-full bg-warning-amber text-warning-amber inline-block"></span>' +
            '<span id="sse-label" class="text-[11px] text-[#E9D9CF] font-medium tracking-wide">conectando…</span>' +
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
          '<div id="userChip" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 cursor-pointer transition">' +
            '<div class="w-9 h-9 rounded-full bg-gold/90 flex items-center justify-center text-sidebar font-bold text-sm shrink-0">' + iniciales + '</div>' +
            '<div class="min-w-0"><p class="text-sm text-[#F2E5DC] font-medium truncate">' + me.nombre + '</p>' +
            '<p class="text-[10px] text-[#9c8678]">Administrador</p></div>' +
            '<span class="material-symbols-outlined ml-auto text-[#9c8678]" style="font-size:18px" title="Cerrar sesión">logout</span>' +
          '</div>' +
        '</div>' +
      '</div>';
    document.getElementById("userChip").addEventListener("click", () => window.AdminAPI && AdminAPI.logout());
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
        '<button id="logoutBtn" class="flex items-center gap-2 px-4 h-10 rounded-full bg-white border border-outline-variant/40 text-primary lift text-sm font-medium">' +
          '<span class="material-symbols-outlined" style="font-size:19px">logout</span>Salir</button>' +
      '</div>';
    document.getElementById("logoutBtn").addEventListener("click", () => window.AdminAPI && AdminAPI.logout());
  }

  // ---------- Drawer móvil ----------
  (function bindBurger() {
    const b = document.getElementById("admin-burger");
    const sb = document.getElementById("admin-sidebar");
    const ov = document.getElementById("admin-overlay");
    if (!b || !sb) return;
    b.addEventListener("click", () => { sb.classList.toggle("-translate-x-full"); if (ov) ov.classList.toggle("hidden"); });
    if (ov) ov.addEventListener("click", () => { sb.classList.add("-translate-x-full"); ov.classList.add("hidden"); });
  })();

  // ---------- SSE real ----------
  if (window.AdminAPI) {
    AdminAPI.loadMaps().finally(() => {
      AdminAPI.connectSSE((ok) => {
        const dot = document.getElementById("sse-dot"), label = document.getElementById("sse-label");
        if (!dot) return;
        dot.className = "dot-pulse w-2 h-2 rounded-full inline-block " + (ok ? "bg-success-green text-success-green" : "bg-error-red text-error-red");
        label.textContent = ok ? "SSE conectado" : "reconectando…";
      });
    });
  }
})();
