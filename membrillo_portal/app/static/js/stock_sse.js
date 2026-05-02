// Cliente SSE: escucha cambios de stock y actualiza badges en vivo
(function () {
  if (typeof window.EventSource === "undefined") return;

  const url = "/stream/stock";
  const es = new EventSource(url);
  const statusBadge = document.getElementById("sse-status");

  es.addEventListener("ready", () => {
    if (statusBadge) {
      statusBadge.innerHTML = '<span class="d-inline-block bg-success rounded-circle me-2" style="width:8px; height:8px;"></span> Stock en vivo conectado';
      statusBadge.style.background = "rgba(255,255,255,0.2)";
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
        // Detectar si el texto tiene formato "Stock: N" o solo "N unidades"
        if (el.textContent.includes("unidades")) {
            el.textContent = `${data.stock_total} unidades`;
        } else if (el.textContent.includes(":")) {
            el.textContent = `Stock: ${data.stock_total}`;
        } else {
            el.textContent = data.stock_total;
        }
        flash(el);
      });
    } catch (e) {
      console.error("SSE parse error", e);
    }
  });

  es.addEventListener("error", () => {
    if (statusBadge) {
      statusBadge.innerHTML = '<span class="d-inline-block bg-danger rounded-circle me-2" style="width:8px; height:8px;"></span> Stock en vivo desconectado';
      statusBadge.style.background = "rgba(220, 53, 69, 0.1)";
    }
  });

  function flash(el) {
    el.classList.add("stock-flash");
    setTimeout(() => el.classList.remove("stock-flash"), 600);
  }
})();
