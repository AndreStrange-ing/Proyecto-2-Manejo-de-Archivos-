import tkinter as tk
from tkinter import messagebox

from config.archivo import cargar
from ui.ventana_principal import VentanaPrincipal


if __name__ == "__main__":
    config, aviso = cargar()
    root = tk.Tk()
    app = VentanaPrincipal(root, config)
    # con after el aviso sale cuando la ventana ya esta dibujada
    if aviso:
        root.after(100, lambda: messagebox.showwarning("Configuración", aviso, parent=root))
    root.mainloop()
