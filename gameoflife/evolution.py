import numpy as np
import numpy.typing as npt #For writing the data types in the function definition
import warnings

def newgen(cells: npt.NDArray[np.bool_]):
    
    # Anti bug checks
    if cells.ndim != 2:
        raise ValueError(f"Input array must be 2D, but got {cells.ndim}D.")
    if cells.size == 0:
        print("Input array is empty")
        return cells.copy()
    if cells.dtype != bool:
        warnings.warn("Input array has non-boolean values. It will be interpreted")
        cells = cells.astype(bool)
    
    #This create a wrapped surface, where top is identified with bottom and left with right
    padded = np.pad(cells, pad_width=1, mode='wrap')
    
    #Extracts the indexes of living cells (True) and dead cells (False)
    alive_idx = np.argwhere(cells == True) 
    dead_idx = np.argwhere(cells == False) 

    #I add [1, 1] in order to traslate the indexes and make them compatible with the padded matrix
    alive_idx += np.array([1, 1])
    dead_idx += np.array([1, 1])

    #Make a copy of the grid, i.e. the next generation (necessary to make the code work)
    newgen = np.copy(cells)

    #Calculates the evolution of the living cells
    for index in alive_idx:
        neig = padded[index[0]-1:index[0]+2, index[1]-1:index[1]+2]
        #The -1 is to delete the cell I am considering from the counts of alive neighbors
        nalive = len(neig[neig == True]) - 1
        if (nalive != 2 and nalive != 3):
            newgen[index[0]-1, index[1]-1] = False

    #Calculates the evolution of the dead cells
    for index in dead_idx:
        neig = padded[index[0]-1:index[0]+2, index[1]-1:index[1]+2]
        #The -1 is to delete the cell I am considering from the counts of alive neighbors
        nalive = len(neig[neig == True]) 
        if (nalive == 3):
            newgen[index[0]-1, index[1]-1] = True

    return newgen

def evolution(genzero: npt.NDArray[np.bool_], timesteps: int):

    # Anti bug checks
    if not isinstance(timesteps, int):
        raise TypeError(f"timesteps must be an integer, got {type(timesteps).__name__}.")
    if timesteps < 0:
        raise ValueError("timesteps cannot be negative.")
    if genzero.dtype != bool:
        warnings.warn("Input array has non-boolean values. It will be interpreted")
        genzero = genzero.astype(bool)
    
    # Creates a list containing the configurations for each timestep in the evolution
    timeline = []
    
    # Initialize the current state with the generation zero
    current_state = genzero
    timeline.append(current_state) # Include the starting state in the timeline
    
    # Calculates the configuration for each timestep
    for t in range(timesteps):
        # ERROR FIX: We must use 'current_state' as input, not 'genzero' repeatedly
        new = newgen(cells=current_state)
        
        # Update the current state for the next iteration
        current_state = new
        
        timeline.append(new)
    
    return timeline
