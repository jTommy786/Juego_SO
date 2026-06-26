import tkinter as tk
from ui.gui import GameGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()