// Cliente SSE: escucha cambios de stock y actualiza badges en vivo
(function () {
  if (typeof window.EventSource === "undefined") return;

  const url = "/stream/stock";
  const es = new EventSource(url);
  const statusBadge = document.getElementById("sse-status");

  es.addEventListener("ready", () => {
    if (statusBadge) {
      statusBadge.textContent = "Stock en vivo conectado";
      statusBadge.classList.remove("bg-warning");
      statusBadge.classList.add("bg-success");
    }
  });

  es.addEventListener("stock_update", (ev) => {
    try {
      const data = JSON.parse(ev.data);
      // Stock por sucursal
      const elem = document.querySelector(`[data-stock="${data.producto_id}-${data.sucursal_id}"]`);
      if (elem) {
        elem.textContent = data.existencia;
        flash(elem);
      }
      // Stock total
      const total = document.querySelectorAll(`[data-stock-total="${data.producto_id}"]`);
      total.forEach((el) => {
        const txt = el.textContent.includes(":") ? `Stock: ${data.stock_total}` : data.stock_total;
        el.textContent = txt;
        flash(el);
      });
    } catch (e) {
      console.error("SSE parse error", e);
    }
  });

  es.addEventListener("error", () => {
    if (statusBadge) {
      statusBadge.textContent = "Stock en vivo desconectado";
      statusBadge.classList.remove("bg-success");
      statusBadge.classList.add("bg-danger");
    }
  });

  function flash(el) {
    el.classList.add("stock-flash");
    setTimeout(() => el.classList.remove("stock-flash"), 600);
  }
})();
