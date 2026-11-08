import hashlib
import os
import zipfile
from datetime import datetime

from contactos.archivo import carpeta, ruta_datos
from contactos.indice import ruta_indice

ruta_hash = os.path.join(carpeta, "contactos.sha256")
carpeta_respaldos = os.path.join(carpeta, "respaldos")


# se lee por bloques para no cargar todo el archivo en memoria
def calcular_hash():
    resumen = hashlib.sha256()
    with open(ruta_datos, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            resumen.update(bloque)
    return resumen.hexdigest()


# se guarda despues de cada cambio hecho desde la aplicacion
def guardar_hash():
    huella = calcular_hash()
    os.makedirs(carpeta, exist_ok=True)
    with open(ruta_hash, "w", encoding="utf-8") as f:
        f.write(huella + "\n")
    return huella


# compara la huella guardada contra la del archivo actual
def verificar():
    try:
        actual = calcular_hash()
    except FileNotFoundError:
        return "sin_archivo", "Todavía no existe contactos.dat."
    except OSError as e:
        return "error", f"No se pudo leer contactos.dat ({e})."

    try:
        with open(ruta_hash, "r", encoding="utf-8") as f:
            guardada = f.read().strip()
    except (OSError, ValueError):
        guardar_hash()
        return "sin_huella", "No había huella guardada, se creó contactos.sha256 con el archivo actual."

    if guardada == actual:
        return "ok", f"El archivo está intacto.\n\nSHA-256: {actual}"
    return "alterado", ("El archivo fue modificado fuera de la aplicación.\n\n"
                        f"Huella guardada: {guardada}\nHuella actual:   {actual}")


# tamaño, fecha de modificacion y permisos reales del archivo
def metadatos(ruta):
    datos = os.stat(ruta)
    return {"tamaño": datos.st_size,
            "modificado": datetime.fromtimestamp(datos.st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
            "lectura": os.access(ruta, os.R_OK),
            "escritura": os.access(ruta, os.W_OK)}


# guarda los contactos, el indice y la huella en un zip con la fecha en el nombre
def crear_respaldo():
    incluidos = [ruta for ruta in (ruta_datos, ruta_indice, ruta_hash) if os.path.exists(ruta)]
    if not incluidos:
        return None, 0, 0

    os.makedirs(carpeta_respaldos, exist_ok=True)
    nombre = datetime.now().strftime("respaldo_%Y%m%d_%H%M%S")
    destino = os.path.join(carpeta_respaldos, nombre + ".zip")
    copia = 2  # dos respaldos en el mismo segundo no se deben pisar
    while os.path.exists(destino):
        destino = os.path.join(carpeta_respaldos, f"{nombre}_{copia}.zip")
        copia += 1
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zip_:
        for ruta in incluidos:
            zip_.write(ruta, os.path.basename(ruta))

    original = sum(os.path.getsize(ruta) for ruta in incluidos)
    return destino, original, os.path.getsize(destino)
