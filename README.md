# Game of Life

### Authors
* [Andreacchio Pasquale](https://github.com/PasqualeAndreacchio), <pasquale.andreacchio@studenti.unipd.it>
* [Calcagni Matteo Renato](https://github.com/matteocalcagniphysics), <matteorenato.calcagni@studenti.unipd.it>
* [Gonzati Agostina](https://github.com/tinagonzati), <agostina.gonzati@studenti.unipd.it>
* [Lavarda Nicola](https://github.com/NicolaLavarda), <nicola.lavarda.1@studenti.unipd.it>



### Supervisors
* Prof. Marco Zanetti, <marco.zanetti@unipd.it>
* Prof. Samir Suweis, <samir.suweis@unipd.it>



### Description of the project
In this work we studied [Conway's Game of Life](http://en.wikipedia.org/wiki/Conway's_Game_of_Life) (GoF), which is a cellular automaton devised by the British mathematician John Horton Conway in 1970.
GoF consists of a grid of square cells, each of which is either alive or dead. Every cell interacts with its eight neighbours, which are the cells that are directly horizontally, vertically, or diagonally adjacent. At each step in time, the following transitions occur:

1. **Underpopulation**: any live cell with fewer than two live neighbours dies.
2. **Overcrowding**: any live cell with more than three live neighbours dies.
3. **Survival**: any live cell with two or three live neighbours lives, unchanged, to the next generation.
4. **Reproduction**: any dead cell with exactly three live neighbours becomes a live cell.

The game is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input.



### Implementation 
This project was developed using **Python** in a **Jupyter Notebook** environment.
This setup allowed a combined use of live code execution with text documentation and data visualization.
We implemented GoF's rules and started by using small grids and testing simple seeds, then we moved into bigger
grids and started testing more advanced patterns.
We finally implemented examples of three categories of patterns:
* Still lifes: stable configurations which don't change.
* Oscillators: they change following a cyclic sequence of states. After a certain number of generations, *period*,
               oscillators come back to their original state.
* Spaceships: like the oscillators, they change following a cyclic sequence of states; however, after a period, they
              come back to their original state, but in a different position of the board.
We provided an analysis of pattern in terms of frequency, replication and occupancy