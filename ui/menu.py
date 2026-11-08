import tkinter as tk
from tkinter import messagebox


def acerca_de():
    messagebox.showinfo("Ayuda", "Agenda de Contactos\nLaboratorio 2 - Manejo de Archivos")


# se hace con Frame y Menubutton porque en windows tk.Menu no deja cambiar el color de la barra
class BarraMenu(tk.Frame):
    def __init__(self, master, acciones):
        super().__init__(master, bd=1, relief="raised")
        self.botones = []

        contactos = acciones["contactos"]
        self.agregar("Archivo", [("Salir", acciones["salir"])])
        self.agregar("Contactos", [("Agregar", contactos), ("Buscar", contactos),
                                   ("Modificar", contactos), ("Eliminar", contactos)])
        self.agregar("Exportar", [("Exportar a JSON", acciones["json"]),
                                  ("Generar reporte PDF", acciones["pdf"])])
        self.agregar("Herramientas", [("Verificar integridad", acciones["integridad"]),
                                      ("Crear respaldo ZIP", acciones["respaldo"])])
        self.agregar("Ayuda", [("Acerca de", acerca_de)])
        self.agregar("Settings", [("Preferencias...", acciones["settings"])])

    # None en la lista de opciones pone un separador
    def agregar(self, texto, opciones):
        boton = tk.Menubutton(self, text=texto, padx=8)
        menu = tk.Menu(boton, tearoff=0)
        for opcion in opciones:
            if opcion is None:
                menu.add_separator()
            else:
                menu.add_command(label=opcion[0], command=opcion[1])
        boton["menu"] = menu
        boton.pack(side="left")
        self.botones.append(boton)

    def pintar(self, fondo, letra, fuente):
        self.config(bg=fondo)
        for boton in self.botones:
            boton.config(bg=fondo, fg=letra, font=fuente)
