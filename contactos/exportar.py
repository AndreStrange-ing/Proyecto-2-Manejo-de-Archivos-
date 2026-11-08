import json
import os
from datetime import datetime

from contactos.archivo import carpeta, recorrer

ruta_json = os.path.join(carpeta, "contactos_export.json")


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
