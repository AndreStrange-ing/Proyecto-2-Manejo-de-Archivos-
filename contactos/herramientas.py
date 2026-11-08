import hashlib
import os

from contactos.archivo import carpeta, ruta_datos

ruta_hash = os.path.join(carpeta, "contactos.sha256")


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
