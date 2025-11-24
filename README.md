# Clique Cover
This is a project for Propositional and Predicate Logic (NAIL062). The provided Python code encodes, solves, and decodes the "Clique Cover" problem via reduction to SAT.

## Problem Description
Input:
-An undirected simple graph G=(V,E) with vertices 0,..,n-1
-A positive integer k

Question: Does the graph have a clique cover of size at most k?

In graph theory, a clique cover is a collection of cliques that cover the whole graph.
This means, each vertex is assigned to exactly one clique index {0,..,k-1}, and any two vertices who share the same index must be adjacent in G.

## Encoding 
I use boolean variables X(v,c) meaning “vertex v is assigned to clique c”.
Each variable is mapped to a DIMACS integer:
var_id(v,c) = v * k + c + 1
The total number of variables is N * K.
Clauses:
Each vertex is in at least one clique
For each vertex v:
X(v,0) OR X(v,1) OR ... OR X(v,k-1)
Each vertex is in at most one clique
For each vertex v, for all c1 < c2:
NOT X(v,c1) OR NOT X(v,c2)
Non-adjacent vertices cannot share a clique
For every non-edge (u,v) and every clique index c:
NOT X(u,c) OR NOT X(v,c)
This guarantees that each assigned group is a valid clique.

## User Documentation
### Script Usage
The main script is: clique_cover.py
#### Input File Format
The input file must be in this format:
n k
u v
u v
...
The first line contains the number of vertices n and the number of allowed cliques k.
#### Running the Script
Arguments:
-i : path to input file
-o : output CNF file name
-s : SAT solver binary name (default: glucose-syrup)
-v : solver verbosity (0 or 1)
#### Output
If the instance is UNSAT, the script prints that no clique cover with at most k cliques exists.
If SAT, the script prints:
each clique and the vertices inside it
each vertex and the clique assigned to it

## Example Instances
small-sat.in
A small graph that has a clique cover of size k.

small-unsat.in
A small graph that does not have a clique cover of size k.

medium-* and large-*
Larger random graphs used for experiments.

## Experiments
I tested graphs of different sizes and densities.
Small graphs solve instantly.
Medium graphs (around 40 to 60 vertices) usually solve in under a second.
Larger graphs (around 70 to 80 vertices) typically solve in 1 to 3 seconds.

I attempted to generate satisfiable instances that take at least 10 seconds:
- I tried many random graphs with different sizes
- I tried different edge densities
- I tried k values near the satisfiable/unsatisfiable boundary
However, on my machine Glucose solved all satisfiable instances quickly.
Since I could not produce a satisfiable instance that takes 10 seconds or more, I included the largest ones I tested and described the attempts here, as allowed by the assignment.
