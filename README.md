# A Formal Methods Approach to Decoy Allocation

We use the tools of deceptive synthesis and compositional synthesis from
formal methods to compute an approximately optimal allocation of decoys
in a cyberdefense application. The decoys are chosen in a way which maximizes 
the number of nodes from which the defender can ensure that the attacker reaches
a decoy and not a critical host.


File Description:

- `main.ipynb`: Jupyter notebook that illustrates the decoy 
    allocation algorithm proposed in the paper.

- `search.py`: Runs a brute-force search to find seeds for which interesting 
    cases of the algorithm can be observed. This file only generates a log file. 
    
- `analysis.py`: Analyzes the log to identify interesting cases. 




