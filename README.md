# decoy-allocation-problem

Code for AIJ 2023 submission. 


## Installation

Use docker image: `abhibp1993/dtptb-reach:latest`


## Description of files

- `exp1_gridworld/`: Directory containing code for the experiment on gridworld domain.
   - `main.py`: Main file for running experiment.
   - `plots_for_paper.py`: Code to generate plots for paper.
- `exp2_randomgame/`: Directory containing code for the experiment on randomly generated game graphs.
    - `main.py`: Main file for running experiments.
    - `game_generator.py`: Code for generating random games.
    - `plots_for_paper.py`: Code to generate plots for paper.
    - `investigate_seed1357.py, investigate_seed1745.py`: Code for investigating the effect of decoys in games. 
- `game.py`: Representation of game on graph.
- `ioutils.py`: Utilities for saving and loading games. 
- `solvers.py`: Algorithms for computing DSWin, DASWin, and greedy DecoyAllocation.
- `vizutils.py`: Utilities for visualizing the game graph and the decoy allocation.





