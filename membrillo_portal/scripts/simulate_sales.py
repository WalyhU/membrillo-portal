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
    productos = s.get(urljoin(url, "/api/productos")).json()
    if not productos:
        print("No hay productos. Verifica BD.")
        return

    print(f"Simulando {n} ventas contra {url} ...")
    for i in range(1, n + 1):
        s.cookies.clear()
        # 1-3 items
        for _ in range(random.randint(1, 3)):
            prod = random.choice(productos)
            cant = random.randint(1, 4)
            try:
                s.post(urljoin(url, "/carrito/agregar"), data={"producto_id": prod["id"], "cantidad": cant}, allow_redirects=False)
            except Exception as e:
                print(f"  err agregar: {e}")

        cliente = random.choice(NOMBRES)
        sucursal = random.randint(1, 6)
        try:
            r = s.post(urljoin(url, "/checkout"), data={
                "nombre": cliente,
                "nit": "CF",
                "sucursal_id": sucursal,
            }, allow_redirects=False)
            print(f"  [{i}/{n}] {cliente} -> sucursal {sucursal} -> HTTP {r.status_code}")
        except Exception as e:
            print(f"  err checkout: {e}")

        time.sleep(delay)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--delay", type=float, default=1.5)
    args = ap.parse_args()
    simular(args.url, args.n, args.delay)
