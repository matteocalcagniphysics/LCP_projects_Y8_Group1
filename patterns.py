import numpy as np


"""
Usage:
    import patterns
    grid = patterns.insert_pattern(grid, "Category", "Name", row, col, rotate=0, flip=False)

Available Tools:
    - patterns.get_available_categories(): Returns a list of all category names.
    - patterns.get_patterns_by_category("CategoryName"): Returns names of patterns in a category.
    - patterns.get_pattern_data("Category", "Name"): Returns a dictionary with size, live cells, and density.
    - patterns.get_all_library_data(): Returns a list of dictionaries containing data for all available patterns.
    - patterns.insert_pattern(...): inserts a pattern into a grid with toroidal wrapping.

"""

def _create_pulsar():
    """Generates the 13x13 matrix for the Pulsar oscillator."""
    p = np.zeros((13, 13), dtype=int)
    lines = [0, 5, 7, 12]
    for l in lines:
        p[l, 2:5] = p[l, 8:11] = 1
        p[2:5, l] = p[8:11, l] = 1
    return p

def _create_pentadecathlon():
    """Generates the 3x8 matrix for the Pentadecathlon oscillator."""
    p = np.ones((3, 8), dtype=int)
    p[1, 1:7] = 0  
    return p

def _create_glider_gun():
    """Generates the 9x36 matrix for the Gosper Glider Gun."""
    gun = np.zeros((9, 36), dtype=int)
    coords = [(4,0), (4,1), (5,0), (5,1), (2,12), (2,13), (3,11), (4,10), (5,10), (6,10), 
              (7,11), (8,12), (8,13), (5,14), (3,15), (4,16), (5,16), (6,16), (5,17), 
              (2,20), (2,21), (3,20), (3,21), (4,20), (4,21), (1,22), (5,22), (0,24), 
              (1,24), (5,24), (6,24), (2,34), (2,35), (3,34), (3,35)]
    for r, c in coords: 
        gun[r, c]= 1
    return gun

def _create_random(rows=10, cols=10, density=0.3, seed=None):
    """Generates a random matrix with configurable dimensions and density."""
    if seed is not None:
        np.random.seed(seed)
    return (np.random.rand(rows, cols) < density).astype(int)

def _create_breeder():
    """Generates a diagonal Breeder (simplified version)."""
    b = np.zeros((50, 50), dtype=int)
    for i in range(0, 48, 6):
        b[i:i+2, i:i+2] = 1
    return b

def _create_snark():
    """Stable reflector (Snark) coordinates."""
    s = np.zeros((11, 17), dtype=int)
    coords = [(0,5), (0,6), (1,5), (1,7), (2,7), (3,0), (3,1), (3,7), (3,8), (4,0), (4,1),
              (5,8), (5,9), (5,10), (6,8), (6,11), (7,9), (7,10), (8,15), (8,16), (9,14), (9,16), (10,16)]
    for r, c in coords: s[r, c] = 1
    return s
  



# --- Nested dictionary storing all patterns ---
SEED_DATA = {
    "Still Life": {
        "Block": np.array([[1, 1], [1, 1]]),
        "Beehive": np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]]),
        "Loaf": np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]]),
        "Snark": _create_snark()  # Added: Stable reflector
    },
    "Oscillator": {
        "Blinker": np.array([[1, 1, 1]]),
        "Toad": np.array([[0, 0, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 0]]),
        "Pulsar": _create_pulsar(),
        "Pentadecathlon": _create_pentadecathlon()
    },
    "Spaceship": {
        "Glider": np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]]),
        "LWSS": np.array([[0, 1, 1, 1, 1], [1, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 0, 0, 1, 0]]),
        "HWSS": np.array([[0,0,0,1,1,0,0], [0,1,0,0,0,0,1], [1,0,0,0,0,0,0], [1,0,0,0,0,0,1], [1,1,1,1,1,1,1]]) #  Heavyweight Spaceship
    },
    "Complex": { 
        "Glider Gun": _create_glider_gun(),
        "Breeder": _create_breeder()  #  Quadratic growth pattern
    },
    "Methuselah": {
        "Acorn": np.array([[0,1,0,0,0,0,0], [0,0,0,1,0,0,0], [1,1,0,0,1,1,1]]) #  Long-lived small pattern
    },
    "Random": {
        "Small Chaos": _create_random(5, 5),
        "Medium Chaos": _create_random(10, 10),
        "Large Chaos": _create_random(20, 20)
    }    
}
# Core functions

def insert_pattern(grid, category, name, row_origin, col_origin, rotate=0, flip=False):
    
    """

    Inserts a pattern into the provided grid using toroidal (wrap-around) logic.

    

    Parameters:

    - grid: The NumPy array representing the world.

    - category/name: Strings to identify the pattern in SEED_DATA.

    - row_origin/col_origin: Starting coordinates for the top-left of the pattern.

    - rotate: Number of 90-degree anticlockwise rotations (0-3).

    - flip: If True, flips the pattern horizontally before insertion.

    """
    if category not in SEED_DATA or name not in SEED_DATA[category]:
        print(f"Error: Pattern '{name}' in '{category}' not found.")
        return grid

   
    seed = SEED_DATA[category][name].copy()
    if flip: seed = np.fliplr(seed)
    if rotate != 0: seed = np.rot90(seed, k=rotate)

    g_rows, g_cols = grid.shape
    rows_idx, cols_idx = np.where(seed == 1)

   
    target_rows = (rows_idx + row_origin) % g_rows
    target_cols = (cols_idx + col_origin) % g_cols

    grid[target_rows, target_cols] = 1
    return grid
    
def get_available_categories():
    """Returns a list of all available pattern categories."""
    return list(SEED_DATA.keys())

def get_patterns_by_category(category):
    """Returns a list of pattern names within a specific category."""
    return list(SEED_DATA.get(category, {}).keys())

def get_pattern_data(category, name):
    """ Returns statistics for the selected pattern.

    Useful for data analysis (e.g., calculating efficiency or growth rates).

    

    Parameters:

    - category (str): The category of the pattern.

    - name (str): The specific name of the pattern.

    

    Returns:

    - dict: Dictionary containing dimensions, live cell count, and density, 

            or None if the pattern is not found.

    """
    if category not in SEED_DATA or name not in SEED_DATA[category]:
        return None
    
    pattern = SEED_DATA[category][name]
    rows, cols = pattern.shape
    total_cells = rows * cols
    live_cells = np.sum(pattern)
    density = live_cells / total_cells
    
    return {
        "name": name,
        "category": category,
        "dimensions": (rows, cols),
        "live_cells": int(live_cells),
        "initial_density": round(float(density), 3)
    }
def get_all_library_data():
    """Returns data for every pattern in the library for bulk analysis."""
    all_data = []
    for category in get_available_categories():
        for name in get_patterns_by_category(category):
            all_data.append(get_pattern_data(category, name))
    return all_data
# Test block
if __name__ == "__main__":
    # 1. Basic Test: multiple insertions
    grid = np.zeros((10, 10), dtype=int)
    insert_pattern(grid, "Still Life", "Block", 1, 1)
    insert_pattern(grid, "Spaceship", "Glider", 5, 5)
    print("\n1. Basic Insertion:")
    print(grid)
    
    # 2. Toroidal Test
    # Placing a 1x3 Blinker at the last column (index 9).
    # Expected: The cells should wrap to columns 9, 0, and 1.
    toroidal_grid = np.zeros((10, 10), dtype=int)
    insert_pattern(toroidal_grid, "Oscillator", "Blinker", 5, 9)
    print(f"\n2. Toroidal Row 5: {toroidal_grid[5]}") 
    # 3. Features Test: Rotation
    # A horizontal Blinker rotated by 90 degrees should become vertical.

    rotation_grid = np.zeros((5, 5), dtype=int)
    insert_pattern(rotation_grid, "Oscillator", "Blinker", 1, 2, rotate=1)

    print(f"\n3. Rotation Test (Blinker rotated 90°):")
    print(rotation_grid)
    # 4. Library Check
    print("\n4. Library Content:")
    for cat in get_available_categories():
        print(f"Category '{cat}': {get_patterns_by_category(cat)}")

    # 5. Pattern Data Retrieval
    print("\n5. Pattern Data Retrieval:")
    pattern_info = get_pattern_data("Random", "Medium Chaos")
    if pattern_info:
        print(f"Name: {pattern_info['name']}")
        print(f"Live Cells: {pattern_info['live_cells']}")
        print(f"Density: {pattern_info['initial_density']}")
    #6. new complex patterns
    print("--- Testing New Complex Patterns ---")
    
    # List of the new patterns we want to verify
    new_patterns = [
        ("Still Life", "Snark"),
        ("Spaceship", "HWSS"),
        ("Complex", "Breeder"),
        ("Methuselah", "Acorn")
    ]
    
    for category, name in new_patterns:
        data = get_pattern_data(category, name)
        
        if data:
            print(f" Pattern: {name:10} | Category: {category:12} | Size: {str(data['dimensions']):8} | Live Cells: {data['live_cells']}")
        else:
            print(f" Error: Pattern '{name}' not found in category '{category}'")

    # Final check: print the Acorn matrix to see it clearly
    print("\nVisual check for 'Acorn':")
    acorn = SEED_DATA["Methuselah"]["Acorn"]
    # Simple trick to print 1 as '#' and 0 as '.'
    for row in acorn:
        print(" ".join(['#' if cell else '.' for cell in row]))




