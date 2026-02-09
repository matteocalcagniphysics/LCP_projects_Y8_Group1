import numpy as np
import patterns 

# ==========================================
# 1. Grid preparation
# ==========================================
# Create a 20x20 world filled with zeros (dead cells)
rows, cols = 20, 20
grid = np.zeros((rows, cols), dtype=int)

print(f"World created: {rows}x{cols}")

# ==========================================
# 2. Inserting patterns
# ==========================================
# Insert a Blinker in the top-left area
patterns.insert_pattern(grid, "Oscillator", "Blinker", 2, 2)

# Insert a Glider rotated by 90 degrees
patterns.insert_pattern(grid, "Spaceship", "Glider", 10, 10, rotate=1)

# Test toroidal wrapping: a Block at column 19 wraps to the first columns
patterns.insert_pattern(grid, "Still Life", "Block", 5, 19)

print("\nGrid updated with patterns (Raw NumPy array):")
print(grid)

# ==========================================
# 3. Data analysis
# ==========================================
print("\n--- Analysis for Project Report ---")

# Retrieve metadata for a specific pattern
info = patterns.get_pattern_data("Complex", "Glider Gun")
if info:
    print(f"The '{info['name']}' contains {info['live_cells']} live cells.")

# Retrieve all library data for bulk statistics or plotting
all_library_data = patterns.get_all_library_data()
print(f"The patterns.py library contains {len(all_library_data)} available patterns.")

# Example: Calculate the average density of the entire library
total_density = sum(p['initial_density'] for p in all_library_data)
average_density = total_density / len(all_library_data)
print(f"Average density across all patterns: {average_density:.3f}")

# ==========================================
# 4. Visual representation
# ==========================================
print("\nVisual representation:")
visual_grid = np.where(grid == 1, "■", ".")
for row in visual_grid:
    print(" ".join(row))