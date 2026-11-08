"""Compara buscar un contacto con el indice contra buscarlo registro por registro.

Se arma un archivo de prueba aparte con 100 contactos, el data/ real no se toca.
"""
import os
import shutil
from time import perf_counter

from contactos import archivo
from contactos.registro import TAMAÑO

TOTAL = 100
REPETICIONES = 200

carpeta_prueba = os.path.join(archivo.carpeta, "pruebas")
archivo.carpeta = carpeta_prueba
archivo.ruta_datos = os.path.join(carpeta_prueba, "contactos.dat")


def preparar():
    shutil.rmtree(carpeta_prueba, ignore_errors=True)
    for i in range(1, TOTAL + 1):
        archivo.agregar({"id": i, "nombre": f"Contacto de prueba {i}", "telefono": "5512-3344",
                         "correo": f"contacto{i}@correo.com", "ciudad": "Quetzaltenango"})
    return {i: i - 1 for i in range(1, TOTAL + 1)}


def medir(funcion):
    inicio = perf_counter()
    for _ in range(REPETICIONES):
        funcion()
    return (perf_counter() - inicio) / REPETICIONES * 1000


if __name__ == "__main__":
    indice = preparar()
    print(f"{TOTAL} contactos, {os.path.getsize(archivo.ruta_datos)} bytes, "
          f"{TAMAÑO} bytes por registro\n")
    print(f"{'ID buscado':<12}{'con indice':>24}{'secuencial':>26}")

    for id_ in (1, TOTAL // 2, TOTAL):
        con_indice = medir(lambda: archivo.leer(indice[id_]))
        secuencial = medir(lambda: archivo.buscar_secuencial(id_))
        leidos = archivo.buscar_secuencial(id_)[1]
        print(f"{id_:<12}{f'1 registro, {con_indice:.3f} ms':>24}"
              f"{f'{leidos} registros, {secuencial:.3f} ms':>26}")

    shutil.rmtree(carpeta_prueba, ignore_errors=True)
