import re

# cada campo se rellena con espacios hasta su largo, asi todos los registros miden
# igual y se puede saltar a cualquiera con seek(numero * TAMAÑO)
CAMPOS = (("id", 5), ("nombre", 35), ("telefono", 15), ("correo", 40), ("ciudad", 24))
TAMAÑO = sum(largo for _, largo in CAMPOS) + 1  # el +1 es el salto de linea
ID_MAX = 10 ** CAMPOS[0][1] - 1

# un id lleno de asteriscos marca un registro eliminado, ese espacio se reutiliza
MARCA_LIBRE = "*" * CAMPOS[0][1]

patron_telefono = re.compile(r"[0-9+\-() ]{8,}")
patron_correo = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


# los largos son en bytes porque el archivo se guarda en utf-8 y una ñ ocupa dos
def largo(texto):
    return len(texto.encode("utf-8"))


def validar(contacto):
    errores = []
    try:
        numero = int(contacto["id"])
        if not 1 <= numero <= ID_MAX:
            errores.append(f"el id debe estar entre 1 y {ID_MAX}")
    except (TypeError, ValueError):
        errores.append("el id debe ser un numero entero")

    if not contacto["nombre"].strip():
        errores.append("el nombre no puede quedar vacio")
    if not patron_telefono.fullmatch(contacto["telefono"]):
        errores.append("el telefono solo admite numeros y tiene al menos 8 digitos")
    if not patron_correo.fullmatch(contacto["correo"]):
        errores.append("el correo no tiene un formato valido")
    if not contacto["ciudad"].strip():
        errores.append("la ciudad no puede quedar vacia")

    for campo, tope in CAMPOS[1:]:
        if largo(contacto[campo]) > tope:
            errores.append(f"{campo} es muy largo, el maximo son {tope} bytes")
    return errores


# devuelve los bytes del registro, siempre del mismo tamaño
def a_bytes(contacto):
    linea = b""
    for campo, tope in CAMPOS:
        valor = str(contacto[campo]).strip().encode("utf-8")
        if len(valor) > tope:
            raise ValueError(f"{campo} no cabe en {tope} bytes")
        linea += valor.ljust(tope)
    return linea + b"\n"


def registro_libre():
    vacio = {campo: "" for campo, _ in CAMPOS}
    return a_bytes(vacio | {"id": MARCA_LIBRE})


# separa los bytes en campos, devuelve None si el registro esta eliminado
def desde_bytes(crudo):
    contacto = {}
    inicio = 0
    for campo, tope in CAMPOS:
        contacto[campo] = crudo[inicio:inicio + tope].decode("utf-8").strip()
        inicio += tope
    if contacto["id"] == MARCA_LIBRE:
        return None
    contacto["id"] = int(contacto["id"])
    return contacto
