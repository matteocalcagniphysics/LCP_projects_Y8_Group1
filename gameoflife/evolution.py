import numpy as np
import numpy.typing as npt #For writing the data types in the function definition

def newgen(cells: npt.NDArray[np.bool_]):
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
