import os
import tkinter as tk

from contactos import herramientas
from contactos.archivo import ruta_datos, total_registros
from contactos.indice import ruta_indice
from contactos.registro import TAMAÑO

ARCHIVOS = (("Contactos", ruta_datos), ("Índice", ruta_indice), ("Huella", herramientas.ruta_hash))


class VentanaInfo(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Información del archivo")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        marco = tk.Frame(self, padx=15, pady=15)
        marco.pack()
        fila = 0
        for titulo, ruta in ARCHIVOS:
            tk.Label(marco, text=titulo, font=("", 10, "bold")).grid(row=fila, column=0, sticky="w", pady=(8, 2))
            tk.Label(marco, text=os.path.basename(ruta)).grid(row=fila, column=1, sticky="w", pady=(8, 2))
            fila += 1
            for etiqueta, valor in self.detalles(ruta):
                tk.Label(marco, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=(15, 0))
                tk.Label(marco, text=valor).grid(row=fila, column=1, sticky="w")
                fila += 1

        tk.Button(marco, text="Cerrar", width=10, command=self.destroy).grid(
            row=fila, column=0, columnspan=2, pady=(14, 0))

    def detalles(self, ruta):
        try:
            datos = herramientas.metadatos(ruta)
        except FileNotFoundError:
            return [("Estado", "el archivo todavía no existe")]
        except OSError as e:
            return [("Estado", f"no se pudo leer ({e})")]

        filas = [("Tamaño", f"{datos['tamaño']} bytes"),
                 ("Última modificación", datos["modificado"]),
                 ("Permisos", f"lectura: {'sí' if datos['lectura'] else 'no'}   "
                              f"escritura: {'sí' if datos['escritura'] else 'no'}")]
        if ruta == ruta_datos:
            registros = total_registros()
            activos = datos["tamaño"] % TAMAÑO
            filas.insert(1, ("Registros", f"{registros} de {TAMAÑO} bytes cada uno"
                                          + (f", sobran {activos} bytes" if activos else "")))
        return filas
