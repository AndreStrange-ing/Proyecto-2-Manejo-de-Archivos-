import json
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from contactos.archivo import carpeta, recorrer

ruta_json = os.path.join(carpeta, "contactos_export.json")
ruta_pdf = os.path.join(carpeta, "reporte_contactos.pdf")

COLUMNAS = (("registro", "Registro", 55), ("id", "ID", 40), ("nombre", "Nombre", 125),
            ("telefono", "Teléfono", 75), ("correo", "Correo", 145), ("ciudad", "Ciudad", 90))


# guarda todos los contactos activos, el registro queda anotado para poder ubicarlos
def a_json():
    contactos = [dict(contacto, registro=numero) for numero, contacto in recorrer()]
    datos = {"generado": datetime.now().strftime("%d/%m/%Y %H:%M"),
             "total": len(contactos),
             "contactos": contactos}

    os.makedirs(carpeta, exist_ok=True)
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    return ruta_json, len(contactos)


# el reporte se arma con el json exportado, no vuelve a leer contactos.dat
def a_pdf():
    with open(ruta_json, "r", encoding="utf-8") as f:
        datos = json.load(f)

    estilos = getSampleStyleSheet()
    filas = [[titulo for _, titulo, _ in COLUMNAS]]
    for contacto in datos["contactos"]:
        filas.append([str(contacto[campo]) for campo, _, _ in COLUMNAS])

    tabla = Table(filas, colWidths=[ancho for _, _, ancho in COLUMNAS], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9e2f3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    documento = SimpleDocTemplate(ruta_pdf, pagesize=letter, title="Reporte de contactos")
    documento.build([
        Paragraph("Agenda de Contactos", estilos["Title"]),
        Paragraph(f"Generado el {datos['generado']} - {datos['total']} contactos", estilos["Normal"]),
        Spacer(1, 14),
        tabla,
    ])
    return ruta_pdf, datos["total"]
