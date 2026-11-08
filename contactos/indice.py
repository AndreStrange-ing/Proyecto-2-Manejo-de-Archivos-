import json
import os

from contactos.archivo import carpeta, recorrer

ruta_indice = os.path.join(carpeta, "indice.json")
ruta_tmp = os.path.join(carpeta, "indice.tmp")


# recorre el .dat completo, solo se usa si el indice se perdio o quedo dañado
def reconstruir():
    return {contacto["id"]: numero for numero, contacto in recorrer()}


# devuelve (indice, aviso), las claves del json son texto y aqui se pasan a entero
def cargar():
    try:
        with open(ruta_indice, "r", encoding="utf-8") as f:
            datos = json.load(f)
        return {int(id_): int(numero) for id_, numero in datos.items()}, None
    except FileNotFoundError:
        return reconstruir(), "No existe indice.json, se reconstruyó leyendo contactos.dat."
    except (ValueError, AttributeError):
        return reconstruir(), "indice.json está dañado, se reconstruyó leyendo contactos.dat."
    except OSError as e:
        return reconstruir(), f"No se pudo leer indice.json ({e}), se reconstruyó desde contactos.dat."


# se escribe primero el tmp y luego se reemplaza, igual que en el laboratorio 1
def guardar(indice):
    try:
        os.makedirs(carpeta, exist_ok=True)
        with open(ruta_tmp, "w", encoding="utf-8") as f:
            json.dump(indice, f, ensure_ascii=False, indent=4, sort_keys=True)
        os.replace(ruta_tmp, ruta_indice)
    except OSError as e:
        try:
            os.remove(ruta_tmp)
        except OSError:
            pass
        return f"No se pudo guardar el indice ({e})."
    return None
