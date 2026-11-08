import tkinter as tk
from tkinter import messagebox, ttk

from contactos import archivo, indice
from contactos.registro import CAMPOS, validar

ETIQUETAS = {"id": "ID", "nombre": "Nombre", "telefono": "Teléfono",
             "correo": "Correo", "ciudad": "Ciudad"}


class VentanaContactos(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Contactos")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.indice, aviso = indice.cargar()
        self.campos = {campo: tk.StringVar() for campo, _ in CAMPOS}

        marco = tk.Frame(self, padx=15, pady=15)
        marco.pack()

        for fila, (campo, tope) in enumerate(CAMPOS):
            tk.Label(marco, text=ETIQUETAS[campo]).grid(row=fila, column=0, sticky="w", pady=3)
            tk.Entry(marco, textvariable=self.campos[campo], width=42).grid(row=fila, column=1, sticky="w")
            tk.Label(marco, text=f"{tope} bytes", fg="#666").grid(row=fila, column=2, sticky="w", padx=6)
        tk.Button(marco, text="Sugerir ID libre", command=self.sugerir_id).grid(row=0, column=3, sticky="w")

        botones = tk.Frame(marco)
        botones.grid(row=len(CAMPOS), column=0, columnspan=4, sticky="w", pady=(12, 8))
        for texto, accion in (("Agregar", self.agregar), ("Buscar", self.buscar),
                              ("Modificar", self.modificar), ("Eliminar", self.eliminar),
                              ("Limpiar", self.limpiar)):
            tk.Button(botones, text=texto, width=11, command=accion).pack(side="left", padx=3)

        self.lista = ttk.Treeview(marco, columns=("registro",) + tuple(ETIQUETAS), show="headings", height=9)
        self.lista.heading("registro", text="Registro")
        self.lista.column("registro", width=70, anchor="center")
        for campo in ETIQUETAS:
            self.lista.heading(campo, text=ETIQUETAS[campo])
            self.lista.column(campo, width=70 if campo == "id" else 170)
        self.lista.grid(row=len(CAMPOS) + 1, column=0, columnspan=4, sticky="we")
        self.lista.bind("<<TreeviewSelect>>", self.tomar_de_lista)

        self.estado = tk.Label(marco, text="", anchor="w", fg="#1f3864")
        self.estado.grid(row=len(CAMPOS) + 2, column=0, columnspan=4, sticky="we", pady=(8, 0))

        self.refrescar()
        if aviso:
            messagebox.showwarning("Contactos", aviso, parent=self)

    # todas las operaciones de archivo pasan por aqui para que un error no cierre la app
    def intentar(self, accion):
        try:
            return accion(), True
        except PermissionError:
            messagebox.showerror("Contactos", "No hay permiso para escribir contactos.dat.", parent=self)
        except (OSError, ValueError) as e:
            messagebox.showerror("Contactos", str(e), parent=self)
        return None, False

    def avisar(self, texto):
        self.estado.config(text=texto)

    def guardar_indice(self):
        error = indice.guardar(self.indice)
        if error:
            messagebox.showerror("Contactos", error, parent=self)

    def limpiar(self):
        for variable in self.campos.values():
            variable.set("")
        self.avisar("")

    def sugerir_id(self):
        self.campos["id"].set(max(self.indice, default=0) + 1)

    def tomar_de_lista(self, evento):
        seleccion = self.lista.selection()
        if seleccion:
            valores = self.lista.item(seleccion[0], "values")[1:]
            for (campo, _), valor in zip(CAMPOS, valores):
                self.campos[campo].set(valor)

    def refrescar(self):
        self.lista.delete(*self.lista.get_children())
        contactos, ok = self.intentar(lambda: list(archivo.recorrer()))
        if ok:
            for numero, contacto in contactos:
                self.lista.insert("", "end", values=(numero,) + tuple(contacto[c] for c, _ in CAMPOS))

    # lee el formulario y lo valida, devuelve None si hay algo mal
    def leer_formulario(self):
        contacto = {campo: self.campos[campo].get().strip() for campo, _ in CAMPOS}
        errores = validar(contacto)
        if errores:
            messagebox.showwarning("Contactos", "\n".join(errores), parent=self)
            return None
        contacto["id"] = int(contacto["id"])
        return contacto

    # el id escrito, solo para buscar, modificar y eliminar
    def id_escrito(self):
        try:
            return int(self.campos["id"].get())
        except ValueError:
            messagebox.showwarning("Contactos", "Escriba el ID del contacto.", parent=self)
            return None

    def agregar(self):
        contacto = self.leer_formulario()
        if contacto is None:
            return
        if contacto["id"] in self.indice:
            if messagebox.askyesno("Contactos", f"El ID {contacto['id']} ya existe. "
                                   "¿Desea modificar ese contacto?", parent=self):
                self.modificar()
            return

        resultado, ok = self.intentar(lambda: archivo.agregar(contacto))
        if not ok:
            return
        numero, fin = resultado
        self.indice[contacto["id"]] = numero
        self.guardar_indice()
        self.refrescar()
        self.avisar(f"Agregado en el registro {numero}, bytes {archivo.posicion(numero)} a {fin}.")

    def buscar(self):
        id_ = self.id_escrito()
        if id_ is None:
            return
        numero = self.indice.get(id_)
        if numero is None:
            messagebox.showinfo("Contactos", f"No existe ningún contacto con el ID {id_}.", parent=self)
            self.avisar(f"El ID {id_} no está en el índice.")
            return

        resultado, ok = self.intentar(lambda: archivo.leer(numero))
        if not ok:
            return
        contacto, fin = resultado
        if contacto is None:
            messagebox.showinfo("Contactos", "Ese registro está libre.", parent=self)
            return
        for campo, _ in CAMPOS:
            self.campos[campo].set(contacto[campo])
        self.avisar(f"El índice dio el registro {numero}, se leyó con seek desde el byte "
                    f"{archivo.posicion(numero)} hasta el {fin}.")

    def modificar(self):
        contacto = self.leer_formulario()
        if contacto is None:
            return
        numero = self.indice.get(contacto["id"])
        if numero is None:
            messagebox.showinfo("Contactos", "Ese ID no existe, usa Agregar.", parent=self)
            return

        fin, ok = self.intentar(lambda: archivo.escribir(numero, contacto))
        if not ok:
            return
        self.refrescar()
        self.avisar(f"Registro {numero} sobrescrito en los bytes {archivo.posicion(numero)} a {fin}, "
                    "el resto del archivo no se tocó.")

    def eliminar(self):
        id_ = self.id_escrito()
        if id_ is None:
            return
        numero = self.indice.get(id_)
        if numero is None:
            messagebox.showinfo("Contactos", f"No existe ningún contacto con el ID {id_}.", parent=self)
            return

        resultado, ok = self.intentar(lambda: archivo.leer(numero))
        if not ok or resultado[0] is None:
            return
        nombre = resultado[0]["nombre"]
        if not messagebox.askyesno("Contactos", f"¿Eliminar a {nombre} (ID {id_})?\n\n"
                                   "El registro se marca como libre y su espacio se reutiliza, "
                                   "el archivo no cambia de tamaño.", parent=self):
            return

        if not self.intentar(lambda: archivo.eliminar(numero))[1]:
            return
        del self.indice[id_]
        self.guardar_indice()
        self.limpiar()
        self.refrescar()
        self.avisar(f"Registro {numero} marcado como libre, queda disponible para el próximo contacto.")
