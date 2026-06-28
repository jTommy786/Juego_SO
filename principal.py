import tkinter as tk
from ui.interfaz import InterfazJuego

if __name__ == "__main__":
    raiz = tk.Tk()
    interfaz = InterfazJuego(raiz)
    raiz.mainloop()