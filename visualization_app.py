import tkinter as tk
from tkinter import ttk
import numpy as np
import sys
sys.path.append('gameoflife')
import gameoflife.evolution as evo


# Global constants for colors
COLORS = {
    "alive"     : "white"   ,   # Alive cell
    "dead"      : "black"   ,   # Dead cell
    "bg"        : "#2E2E2E" ,   # Dark background
    "grid"      : "#505050" ,   # Grid lines
    "panel_bg"  : "#1E1E1E" ,   # Side panel background
    "btn_bg"    : "#3E3E3E" ,   # Button background
    "btn_fg"    : "white"   ,   # Button text
    "text"      : "white"   ,   # General text color
}


# Game of Life implementation using a class
class GameOfLife:

    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("Game of Life - Full Screen Visualization")
        
        # Get screen dimensions and set fullscreen
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        
        # Set fullscreen (works on Linux)
        try:
            self.root.attributes('-fullscreen', True)
        except:
            # Fallback if fullscreen doesn't work
            self.root.state('normal')
        
        self.root.configure(bg=COLORS["bg"])
        
        # Bind ESC key to exit fullscreen
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        # Initialize state variables
        self.rows = 5
        self.cols = 5
        self.state = np.random.choice([True, False], size=(self.rows, self.cols))
        self.previous_state = None  # For detecting stable states
        self.is_running = False
        self.fps = 5
        self.generation = 0
        self.animation_id = None

        # Calculate dimensions
        self.panel_width = 200
        self.canvas_width = self.screen_width - (2 * self.panel_width)
        self.canvas_height = self.screen_height
        
        # Calculate cell size to fit grid in center
        # Limit max cell size to prevent oversized grids with small dimensions
        self.cell_size = min(
            (self.canvas_width - 40) // self.cols,  # -40 for padding
            (self.canvas_height - 180) // self.rows,  # -180 for title + padding
            70  # Maximum cell size (larger for better visibility of small grids)
        )
        
        # Calculate actual grid size and offset to center it
        self.grid_width = self.cols * self.cell_size
        self.grid_height = self.rows * self.cell_size
        self.grid_offset_x = (self.canvas_width - self.grid_width) // 2
        # Ensure grid starts below title (minimum Y = 80)
        self.grid_offset_y = max(80, (self.canvas_height - self.grid_height) // 2)

        # Set up UI
        self._setup_layout()
        self._create_left_panel()
        self._create_center_panel()
        self._create_right_panel()
        self._draw_grid()


    def _setup_layout(self):
        """Create the three-column layout"""
        # Left panel for controls
        self.left_frame = tk.Frame(self.root, width=self.panel_width, 
                                   bg=COLORS["panel_bg"], relief=tk.RAISED, bd=2)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.left_frame.pack_propagate(False)  # Prevent frame from resizing

        # Center panel for grid
        self.center_frame = tk.Frame(self.root, bg=COLORS["bg"])
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right panel for info
        self.right_frame = tk.Frame(self.root, width=self.panel_width, 
                                    bg=COLORS["panel_bg"], relief=tk.RAISED, bd=2)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.right_frame.pack_propagate(False)


    def _create_left_panel(self):
        """Create control buttons in left panel"""
        # Title
        title = tk.Label(self.left_frame, text="Controls", 
                        font=("Arial", 16, "bold"), 
                        fg=COLORS["text"], bg=COLORS["panel_bg"])
        title.pack(pady=(20, 30))

        # Start/Stop button
        self.start_btn = tk.Button(self.left_frame, text="START", 
                                   command=self._toggle_simulation,
                                   font=("Arial", 12, "bold"),
                                   bg="#2E7D32", fg=COLORS["btn_fg"],
                                   activebackground="#388E3C",
                                   relief=tk.RAISED, bd=3,
                                   width=15, height=2)
        self.start_btn.pack(pady=10, padx=10)

        # Step button
        step_btn = tk.Button(self.left_frame, text="STEP",
                           command=self._step_forward,
                           font=("Arial", 11),
                           bg=COLORS["btn_bg"], fg=COLORS["btn_fg"],
                           activebackground="#505050",
                           relief=tk.RAISED, bd=2,
                           width=15, height=2)
        step_btn.pack(pady=10, padx=10)

        # Reset button
        reset_btn = tk.Button(self.left_frame, text="RESET",
                            command=self._reset_grid,
                            font=("Arial", 11),
                            bg="#C62828", fg=COLORS["btn_fg"],
                            activebackground="#D32F2F",
                            relief=tk.RAISED, bd=2,
                            width=15, height=2)
        reset_btn.pack(pady=10, padx=10)

        # Clear button
        clear_btn = tk.Button(self.left_frame, text="CLEAR",
                            command=self._clear_grid,
                            font=("Arial", 11),
                            bg=COLORS["btn_bg"], fg=COLORS["btn_fg"],
                            activebackground="#505050",
                            relief=tk.RAISED, bd=2,
                            width=15, height=2)
        clear_btn.pack(pady=10, padx=10)

        # Speed control
        speed_label = tk.Label(self.left_frame, text="Speed (FPS)", 
                             font=("Arial", 11),
                             fg=COLORS["text"], bg=COLORS["panel_bg"])
        speed_label.pack(pady=(30, 5))

        self.speed_var = tk.IntVar(value=self.fps)
        speed_slider = tk.Scale(self.left_frame, from_=1, to=30, 
                              orient=tk.HORIZONTAL,
                              variable=self.speed_var,
                              command=self._update_speed,
                              bg=COLORS["panel_bg"], 
                              fg=COLORS["text"],
                              highlightthickness=0,
                              troughcolor=COLORS["btn_bg"],
                              activebackground="#505050",
                              length=180)
        speed_slider.pack(pady=5, padx=10)

        # Seed control
        seed_label = tk.Label(self.left_frame, text="Seed (optional)", 
                             font=("Arial", 11),
                             fg=COLORS["text"], bg=COLORS["panel_bg"])
        seed_label.pack(pady=(30, 5))

        # Frame to hold seed entry and button
        seed_frame = tk.Frame(self.left_frame, bg=COLORS["panel_bg"])
        seed_frame.pack(pady=5, padx=10)

        self.seed_entry = tk.Entry(seed_frame, 
                                   font=("Arial", 11),
                                   width=12,
                                   bg=COLORS["btn_bg"],
                                   fg=COLORS["text"],
                                   insertbackground=COLORS["text"],
                                   relief=tk.SUNKEN, bd=2)
        self.seed_entry.pack(side=tk.LEFT, padx=(0, 5))

        seed_help = tk.Label(self.left_frame, 
                           text="(empty = random)", 
                           font=("Arial", 9),
                           fg="#888888", bg=COLORS["panel_bg"])
        seed_help.pack(pady=(0, 10))

        # Exit button at bottom
        exit_btn = tk.Button(self.left_frame, text="EXIT",
                           command=self.root.destroy,
                           font=("Arial", 10),
                           bg="#B71C1C", fg=COLORS["btn_fg"],
                           activebackground="#C62828",
                           relief=tk.RAISED, bd=2,
                           width=15, height=1)
        exit_btn.pack(side=tk.BOTTOM, pady=20, padx=10)


    def _create_center_panel(self):
        """Create the canvas for the grid"""
        self.canvas = tk.Canvas(self.center_frame, 
                               width=self.canvas_width, 
                               height=self.canvas_height,
                               bg=COLORS["bg"], 
                               highlightthickness=0)
        self.canvas.pack()

        # Add title above grid (fixed position for all grid sizes)
        title_y = 30
        self.canvas.create_text(self.canvas_width // 2, title_y,
                              text=f"Game of Life - {self.rows}×{self.cols} Grid",
                              font=("Arial", 18, "bold"),
                              fill=COLORS["text"],
                              tags="title")


    def _create_right_panel(self):
        """Create info display in right panel"""
        # Title
        title = tk.Label(self.right_frame, text="Information", 
                        font=("Arial", 16, "bold"),
                        fg=COLORS["text"], bg=COLORS["panel_bg"])
        title.pack(pady=(20, 30))

        # Generation counter
        gen_frame = tk.Frame(self.right_frame, bg=COLORS["panel_bg"])
        gen_frame.pack(pady=10, padx=10)

        gen_label = tk.Label(gen_frame, text="Generation:", 
                           font=("Arial", 11),
                           fg=COLORS["text"], bg=COLORS["panel_bg"])
        gen_label.pack()

        self.gen_display = tk.Label(gen_frame, text="0", 
                                   font=("Arial", 24, "bold"),
                                   fg="#4CAF50", bg=COLORS["panel_bg"])
        self.gen_display.pack()

        # Grid info
        info_frame = tk.Frame(self.right_frame, bg=COLORS["panel_bg"])
        info_frame.pack(pady=(30, 10), padx=10)

        size_title = tk.Label(info_frame, text="Grid Size", 
                            font=("Arial", 11, "bold"),
                            fg=COLORS["text"], bg=COLORS["panel_bg"])
        size_title.pack(pady=(0, 10))

        # Rows control
        rows_container = tk.Frame(info_frame, bg=COLORS["panel_bg"])
        rows_container.pack(pady=5)

        rows_label = tk.Label(rows_container, text="Rows:", 
                            font=("Arial", 10),
                            fg=COLORS["text"], bg=COLORS["panel_bg"],
                            width=8, anchor=tk.W)
        rows_label.pack(side=tk.LEFT, padx=(0, 5))

        self.rows_entry = tk.Entry(rows_container, 
                                  font=("Arial", 10),
                                  width=8,
                                  bg=COLORS["btn_bg"],
                                  fg=COLORS["text"],
                                  insertbackground=COLORS["text"],
                                  relief=tk.SUNKEN, bd=2)
        self.rows_entry.insert(0, str(self.rows))
        self.rows_entry.pack(side=tk.LEFT)

        # Columns control
        cols_container = tk.Frame(info_frame, bg=COLORS["panel_bg"])
        cols_container.pack(pady=5)

        cols_label = tk.Label(cols_container, text="Columns:", 
                            font=("Arial", 10),
                            fg=COLORS["text"], bg=COLORS["panel_bg"],
                            width=8, anchor=tk.W)
        cols_label.pack(side=tk.LEFT, padx=(0, 5))

        self.cols_entry = tk.Entry(cols_container, 
                                  font=("Arial", 10),
                                  width=8,
                                  bg=COLORS["btn_bg"],
                                  fg=COLORS["text"],
                                  insertbackground=COLORS["text"],
                                  relief=tk.SUNKEN, bd=2)
        self.cols_entry.insert(0, str(self.cols))
        self.cols_entry.pack(side=tk.LEFT)

        # Apply button
        apply_btn = tk.Button(info_frame, text="Apply Size",
                            command=self._apply_grid_size,
                            font=("Arial", 10),
                            bg="#1976D2", fg=COLORS["btn_fg"],
                            activebackground="#2196F3",
                            relief=tk.RAISED, bd=2,
                            width=12, height=1)
        apply_btn.pack(pady=(10, 0))

        # Current info display
        self.grid_info_label = tk.Label(info_frame, 
                                       text=f"Total: {self.rows * self.cols} cells",
                                       font=("Arial", 9),
                                       fg="#888888", bg=COLORS["panel_bg"])
        self.grid_info_label.pack(pady=(5, 0))

        # Status indicator
        status_frame = tk.Frame(self.right_frame, bg=COLORS["panel_bg"])
        status_frame.pack(pady=(30, 10), padx=10)

        status_label = tk.Label(status_frame, text="Status:", 
                              font=("Arial", 11),
                              fg=COLORS["text"], bg=COLORS["panel_bg"])
        status_label.pack()

        self.status_display = tk.Label(status_frame, text="PAUSED", 
                                      font=("Arial", 12, "bold"),
                                      fg="#FFC107", bg=COLORS["panel_bg"])
        self.status_display.pack()


    def _draw_grid(self):
        """Draw the Game of Life grid on the canvas"""
        self.canvas.delete("cell")  # Remove old cells
        
        for row in range(self.rows):
            for col in range(self.cols):
                x1 = self.grid_offset_x + col * self.cell_size
                y1 = self.grid_offset_y + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = COLORS["alive"] if self.state[row, col] else COLORS["dead"]
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=color, 
                                            outline=COLORS["grid"],
                                            tags="cell")


    def _update_simulation(self):
        """Update the grid to the next generation"""
        if self.is_running:
            # Save current state before evolving
            self.previous_state = self.state.copy()
            
            # Evolve to next generation
            self.state = evo.newgen(self.state)
            self.generation += 1
            
            # Check if state is stable (no change from previous)
            if np.array_equal(self.state, self.previous_state):
                # Stable state detected - stop simulation
                self.is_running = False
                self.start_btn.config(text="START", bg="#2E7D32", 
                                    activebackground="#388E3C")
                self.status_display.config(text="FINISHED", fg="#4CAF50")
                if self.animation_id:
                    self.root.after_cancel(self.animation_id)
                # Update display one last time
                self._draw_grid()
                self.gen_display.config(text=str(self.generation))
                return
            
            # Update display
            self._draw_grid()
            self.gen_display.config(text=str(self.generation))
            
            # Schedule next update
            delay = int(1000 / self.fps)
            self.animation_id = self.root.after(delay, self._update_simulation)


    def _toggle_simulation(self):
        """Start or stop the simulation"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_btn.config(text="PAUSE", bg="#C62828", 
                                activebackground="#D32F2F")
            self.status_display.config(text="RUNNING", fg="#4CAF50")
            self._update_simulation()
        else:
            self.start_btn.config(text="START", bg="#2E7D32", 
                                activebackground="#388E3C")
            self.status_display.config(text="PAUSED", fg="#FFC107")
            if self.animation_id:
                self.root.after_cancel(self.animation_id)


    def _step_forward(self):
        """Advance one generation"""
        if not self.is_running:
            self.state = evo.newgen(self.state)
            self.generation += 1
            self._draw_grid()
            self.gen_display.config(text=str(self.generation))


    def _reset_grid(self):
        """Reset the grid to random state (optionally with seed)"""
        was_running = self.is_running
        if self.is_running:
            self._toggle_simulation()
        
        # Get seed from entry field
        seed_text = self.seed_entry.get().strip()
        
        if seed_text:
            try:
                seed = int(seed_text)
                np.random.seed(seed)
                # Show feedback to user
                self.seed_entry.config(bg="#2E7D32")  # Green background
                self.root.after(500, lambda: self.seed_entry.config(bg=COLORS["btn_bg"]))
            except ValueError:
                # Invalid seed, show error
                self.seed_entry.config(bg="#C62828")  # Red background
                self.root.after(500, lambda: self.seed_entry.config(bg=COLORS["btn_bg"]))
                # Use random seed anyway
                np.random.seed(None)
        else:
            # No seed provided, use random
            np.random.seed(None)
        
        self.state = np.random.choice([True, False], 
                                     size=(self.rows, self.cols), 
                                     p=[0.3, 0.7])
        self.previous_state = None  # Reset for fresh simulation
        self.generation = 0
        self._draw_grid()
        self.gen_display.config(text="0")
        
        if was_running:
            self._toggle_simulation()


    def _clear_grid(self):
        """Clear all cells"""
        was_running = self.is_running
        if self.is_running:
            self._toggle_simulation()
        
        self.state = np.zeros((self.rows, self.cols), dtype=bool)
        self.previous_state = None  # Reset for fresh simulation
        self.generation = 0
        self._draw_grid()
        self.gen_display.config(text="0")


    def _update_speed(self, value):
        """Update simulation speed"""
        self.fps = int(value)


    def _apply_grid_size(self):
        """Apply new grid dimensions"""
        try:
            new_rows = int(self.rows_entry.get())
            new_cols = int(self.cols_entry.get())
            
            # Validate dimensions
            if new_rows < 5 or new_rows > 200:
                self.rows_entry.config(bg="#C62828")
                self.root.after(500, lambda: self.rows_entry.config(bg=COLORS["btn_bg"]))
                return
            
            if new_cols < 5 or new_cols > 300:
                self.cols_entry.config(bg="#C62828")
                self.root.after(500, lambda: self.cols_entry.config(bg=COLORS["btn_bg"]))
                return
            
            # Stop simulation if running
            was_running = self.is_running
            if self.is_running:
                self._toggle_simulation()
            
            # Update dimensions
            self.rows = new_rows
            self.cols = new_cols
            
            # Recalculate cell size
            # Limit max cell size to prevent oversized grids with small dimensions
            self.cell_size = min(
                (self.canvas_width - 40) // self.cols,
                (self.canvas_height - 180) // self.rows,
                70  # Maximum cell size (larger for better visibility of small grids)
            )
            
            # Recalculate grid dimensions and offset
            self.grid_width = self.cols * self.cell_size
            self.grid_height = self.rows * self.cell_size
            self.grid_offset_x = (self.canvas_width - self.grid_width) // 2
            # Ensure grid starts below title (minimum Y = 80)
            self.grid_offset_y = max(80, (self.canvas_height - self.grid_height) // 2)
            
            # Create new state
            self.state = np.random.choice([True, False], 
                                         size=(self.rows, self.cols), 
                                         p=[0.3, 0.7])
            self.previous_state = None  # Reset for fresh simulation
            self.generation = 0
            
            # Update displays
            self._draw_grid()
            self.gen_display.config(text="0")
            self.grid_info_label.config(text=f"Total: {self.rows * self.cols} cells")
            
            # Update canvas title (fixed position for all grid sizes)
            self.canvas.delete("title")
            title_y = 30
            self.canvas.create_text(self.canvas_width // 2, title_y,
                                  text=f"Game of Life - {self.rows}×{self.cols} Grid",
                                  font=("Arial", 18, "bold"),
                                  fill=COLORS["text"],
                                  tags="title")
            
            # Show success feedback
            self.rows_entry.config(bg="#2E7D32")
            self.cols_entry.config(bg="#2E7D32")
            self.root.after(500, lambda: self.rows_entry.config(bg=COLORS["btn_bg"]))
            self.root.after(500, lambda: self.cols_entry.config(bg=COLORS["btn_bg"]))
            
            if was_running:
                self._toggle_simulation()
                
        except ValueError:
            # Invalid input
            self.rows_entry.config(bg="#C62828")
            self.cols_entry.config(bg="#C62828")
            self.root.after(500, lambda: self.rows_entry.config(bg=COLORS["btn_bg"]))
            self.root.after(500, lambda: self.cols_entry.config(bg=COLORS["btn_bg"]))


if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root)
    root.mainloop()
