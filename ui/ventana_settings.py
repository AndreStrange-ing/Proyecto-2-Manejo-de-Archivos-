import os
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

from config.archivo import cargar, guardar, listar_perfiles, nombre_perfil_valido, ruta_perfil
from config.valores import FUENTE_MAX, FUENTE_MIN, IDIOMAS, TEMAS, validar


class VentanaSettings(tk.Toplevel):
    def __init__(self, master, config, al_guardar):
        super().__init__(master)
        self.title("Settings")
        self.resizable(False, False)
        # transient + grab_set para que no se pueda usar la principal mientras esta abierta
        self.transient(master)
        self.grab_set()
        self.al_guardar = al_guardar

        self.nombre = tk.StringVar()
        self.tema = tk.StringVar()
        self.idioma = tk.StringVar()
        self.fuente = tk.StringVar()
        self.foto = tk.StringVar()
        self.colores = {}
        self.perfil = tk.StringVar()

        marco = tk.Frame(self, padx=15, pady=15)
        marco.pack()

        tk.Label(marco, text="Perfil").grid(row=0, column=0, sticky="w", pady=4)
        self.combo_perfiles = ttk.Combobox(marco, textvariable=self.perfil, values=listar_perfiles(),
                                           state="readonly", width=18)
        self.combo_perfiles.grid(row=0, column=1, sticky="w")
        botones_perfil = tk.Frame(marco)
        botones_perfil.grid(row=0, column=2, sticky="w", padx=4)
        tk.Button(botones_perfil, text="Cargar", command=self.cargar_perfil).pack(side="left")
        tk.Button(botones_perfil, text="Guardar como perfil...",
                  command=self.guardar_perfil).pack(side="left", padx=(4, 0))
        ttk.Separator(marco).grid(row=1, column=0, columnspan=3, sticky="ew", pady=8)

        tk.Label(marco, text="Nombre de usuario").grid(row=2, column=0, sticky="w", pady=4)
        tk.Entry(marco, textvariable=self.nombre, width=30).grid(row=2, column=1, columnspan=2, sticky="w")

        tk.Label(marco, text="Tema").grid(row=3, column=0, sticky="w", pady=4)
        temas = tk.Frame(marco)
        temas.grid(row=3, column=1, columnspan=2, sticky="w")
        for tema in TEMAS:
            tk.Radiobutton(temas, text=tema.capitalize(), value=tema, variable=self.tema).pack(side="left")

        tk.Label(marco, text="Idioma").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Combobox(marco, textvariable=self.idioma, values=IDIOMAS, state="readonly",
                     width=8).grid(row=4, column=1, sticky="w")

        tk.Label(marco, text="Tamaño de fuente").grid(row=5, column=0, sticky="w", pady=4)
        tk.Spinbox(marco, from_=FUENTE_MIN, to=FUENTE_MAX, textvariable=self.fuente,
                   width=6).grid(row=5, column=1, sticky="w")

        # cuadrito que muestra el color que esta elegido
        self.muestras = {}
        for fila, (campo, texto) in enumerate([("color_barra_menu", "Color barra de menú"),
                                                ("color_letra", "Color de letra")], start=6):
            tk.Label(marco, text=texto).grid(row=fila, column=0, sticky="w", pady=4)
            muestra = tk.Label(marco, width=4, relief="solid", bd=1)
            muestra.grid(row=fila, column=1, sticky="w")
            tk.Button(marco, text="Elegir...",
                      command=lambda c=campo: self.elegir_color(c)).grid(row=fila, column=2, sticky="w")
            self.muestras[campo] = muestra

        tk.Label(marco, text="Foto de perfil").grid(row=8, column=0, sticky="w", pady=4)
        tk.Entry(marco, textvariable=self.foto, width=30, state="readonly").grid(row=8, column=1, sticky="w")
        tk.Button(marco, text="Buscar...", command=self.elegir_foto).grid(row=8, column=2, sticky="w", padx=4)

        botones = tk.Frame(marco)
        botones.grid(row=9, column=0, columnspan=3, sticky="e", pady=(15, 0))
        tk.Button(botones, text="Guardar", width=10, command=self.guardar_cambios).pack(side="left", padx=4)
        tk.Button(botones, text="Cancelar", width=10, command=self.destroy).pack(side="left")

        self.llenar(config)

    def llenar(self, config):
        self.nombre.set(config["nombre_usuario"])
        self.tema.set(config["tema_interfaz"])
        self.idioma.set(config["idioma"])
        self.fuente.set(str(config["tamaño_fuente"]))
        self.foto.set(config["foto_perfil"])
        for campo in self.muestras:
            self.colores[campo] = config[campo]
            self.muestras[campo].config(bg=config[campo])

    def elegir_color(self, campo):
        _, color = colorchooser.askcolor(self.colores[campo], parent=self)
        if color:  # si cancela devuelve None
            self.colores[campo] = color
            self.muestras[campo].config(bg=color)

    def elegir_foto(self):
        # tkinter solo puede mostrar png y gif sin librerias extra
        ruta = filedialog.askopenfilename(parent=self, title="Foto de perfil",
                                          filetypes=[("Imágenes", "*.png *.gif")])
        if ruta:
            self.foto.set(ruta)

    # junta lo que hay en los campos y lo valida, devuelve None si algo esta mal
    def leer_campos(self):
        try:
            fuente = int(self.fuente.get())
        except ValueError:
            fuente = None

        datos = {
            "nombre_usuario": self.nombre.get().strip(),
            "tema_interfaz": self.tema.get(),
            "idioma": self.idioma.get(),
            "tamaño_fuente": fuente,
            **self.colores,
            "foto_perfil": self.foto.get(),
        }
        config, errores = validar(datos)
        if errores:
            messagebox.showwarning("Settings", "Revise estos campos: " + ", ".join(errores), parent=self)
            return None
        return config

    def guardar_cambios(self):
        config = self.leer_campos()
        if config is None:
            return

        # si no se pudo guardar la ventana se queda abierta con lo que el usuario puso
        error = guardar(config)
        if error:
            messagebox.showerror("Settings", error, parent=self)
            return

        self.al_guardar(config)
        self.destroy()

    # solo llena los campos, se aplica hasta que le den Guardar
    def cargar_perfil(self):
        nombre = self.perfil.get()
        if not nombre:
            messagebox.showinfo("Perfiles", "Seleccione un perfil.", parent=self)
            return
        config, aviso = cargar(ruta_perfil(nombre))
        if aviso:
            messagebox.showwarning("Perfiles", aviso, parent=self)
        self.llenar(config)

    def guardar_perfil(self):
        config = self.leer_campos()
        if config is None:
            return

        nombre = simpledialog.askstring("Guardar perfil", "Nombre del perfil:", parent=self)
        if nombre is None:  # cancelo
            return
        nombre = nombre.strip()
        if not nombre_perfil_valido(nombre):
            messagebox.showwarning("Perfiles", 'Nombre no válido. No puede estar vacío, terminar en punto '
                                   'ni tener \\ / : * ? " < > |', parent=self)
            return

        ruta = ruta_perfil(nombre)
        if os.path.exists(ruta) and not messagebox.askyesno(
                "Perfiles", f"Ya existe el perfil {nombre}. ¿Desea sobrescribirlo?", parent=self):
            return

        error = guardar(config, ruta)
        if error:
            messagebox.showerror("Perfiles", error, parent=self)
            return
        self.combo_perfiles.config(values=listar_perfiles())
        self.perfil.set(nombre)
        messagebox.showinfo("Perfiles", f"Perfil {nombre} guardado.", parent=self)
