import numpy as np

#Fixes the seed for replicability
np.random.seed(200)

#Number of rows and columns of the GoL grid
nrows, ncols = 10, 10 

#Generates randomly the initial distribution (seed)
cells = np.random.choice(a=[True, False], size=(nrows, ncols)) 

#Extracts the indexes of living cells (True) and dead cells (False)
alive_idx = np.argwhere(cells == True)
dead_idx = np.argwhere(cells == False)

#Extract border cells
alive_idx_border = alive_idx[(alive_idx[:, 0] == 0) | (alive_idx[:, 1] == 0) 
                             | (alive_idx[:, 0] == nrows-1) | (alive_idx[:, 1] == ncols-1)]
dead_idx_border = dead_idx[(dead_idx[:, 0] == 0) | (dead_idx[:, 1] == 0)
                           | (dead_idx[:, 0] == nrows-1) | (dead_idx[:, 1] == ncols-1)]

#Extracts the insider cells
alive_idx_inside = alive_idx[(alive_idx[:, 0] != 0) & (alive_idx[:, 1] != 0)
                             & (alive_idx[:, 0] != nrows-1) & (alive_idx[:, 1] != ncols-1)]
dead_idx_border = dead_idx[(dead_idx[:, 0] != 0) & (dead_idx[:, 1] != 0)
                           & (dead_idx[:, 0] != nrows-1) & (dead_idx[:, 1] != ncols-1)]

#Make a copy of the grid, i.e. the next generation
newgen = np.copy(cells)

for item in alive_idx_inside:
    neig = cells[item[0]-1:item[0]+2, item[1]-1:item[1]+2]
    #The -1 is to delete the cell I am considering from the counts of alive neighbors
    nalive = len(neig[neig == True]) - 1
    if (nalive != 2 and nalive != 3):
        newgen[item[0], item[1]] = False

