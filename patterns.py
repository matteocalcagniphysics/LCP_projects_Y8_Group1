import numpy as np
"""
PATTERN LIBRARY MODULE
Usage:
    import patterns
    grid = patterns.insert_pattern(grid, "Category", "Name", row, col, rotate=0, flip=False)

Available Tools:
    - patterns.get_available_categories()
    - patterns.get_patterns_by_category("CategoryName")
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
    """
    Generates the standard Pentadecathlon (period 15 oscillator).
    Defined as a 3x8 block with specific internal gaps to allow oscillation.
    """
    p = np.ones((3, 8), dtype=int)
    p[1, 1:7] = 0  # Create the required internal hollow structure
    return p

def _create_glider_gun():
    """Generates the 36x9 matrix for the Gosper Glider Gun."""
    gun = np.zeros((9, 36), dtype=int)
    coords = [(4,0), (4,1), (5,0), (5,1), (2,12), (2,13), (3,11), (4,10), (5,10), (6,10), 
              (7,11), (8,12), (8,13), (5,14), (3,15), (4,16), (5,16), (6,16), (5,17), 
              (2,20), (2,21), (3,20), (3,21), (4,20), (4,21), (1,22), (5,22), (0,24), 
              (1,24), (5,24), (6,24), (2,34), (2,35), (3,34), (3,35)]
    for r, c in coords: 
        gun[r, c] = 1
    return gun

# Nested dictionary storing all patterns by category
SEED_DATA = {
    "Still Life": {
        "Block": np.array([[1, 1], [1, 1]]),
        "Beehive": np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]]),
        "Loaf": np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]])
    },
    "Oscillator": {
        "Blinker": np.array([[1, 1, 1]]),
        "Toad": np.array([[0, 0, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 0]]),
        "Pulsar": _create_pulsar(),
        "Pentadecathlon": _create_pentadecathlon()
    },
    "Spaceship": {
        "Glider": np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]]),
        "LWSS": np.array([[0, 1, 1, 1, 1], [1, 0, 0, 0, 1], [0, 0, 0, 0, 1], [1, 0, 0, 1, 0]])
    },
    "Complex": { 
        "Glider Gun": _create_glider_gun() 
    }
}


#Core functions

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

    # Copy the seed to avoid modifying the original database during transformations
    seed = SEED_DATA[category][name].copy()
    
    if flip: 
        seed = np.fliplr(seed)
    if rotate != 0: 
        seed = np.rot90(seed, k=rotate)

    s_rows, s_cols = seed.shape
    g_rows, g_cols = grid.shape

    # Iterate through the pattern and place live cells (1s) into the grid
    for r in range(s_rows):
        for c in range(s_cols):
            if seed[r, c] == 1:
                # Use modulo operator (%) to handle wrap-around at grid edges
                target_r = (row_origin + r) % g_rows
                target_c = (col_origin + c) % g_cols
                grid[target_r, target_c] = 1
    return grid

def get_available_categories():
    """Returns a list of all available pattern categories."""
    return list(SEED_DATA.keys())

def get_patterns_by_category(category):
    """Returns a list of pattern names within a specific category."""
    return list(SEED_DATA.get(category, {}).keys())
#Test
if __name__ == "__main__":
    print("--- FULL PATTERN LIBRARY TEST ---")
    
    # 1. Basic Test: Multiple insertions
    grid = np.zeros((10, 10), dtype=int)
    insert_pattern(grid, "Still Life", "Block", 1, 1)
    insert_pattern(grid, "Spaceship", "Glider", 5, 5)
    
    print("\n1. Basic Insertion (Block at 1,1 and Glider at 5,5):")
    print(grid)
    
    # 2. Crucial Test: Toroidal Logic (Wrap-around)
    # Placing a 1x3 Blinker at the last column (index 9).
    # Expected: The cells should wrap to columns 9, 0, and 1.
    toroidal_grid = np.zeros((10, 10), dtype=int)
    insert_pattern(toroidal_grid, "Oscillator", "Blinker", 5, 9)
    
    print("\n2. Toroidal Test (Blinker starting at col 9 - should wrap to col 0,1):")
    print(f"Row 5: {toroidal_grid[5]}") 
    
    # 3. Features Test: Rotation
    # A horizontal Blinker rotated by 90 degrees should become vertical.
    rotation_grid = np.zeros((5, 5), dtype=int)
    insert_pattern(rotation_grid, "Oscillator", "Blinker", 1, 2, rotate=1)
    print("\n3. Rotation Test (Blinker rotated 90°):")
    print(rotation_grid)
    
    # 4. Library Integrity Check
    print("\n4. Library Content Check:")
    for cat in get_available_categories():
        print(f"Category '{cat}': {get_patterns_by_category(cat)}")

