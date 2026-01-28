import numpy as np
import numpy.typing as npt #For writing the data types in the function definition

def cellgen(nrows: int, ncols: int):
    #Fixes the seed for replicability
    np.random.seed(200)

    #Number of rows and columns of the GoL grid
    nrows, ncols = 10, 10

    #Generates randomly the initial distribution (seed)
    cells = np.random.choice(a=[True, False], size=(nrows, ncols)) 

    #Extracts the indexes of living cells (True) and dead cells (False)
    alive_idx = np.argwhere(cells == True) 
    dead_idx = np.argwhere(cells == False) 

    return cells, alive_idx, dead_idx

def newgen(cells: npt.NDArray[np.bool_], alive_idx: npt.NDArray[np.intp], dead_idx: npt.NDArray[np.intp]):
    #This create a wrapped surface, where top is identified with bottom and left with right
    padded = np.pad(cells, pad_width=1, mode='wrap')

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

cells, alive, dead = cellgen(10, 8)
new = newgen(cells, alive, dead)
print(new)
