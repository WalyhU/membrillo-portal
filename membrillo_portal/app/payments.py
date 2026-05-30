"""Pasarela de pago SIMULADA (sin dinero real, sin red externa).

Valida tarjetas con el algoritmo de Luhn, detecta la marca por prefijo y
simula la aprobacion/rechazo. Pensado para demo academico.
"""
import random
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ResultadoValidacion:
    ok: bool
    error: Optional[str] = None
    marca: Optional[str] = None
    ult4: Optional[str] = None


def _solo_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def luhn_valido(numero: str) -> bool:
    digitos = [int(d) for d in _solo_digitos(numero)]
    if len(digitos) < 13:
        return False
    suma = 0
    par = False
    for d in reversed(digitos):
        if par:
            d *= 2
            if d > 9:
                d -= 9
        suma += d
        par = not par
    return suma % 10 == 0


def detectar_marca(numero: str) -> Optional[str]:
    n = _solo_digitos(numero)
    if n.startswith("4"):
        return "Visa"
    if re.match(r"^(5[1-5]|2[2-7])", n):
        return "Mastercard"
    if re.match(r"^3[47]", n):
        return "Amex"
    if n.startswith("6"):
        return "Discover"
    return None


def _expiracion_valida(expiracion: str) -> bool:
    """Formato MM/AA o MM/AAAA, no vencida."""
    m = re.match(r"^\s*(\d{1,2})\s*/\s*(\d{2,4})\s*$", expiracion or "")
    if not m:
        return False
    mes = int(m.group(1))
    anio = int(m.group(2))
    if anio < 100:
        anio += 2000
    if mes < 1 or mes > 12:
        return False
    ahora = datetime.utcnow()
    # vence al final del mes indicado
    return (anio, mes) >= (ahora.year, ahora.month)


def validar_tarjeta(numero: str, expiracion: str, cvv: str) -> ResultadoValidacion:
    n = _solo_digitos(numero)
    if not luhn_valido(n):
        return ResultadoValidacion(False, "Numero de tarjeta invalido (no pasa validacion Luhn).")
    marca = detectar_marca(n)
    if marca is None:
        return ResultadoValidacion(False, "Marca de tarjeta no reconocida.")
    if not _expiracion_valida(expiracion):
        return ResultadoValidacion(False, "Fecha de expiracion invalida o vencida.")
    cvv_len = 4 if marca == "Amex" else 3
    if not re.match(rf"^\d{{{cvv_len}}}$", _solo_digitos(cvv)):
        return ResultadoValidacion(False, f"CVV invalido (se esperan {cvv_len} digitos).")
    return ResultadoValidacion(True, marca=marca, ult4=n[-4:])


def procesar_pago(validacion: ResultadoValidacion, tasa_aprobacion: float = 0.9) -> bool:
    """Simula el procesamiento: aprueba con la probabilidad dada.

    Regla de demo: la tarjeta de prueba 4111 1111 1111 1111 siempre aprueba
    (se maneja en la ruta). Aqui solo el azar del 'banco'.
    """
    return random.random() < tasa_aprobacion
