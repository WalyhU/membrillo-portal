"""Generador PDF factura con reportlab."""
import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)

from . import models

FACTURAS_DIR = Path(__file__).parent / "static" / "facturas"
FACTURAS_DIR.mkdir(parents=True, exist_ok=True)


def generar_factura_pdf(factura: models.Factura) -> str:
    filename = FACTURAS_DIR / f"factura_{factura.id:06d}.pdf"
    doc = SimpleDocTemplate(
        str(filename),
        pagesize=LETTER,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"], textColor=colors.HexColor("#8B0000"),
        alignment=1, fontSize=20, spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"], alignment=1, fontSize=10, textColor=colors.grey
    )

    story = []
    story.append(Paragraph("El Membrillo - Jaleas Artesanales S.A.", title_style))
    story.append(Paragraph("San Francisco El Alto, Sacatepequez | NIT 1234567-8", sub_style))
    story.append(Spacer(1, 0.5 * cm))

    info = [
        ["Factura No.", f"{factura.id:06d}"],
        ["Fecha", factura.fecha.strftime("%d/%m/%Y %H:%M")],
        ["Cliente", factura.cliente.nombre],
        ["NIT", factura.cliente.nit or "CF"],
        ["Sucursal", factura.sucursal.nombre],
    ]
    info_table = Table(info, colWidths=[4 * cm, 12 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#FFF5F5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.7 * cm))

    data = [["#", "Producto", "Cant.", "Precio", "Subtotal"]]
    for i, det in enumerate(factura.detalles, 1):
        data.append([
            str(i),
            det.producto.nombre,
            str(det.cantidad),
            f"Q {det.precio_unit:.2f}",
            f"Q {det.subtotal:.2f}",
        ])

    detalle_table = Table(data, colWidths=[1 * cm, 9 * cm, 2 * cm, 2.5 * cm, 2.5 * cm])
    detalle_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8B0000")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
    ]))
    story.append(detalle_table)
    story.append(Spacer(1, 0.5 * cm))

    totales = [
        ["Subtotal", f"Q {factura.subtotal:.2f}"],
        ["IVA (12%)", f"Q {factura.iva:.2f}"],
        ["TOTAL", f"Q {factura.total:.2f}"],
    ]
    tot_table = Table(totales, colWidths=[12 * cm, 5 * cm])
    tot_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#8B0000")),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#8B0000")),
    ]))
    story.append(tot_table)
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        "Gracias por su compra. Producto artesanal sin preservantes.",
        ParagraphStyle("Foot", parent=styles["Normal"], alignment=1, fontSize=9, textColor=colors.grey),
    ))

    doc.build(story)
    return str(filename)
