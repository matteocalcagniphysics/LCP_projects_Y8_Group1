import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.animation as animation
import evolution as evo


# Color configuration for visualization
COLORS = {
    "Alive" : "white"  ,        # Alive cells
    "Dead"  : "black"  ,        # Dead cells
    "Grid"  : "#505050",        # Grid color (light gray)
}




def is_notebook() -> bool:
    """
    Detects if the code is running in a Jupyter notebook environment.
    Used to determine whether to use HTML display for Jupyter notebooks or plt.show() for regular Python scripts.
    Returns:
        bool: True if running in Jupyter, False otherwise.
    """
    try:
        from IPython import get_ipython
        if get_ipython() is None:
            return False
        # Check if we're in an IPython environment (notebook or IPython terminal)
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':          # Jupyter notebook
            return True
        elif shell == 'TerminalInteractiveShell':   # IPython terminal
            return False
        else:
            return False
    except (ImportError, NameError):
        return False



def create_evolution(grid: np.ndarray, frames: int, interval: int) -> animation.FuncAnimation:
    """
    Creates the Game of Life grid evolution using matplotlib.
    Helper function to be used by plot_evolution.
    Args (passed by plot_evolution):
        grid (np.ndarray): 2D array (either boolean or numeric) representing the initial state.
        frames (int): Number of generations to animate.
        interval (int): Time in milliseconds between frames.
    Returns:
        animation.FuncAnimation: The animation object that can be displayed in Jupyter.
    """

    # 1. Create a personalized colormap
    colors_list = [COLORS["Dead"], COLORS["Alive"]]
    cmap = mcolors.ListedColormap(colors_list)
    


    # 2. Calculate figure size based on grid dimensions for better visualization
    # First, get number of rows and columns and we define how big each cell should be
    rows, cols = grid.shape
    cell_size_inches = 0.5
    
    # Then we calculate width and height of the figure adding a small margin for 
    # title and axes
    w = cols * cell_size_inches + 1.5
    h = rows * cell_size_inches + 1.5
    
    # Finally, we limit the maximum size to avoid too large figures
    max_size = 7
    w = min(w, max_size)
    h = min(h, max_size)



    # 3. Visualization 
    #    We use imshow because it's very efficient for displaying 2D arrays.
    #    We add interpolation='nearest' to avoid blurring of the cells.
    #    We add .astype(int) in case the grid is boolean, so it coverts False->0, True->1
    fig, ax = plt.subplots(figsize=(w,h), dpi=120)    
    img = ax.imshow(grid.astype(int), cmap=cmap, interpolation='nearest')



    # 4. Aesthetic adjustments
    #    First, we use major tick positions to definire where grid lines should be drawn
    #    -0.5 is used to center the grid lines between the cells
    ax.set_xticks(np.arange(-0.5, cols, 1))
    ax.set_yticks(np.arange(-0.5, rows, 1))
    ax.grid(which='major', color=COLORS["Grid"], linestyle='-', linewidth=1)
     
    # Then, we remove the ticks marks and labels for a cleaner look (grid lines remain visible).
    # We also set the title, pad is used to add some space between title and grid
    ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
    title = ax.set_title(f"Game of Life - Dimension: {rows}x{cols}\nGeneration: 1", 
                         fontsize=15, color='black', pad=20)


    # 5. Creating the animation
    #    First, we create a function to "update" every frame
    def update(frame):
        """
        This function is called by FuncAnimation for every frame.
        """
        # 1. Compute the next generation of the grid. 
        #    Keyword nonlocal "tells" Python to edit the variable "grid" from
        #    the external scope, avoiding creating a new local variable
        nonlocal grid
        grid = evo.newgen(grid)

        # 2. Update the image data and title text. 
        #    Instead of plotting again, we just update the data of the existing image
        img.set_data(grid.astype(int))
        title.set_text(f"Game of Life - Dimension: {rows}x{cols}\nGeneration: {frame+1}")

        # Return a list of elements that have changed to be used by blit for optimization.
        return img, title

    plt.tight_layout()

    # Then, we create the animation object
    # Use blit=True only in notebooks (where to_jshtml() is used) for better performance
    # In regular Python scripts, blit=True causes the grid to disappear after the first frame
    # because the grid is not returned by the update function
    use_blit = is_notebook()
    anim = animation.FuncAnimation(fig, update, frames=frames, interval=interval, 
                                   blit=use_blit, repeat=False)
    
    # Close the figure only in notebook environments to prevent static image display
    # In regular Python scripts, we need to keep it open for plt.show()
    if is_notebook():
        plt.close(fig)
    
    return anim


def plot_evolution(grid: np.ndarray, frames: int, FPS: int) -> None:
    """
    Plots the Game of Life grid evolution.
    Automatically detects the environment and uses:
    - HTML display for Jupyter notebooks
    - plt.show() for regular Python scripts
    
    Args:
        grid (np.ndarray): 2D array representing the initial grid state.
        frames (int): Number of generations to animate.
        FPS (int): Frames per second for the animation (converted in "interval": delay
                   between frames in milliseconds).
    """

    # 1. Use the helper function to create the animation object
    interval = 1000 // FPS  # Convert FPS to interval in milliseconds
    anim = create_evolution(grid, frames, interval=interval)

    # 2. Display the animation based on the environment
    if is_notebook():
        # In Jupyter notebook: use HTML display with styling
        try:
            from IPython.display import HTML, display
            styled_html = f"""
                <div style="max-width: 600px; width: 100%; margin: 0 auto;">
                    {anim.to_jshtml()}
                </div>
            """
            display(HTML(styled_html))
        except ImportError:
            # Fallback if IPython is not available (shouldn't happen if is_notebook() returned True)
            print("Warning: IPython not available, using plt.show() instead")
            plt.show()
    else:
        # In regular Python script: use matplotlib's native display
        plt.show()

    return None