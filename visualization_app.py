import tkinter as tk
import numpy as np

# Global constants
COLORS = {
    "alive" : "white"   ,       # Alive cell
    "dead"  : "black"   ,       # Dead cell
    "bg"    : "#505050" ,       # Background
}
WIDTH = 1000
HEIGHT = 800

# Grid variables that can be changed in the app
ROWS = 20
COLS = 20
CELL_SIZE = WIDTH // COLS


# Game of Life implementation using a class
class GameOfLife():

    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("Game of Life")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)         # Don't make the window resizable
        self.root.configure(bg=COLORS["bg"])      # Set the background color of the main window

        # Initialise state variables
        self.state = np.random.choice([True, False], size=(ROWS, COLS))     # Initial state of the grid
        self.is_running = False                                             # State of the simulation
        self.FPS = 2                                                        # Frame per second
        self.generation = 0                                                 # Generation counter

        # Call setup methods
        self._setup_canvas()
        self._draw_grid()

    def _setup_canvas(self):
        """Set up the canvas for drawing the grid"""
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=COLORS["bg"])
        self.canvas.pack()
    
    def _draw_grid(self):
        """Draw the grid on the canvas"""
        for row in range(ROWS):
            for col in range(COLS):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = COLORS["alive"] if self.state[row, col] else COLORS["dead"]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="blue")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root)
    root.mainloop()                # Start the application
