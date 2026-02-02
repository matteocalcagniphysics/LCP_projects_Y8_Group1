import tkinter as tk
import numpy as np

# Configurazione estetica
CELL_SIZE = 20  # Dimensione fissa ma generosa
ROWS, COLS = 30, 40
BG_COLOR = "#1e1e1e" # Grigio scuro molto "pro"
GRID_COLOR = "#333333"

root = tk.Tk()
root.title("Game of Life - Jupyter Edition")
root.configure(bg=BG_COLOR)

# Calcoliamo la dimensione esatta per contenere la griglia
canvas_w = COLS * CELL_SIZE
canvas_h = ROWS * CELL_SIZE

# highlightthickness=0 rimuove il bordo brutto di default di tkinter
canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, 
                   bg=BG_COLOR, highlightthickness=0)
canvas.pack(padx=20, pady=20) # Aggiunge un po' di "respiro" intorno

def draw_static_grid():
    # Creiamo la matrice di esempio
    cells = np.random.choice([True, False], size=(ROWS, COLS))
    
    for (r, c), alive in np.ndenumerate(cells):
        x1, y1 = c * CELL_SIZE, r * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        
        color = "white" if alive else "black"
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=GRID_COLOR)

draw_static_grid()

# Impedisce all'utente di deformare la finestra (mantiene l'estetica)
root.resizable(False, False) 

root.mainloop()