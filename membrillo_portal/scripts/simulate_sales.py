"""Simulador: genera ventas concurrentes contra el portal para demo SSE en vivo.
Uso: python scripts/simulate_sales.py [--url http://localhost:8000] [--n 30] [--delay 1.5]
"""
import argparse
import random
import sys
import time
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Falta 'requests'. Instala: pip install requests")
    sys.exit(1)


NOMBRES = [
    "Maria Lopez", "Juan Perez", "Ana Garcia", "Luis Morales", "Carmen Ruiz",
    "Pedro Castillo", "Sofia Hernandez", "Diego Ramirez", "Lucia Torres", "Carlos Mendez",
]


def simular(url: str, n: int, delay: float) -> None:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    productos = s.get(urljoin(url, "/api/productos")).json()
    if not productos:
        print("No hay productos. Verifica BD.")
        return

    print(f"Simulando {n} ventas contra {url}/api ...")
    for i in range(1, n + 1):
        cliente = random.choice(NOMBRES)
        sucursal = random.randint(1, 6)
        items = []
        for _ in range(random.randint(1, 3)):
            prod = random.choice(productos)
            items.append({"producto_id": prod["id"], "cantidad": random.randint(1, 4)})
        try:
            # 1) checkout -> crea factura PENDIENTE + reserva stock
            r = s.post(urljoin(url, "/api/checkout"), json={
                "nombre": cliente, "nit": "CF", "sucursal_id": sucursal, "items": items,
            })
            if r.status_code != 200:
                print(f"  [{i}/{n}] {cliente} -> sucursal {sucursal} -> checkout HTTP {r.status_code} (sin stock?)")
                time.sleep(delay)
                continue
            fid = r.json()["factura_id"]
            # 2) pago con tarjeta de prueba (siempre aprueba) -> confirma reserva y baja stock
            rp = s.post(urljoin(url, f"/api/pago/{fid}"), json={
                "metodo": "tarjeta", "numero": "4111111111111111",
                "titular": cliente.upper(), "expiracion": "12/29", "cvv": "123",
            })
            estado = rp.json().get("estado", rp.status_code) if rp.content else rp.status_code
            print(f"  [{i}/{n}] {cliente} -> sucursal {sucursal} -> factura {fid} -> {estado}")
        except Exception as e:
            print(f"  err venta: {e}")

        time.sleep(delay)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--delay", type=float, default=1.5)
    args = ap.parse_args()
    simular(args.url, args.n, args.delay)
