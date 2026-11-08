import math
import tkinter as tk
from tkinter import font as tkfont, messagebox

from contactos import archivo, indice
from ui.menu import BarraMenu
from ui.ventana_contactos import VentanaContactos
from ui.ventana_settings import VentanaSettings

FONDOS = {"claro": "#f5f5f5", "oscuro": "#2b2b2b"}
TAMAÑO_FOTO = 100


class VentanaPrincipal:
    def __init__(self, root, config):
        self.root = root
        self.root.title("Agenda de Contactos")
        self.root.geometry("800x500")
        self.imagen = None  # hay que guardar la referencia o tkinter borra la imagen

        # al cambiar el size de estas fuentes se actualizan todos los widgets que las usan
        familia = tkfont.nametofont("TkDefaultFont").actual("family")
        self.fuente = tkfont.Font(root, family=familia)
        self.fuente_titulo = tkfont.Font(root, family=familia, weight="bold")

        self.barra = BarraMenu(root, {"salir": root.destroy, "contactos": self.abrir_contactos,
                                      "settings": self.abrir_settings})
        self.barra.pack(side="top", fill="x")

        self.contenido = tk.Frame(root, padx=20, pady=20)
        self.contenido.pack(fill="both", expand=True)
        self.lbl_foto = tk.Label(self.contenido)
        self.lbl_foto.grid(row=0, column=0, rowspan=3, sticky="nw", padx=(0, 15))
        self.lbl_saludo = tk.Label(self.contenido, font=self.fuente_titulo)
        self.lbl_saludo.grid(row=0, column=1, sticky="w")
        self.lbl_resumen = tk.Label(self.contenido, font=self.fuente, justify="left")
        self.lbl_resumen.grid(row=1, column=1, sticky="nw")

        self.aplicar(config)

    def abrir_contactos(self):
        ventana = VentanaContactos(self.root)
        self.root.wait_window(ventana)
        self.resumir()

    def abrir_settings(self):
        VentanaSettings(self.root, self.config, self.aplicar)

    # cuenta los contactos activos y avisa si el indice no coincide con el archivo
    def resumir(self):
        try:
            guardados = sum(1 for _ in archivo.recorrer())
        except OSError:
            self.lbl_resumen.config(text="No se pudo leer contactos.dat")
            return
        registros = archivo.total_registros()
        libres = registros - guardados
        self.lbl_resumen.config(text=f"Idioma: {self.config['idioma']}\n"
                                     f"Contactos guardados: {guardados}\n"
                                     f"Registros en el archivo: {registros} ({libres} libres)")

    def aplicar(self, config):
        self.config = config
        fondo = FONDOS[config["tema_interfaz"]]
        letra = config["color_letra"]
        self.fuente.configure(size=config["tamaño_fuente"])
        self.fuente_titulo.configure(size=config["tamaño_fuente"] + 4)

        self.contenido.config(bg=fondo)
        for lbl in (self.lbl_foto, self.lbl_saludo, self.lbl_resumen):
            lbl.config(bg=fondo, fg=letra)
        self.lbl_saludo.config(text=f"Bienvenido, {config['nombre_usuario']}")
        self.barra.pintar(config["color_barra_menu"], letra, self.fuente)
        self.cargar_foto(config["foto_perfil"])
        self.resumir()

    def cargar_foto(self, ruta):
        self.imagen = None
        if ruta:
            try:
                imagen = tk.PhotoImage(file=ruta)
                # subsample solo divide entre enteros, por eso el ceil
                factor = math.ceil(max(imagen.width(), imagen.height()) / TAMAÑO_FOTO)
                self.imagen = imagen.subsample(max(factor, 1))
            except tk.TclError:
                self.root.after(100, lambda: messagebox.showwarning(
                    "Foto de perfil", f"No se pudo abrir la foto:\n{ruta}", parent=self.root))

        if self.imagen:
            self.lbl_foto.config(image=self.imagen)
            self.lbl_foto.grid()
        else:
            self.lbl_foto.config(image="")
            self.lbl_foto.grid_remove()
