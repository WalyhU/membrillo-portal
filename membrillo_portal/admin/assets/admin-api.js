/* El Membrillo — cliente de API del panel admin (token propio + SSE real). */
(function () {
  const API = window.API_BASE || "http://localhost:8000/api";
  const TK = "mem_admin_token", UK = "mem_admin_user";

  function token() { return localStorage.getItem(TK); }
  function user() { try { return JSON.parse(localStorage.getItem(UK) || "null"); } catch { return null; } }
  function setSession(t, u) { localStorage.setItem(TK, t); localStorage.setItem(UK, JSON.stringify(u)); }
  function logout() { localStorage.removeItem(TK); localStorage.removeItem(UK); window.location.href = "login.html"; }

  function requireAdmin() {
    const u = user();
    if (!token() || !u || u.rol !== "admin") { window.location.href = "login.html"; return false; }
    return true;
  }

  async function adminFetch(path, opts) {
    opts = opts || {};
    const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers || {});
    const t = token();
    if (t) headers["Authorization"] = "Bearer " + t;
    const res = await fetch(API + path, {
      method: opts.method || "GET", headers,
      body: opts.body != null ? JSON.stringify(opts.body) : undefined,
    });
    if (res.status === 401 || res.status === 403) { logout(); throw new Error("No autorizado"); }
    let data = null;
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) data = await res.json().catch(() => null);
    if (!res.ok) {
      const msg = (data && (data.detail || data.error)) || ("HTTP " + res.status);
      const err = new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
      err.status = res.status; err.data = data; throw err;
    }
    return data;
  }

  function money(v) { return "Q" + Number(v).toLocaleString("es-GT", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }

  // mapas id->nombre (públicos)
  let _maps = null;
  async function loadMaps() {
    if (_maps) return _maps;
    const [prods, sucs] = await Promise.all([
      fetch(API + "/productos").then((r) => r.json()).catch(() => []),
      fetch(API + "/sucursales").then((r) => r.json()).catch(() => []),
    ]);
    _maps = {
      prod: Object.fromEntries(prods.map((p) => [p.id, p.nombre])),
      suc: Object.fromEntries(sucs.map((s) => [s.id, s.nombre])),
    };
    return _maps;
  }

  // SSE compartido -> dispatch 'membrillo:stock'
  let _es = null;
  function connectSSE(onStatus) {
    if (_es) return _es;
    _es = new EventSource(API + "/stream/stock");
    _es.addEventListener("ready", () => onStatus && onStatus(true));
    _es.addEventListener("error", () => onStatus && onStatus(false));
    _es.addEventListener("stock_update", (ev) => {
      let d; try { d = JSON.parse(ev.data); } catch { return; }
      document.dispatchEvent(new CustomEvent("membrillo:stock", { detail: d }));
    });
    return _es;
  }

  window.AdminAPI = { API, token, user, setSession, logout, requireAdmin, adminFetch, money, loadMaps, connectSSE };
})();
