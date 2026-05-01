from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class ProductoOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    imagen_url: Optional[str] = None
    tipo_nombre: str
    stock_total: int

    class Config:
        from_attributes = True


class StockSucursalOut(BaseModel):
    sucursal_id: int
    sucursal_nombre: str
    existencia: int


class StockEvent(BaseModel):
    producto_id: int
    sucursal_id: int
    existencia: int
    stock_total: int


class ItemCarrito(BaseModel):
    producto_id: int
    cantidad: int = Field(ge=1)


class CheckoutIn(BaseModel):
    nombre: str
    nit: str = "CF"
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    sucursal_id: int
    items: List[ItemCarrito]


class FacturaOut(BaseModel):
    id: int
    total: Decimal
    pdf_url: str
