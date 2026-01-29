import numpy as np
import tkinter as tk

CANVAS_SIZE = 600   # width and height of canvas, fixed parameter

# Serve da esempio
rows, cols = 10, 10
cells = np.random.choice(a=[True, False], size=(rows, cols)) 

# Principal container
root = tk.Tk()
root.title("Game of Life")

cell_size = CANVAS_SIZE // cols   # Dimension of the cell, // so it's an integer 
canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
canvas.pack()

root.mainloop()