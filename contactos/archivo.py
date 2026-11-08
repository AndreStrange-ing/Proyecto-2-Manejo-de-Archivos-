import os

from contactos.registro import CAMPOS, MARCA_LIBRE, TAMAÑO, a_bytes, desde_bytes, registro_libre

carpeta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ruta_datos = os.path.join(carpeta, "contactos.dat")
largo_id = CAMPOS[0][1]


def crear_si_falta():
    os.makedirs(carpeta, exist_ok=True)
    if not os.path.exists(ruta_datos):
        open(ruta_datos, "wb").close()


def total_registros():
    try:
        return os.path.getsize(ruta_datos) // TAMAÑO
    except OSError:
        return 0


# cada registro empieza donde terminó el anterior, por eso basta una multiplicacion
def posicion(numero):
    return numero * TAMAÑO


# lee un solo registro saltando directo a su posicion, devuelve (contacto, byte final)
# el contacto es None si ese espacio esta libre
def leer(numero):
    with open(ruta_datos, "rb") as f:
        f.seek(posicion(numero))
        crudo = f.read(TAMAÑO)
        fin = f.tell()
    if len(crudo) < TAMAÑO:
        raise ValueError(f"el registro {numero} está incompleto")
    try:
        return desde_bytes(crudo[:-1]), fin
    except (UnicodeDecodeError, ValueError):
        raise ValueError(f"el registro {numero} está dañado")


# sobrescribe un registro sin tocar el resto del archivo
def escribir(numero, contacto):
    crear_si_falta()
    with open(ruta_datos, "rb+") as f:
        f.seek(posicion(numero))
        f.write(a_bytes(contacto))
        return f.tell()


# busca el primer espacio de un contacto eliminado leyendo solo el campo id
def buscar_libre():
    marca = MARCA_LIBRE.encode("utf-8")
    with open(ruta_datos, "rb") as f:
        for numero in range(total_registros()):
            f.seek(posicion(numero))
            if f.read(largo_id) == marca:
                return numero
    return None


# reutiliza el espacio de un eliminado y si no hay escribe al final
def agregar(contacto):
    crear_si_falta()
    numero = buscar_libre()
    if numero is None:
        numero = total_registros()
    return numero, escribir(numero, contacto)


# borrado logico: el registro se marca como libre pero sigue ocupando su lugar
def eliminar(numero):
    crear_si_falta()
    with open(ruta_datos, "rb+") as f:
        f.seek(posicion(numero))
        f.write(registro_libre())
        return f.tell()


# busqueda sin indice, hay que leer registro por registro hasta dar con el id
# devuelve tambien cuantos registros se leyeron para poder comparar
def buscar_secuencial(id_buscado):
    leidos = 0
    with open(ruta_datos, "rb") as f:
        for numero in range(total_registros()):
            crudo = f.read(TAMAÑO)
            leidos += 1
            try:
                contacto = desde_bytes(crudo[:-1])
            except (UnicodeDecodeError, ValueError):
                continue
            if contacto and contacto["id"] == id_buscado:
                return numero, leidos
    return None, leidos


# recorre todo el archivo, se usa para exportar y para reconstruir el indice
def recorrer():
    total = total_registros()
    if not total:
        return
    with open(ruta_datos, "rb") as f:
        for numero in range(total):
            crudo = f.read(TAMAÑO)
            try:
                contacto = desde_bytes(crudo[:-1])
            except (UnicodeDecodeError, ValueError):
                continue  # un registro dañado no detiene el recorrido
            if contacto:
                yield numero, contacto
