/* El Membrillo — cliente de API + carrito (localStorage) para el e-commerce.
   Requiere config.js cargado antes. Expone window.Mem. */
(function () {
  const API = window.API_BASE || "http://localhost:8000/api";
  const TOKEN_KEY = "mem_token", USER_KEY = "mem_user", CART_KEY = "mem_cart";

  // ---------- sesión ----------
  function getToken() { return localStorage.getItem(TOKEN_KEY); }
  function getUser() { try { return JSON.parse(localStorage.getItem(USER_KEY) || "null"); } catch { return null; } }
  function setSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
  function clearSession() { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); }
  function logout(redirect) { clearSession(); window.location.href = redirect || "login.html"; }
  function requireAuth() {
    if (!getToken()) { window.location.href = "login.html?next=" + encodeURIComponent(location.pathname.split("/").pop()); return false; }
    return true;
  }

  // ---------- fetch ----------
  async function apiFetch(path, opts) {
    opts = opts || {};
    const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    const token = getToken();
    if (token) headers["Authorization"] = "Bearer " + token;
    const res = await fetch(API + path, {
      method: opts.method || "GET",
      headers,
      body: opts.body != null ? JSON.stringify(opts.body) : undefined,
    });
    let data = null;
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) data = await res.json().catch(() => null);
    if (!res.ok) {
      const msg = (data && (data.detail || data.error)) || ("HTTP " + res.status);
      const err = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
      err.status = res.status; err.data = data;
      throw err;
    }
    return data;
  }

  // ---------- carrito (localStorage) ----------
  function getCart() { try { return JSON.parse(localStorage.getItem(CART_KEY) || "[]"); } catch { return []; } }
  function saveCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); updateBadges(); }
  function cartCount() { return getCart().reduce((n, i) => n + i.cantidad, 0); }
  function addToCart(producto_id, cantidad) {
    cantidad = cantidad || 1;
    const c = getCart();
    const it = c.find((x) => x.producto_id === producto_id);
    if (it) it.cantidad += cantidad; else c.push({ producto_id, cantidad });
    saveCart(c);
  }
  function setQty(producto_id, cantidad) {
    let c = getCart();
    if (cantidad <= 0) c = c.filter((x) => x.producto_id !== producto_id);
    else { const it = c.find((x) => x.producto_id === producto_id); if (it) it.cantidad = cantidad; }
    saveCart(c);
  }
  function removeFromCart(producto_id) { saveCart(getCart().filter((x) => x.producto_id !== producto_id)); }
  function clearCart() { localStorage.removeItem(CART_KEY); updateBadges(); }

  function updateBadges() {
    const n = cartCount();
    document.querySelectorAll("[data-cart-count]").forEach((el) => { el.textContent = n; });
  }

  // utilidades
  function money(v) { return "Q" + Number(v).toLocaleString("es-GT", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  document.addEventListener("DOMContentLoaded", updateBadges);

  window.Mem = {
    API, apiFetch, getToken, getUser, setSession, clearSession, logout, requireAuth,
    getCart, saveCart, cartCount, addToCart, setQty, removeFromCart, clearCart, updateBadges, money,
  };
})();
