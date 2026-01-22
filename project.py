# Libraries

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

##########################################################
##########################################################

# Color Map: black --> 0 (dead cell), white --> 1 (alive cell)
COLOR_MAP = ListedColormap(["black", "white"])

##########################################################
##########################################################

# Methods

def draw_grid(n_raws: int, n_columns: int) -> np.ndarray:
    """
    Draws a grid (using matplotlib) with the specified number of rows and columns.
    Args:
        n_raws (int): Number of rows in the grid.
        n_columns (int): Number of columns in the grid.
    Returns:
        np.ndarray: A 2D numpy array representing the grid.
    """
    grid: np.ndarray = np.zeros((n_raws, n_columns))
    return grid


def show_grid(grid: np.ndarray) -> None:
    """
    Displays the grid using matplotlib.
    Args:
        grid (np.ndarray): A 2D numpy array representing the grid.
    """

    plt.figure(figsize=(10,10))     # Fixed figure size for better visibility

    # Display the grid using pcolormesh to plot every cell as a square
    # and to have definite border lines between cells
    plt.pcolormesh(grid, cmap=COLOR_MAP, edgecolors='gray', linewidth=0.5)
    plt.gca().set_aspect('equal')
    plt.gca().invert_yaxis()

    plt.axis('off')  # Optional: turn off axes for better visualization
    plt.title(f"Dimension of the grid: {grid.shape[0]} x {grid.shape[1]} cells")
    plt.show()
    return None

##########################################################
##########################################################

# Test
grid = draw_grid(100, 100)
grid[3][9], grid[4][9], grid[5][9] = 1, 1, 1
show_grid(grid)