import tkinter as tk


class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda de Contactos")
        self.root.geometry("800x500")

        # por ahora solo la ventana vacia, el menu va en ui/menu.py
