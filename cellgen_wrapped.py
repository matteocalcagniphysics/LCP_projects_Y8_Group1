import numpy as np

#Fixes the seed for replicability
np.random.seed(200)

#Number of rows and columns of the GoL grid
nrows, ncols = 10, 10

#Generates randomly the initial distribution (seed)
cells = np.random.choice(a=[True, False], size=(nrows, ncols)) 

#Extracts the indexes of living cells (True) and dead cells (False)
#I add [1, 1] in order to traslate the indexes and make them compatible with the padded matrix
alive_idx = np.argwhere(cells == True) + np.array([1, 1])
dead_idx = np.argwhere(cells == False) + np.array([1, 1])

#This create a wrapped surface, where top is identified with bottom and left with right
padded = np.pad(cells, pad_width=1, mode='wrap')

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

print(cells, '\n\n', newgen)

