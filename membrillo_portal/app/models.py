from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DECIMAL, ForeignKey, TIMESTAMP, DateTime, Enum, UniqueConstraint, SmallInteger
)
from sqlalchemy.orm import relationship
from .db import Base


class TipoProducto(Base):
    __tablename__ = "tipo_producto"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)
    descripcion = Column(String(255))
    productos = relationship("Producto", back_populates="tipo")


class Producto(Base):
    __tablename__ = "producto"
    id = Column(Integer, primary_key=True)
    tipo_id = Column(Integer, ForeignKey("tipo_producto.id"), nullable=False)
    nombre = Column(String(120), nullable=False)
    descripcion = Column(Text)
    precio = Column(DECIMAL(10, 2), nullable=False)
    imagen_url = Column(String(255))
    activo = Column(SmallInteger, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    tipo = relationship("TipoProducto", back_populates="productos")
    stocks = relationship("StockSucursal", back_populates="producto", cascade="all, delete-orphan")


class Sucursal(Base):
    __tablename__ = "sucursal"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)
    direccion = Column(String(255))
    telefono = Column(String(30))
    stocks = relationship("StockSucursal", back_populates="sucursal", cascade="all, delete-orphan")


class StockSucursal(Base):
    __tablename__ = "stock_sucursal"
    __table_args__ = (UniqueConstraint("producto_id", "sucursal_id", name="uk_producto_sucursal"),)
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("producto.id", ondelete="CASCADE"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursal.id", ondelete="CASCADE"), nullable=False)
    existencia = Column(Integer, default=0, nullable=False)
    reservado = Column(Integer, default=0, nullable=False)
    producto = relationship("Producto", back_populates="stocks")
    sucursal = relationship("Sucursal", back_populates="stocks")

    @property
    def disponible(self) -> int:
        return max(0, (self.existencia or 0) - (self.reservado or 0))


class Cliente(Base):
    __tablename__ = "cliente"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    nit = Column(String(20), default="CF")
    email = Column(String(120))
    telefono = Column(String(30))
    direccion = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(Enum("admin", "cliente"), default="cliente", nullable=False)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=True)
    activo = Column(SmallInteger, default=1, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    cliente = relationship("Cliente")


class Factura(Base):
    __tablename__ = "factura"
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursal.id"), nullable=False)
    fecha = Column(TIMESTAMP, default=datetime.utcnow)
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    iva = Column(DECIMAL(12, 2), nullable=False)
    total = Column(DECIMAL(12, 2), nullable=False)
    estado = Column(Enum("pendiente", "pagada", "anulada"), default="pendiente", nullable=False)
    cliente = relationship("Cliente")
    sucursal = relationship("Sucursal")
    detalles = relationship("DetalleFactura", back_populates="factura", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="factura", cascade="all, delete-orphan")
    reservas = relationship("Reserva", back_populates="factura", cascade="all, delete-orphan")


class DetalleFactura(Base):
    __tablename__ = "detalle_factura"
    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey("factura.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unit = Column(DECIMAL(10, 2), nullable=False)
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("Producto")


class Pago(Base):
    __tablename__ = "pago"
    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey("factura.id", ondelete="CASCADE"), nullable=False)
    metodo = Column(Enum("tarjeta", "contra_entrega"), default="tarjeta", nullable=False)
    ult4 = Column(String(4))
    marca = Column(String(20))
    estado = Column(Enum("pendiente", "procesando", "aprobado", "rechazado"), default="pendiente", nullable=False)
    monto = Column(DECIMAL(12, 2), nullable=False)
    detalle = Column(String(255))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    factura = relationship("Factura", back_populates="pagos")


class Reserva(Base):
    __tablename__ = "reserva"
    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey("factura.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursal.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    estado = Column(Enum("activa", "confirmada", "liberada"), default="activa", nullable=False)
    expira_en = Column(DateTime, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    factura = relationship("Factura", back_populates="reservas")
    producto = relationship("Producto")
    sucursal = relationship("Sucursal")
