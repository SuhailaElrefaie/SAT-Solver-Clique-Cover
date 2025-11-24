import subprocess
from argparse import ArgumentParser

# Global variables:
N = None # number of vertices
K = None # number of allowed cliques
EDGES = None # list of edges
NON_EDGES = None # list of non-edges

def load_instance(input_file_name):
    global N, K, EDGES, NON_EDGES
    edges = []
    with open(input_file_name, "r") as f:
        header = next(f).split()
        N = int(header[0])
        K = int(header[1])

        for line in f:
            line = line.strip()
            if not line:
                continue
            string_u, string_v = line.split()
            u = int(string_u)
            v = int(string_v)
            edges.append((u, v))

    # build adjacency matrix to find non-edges
    adj = [[False] * N for _ in range(N)]
    for (u, v) in edges:
        adj[u][v] = True
        adj[v][u] = True

    non_edges = []
    for u in range(N):
        for v in range(u + 1, N):
            if not adj[u][v]:
                non_edges.append((u, v))

    EDGES = edges
    NON_EDGES = non_edges

    return N, K, EDGES

def var_id(v, c):
    return v * K + c + 1 # DIMACS 

def encode():
    # CNF encoding of the clique cover problem.
    
    cnf = [] # list of clauses, each clause is a list of ints ending with 0
    nr_vars = N * K # total number of variables

    # 1) Each vertex has at least one clique
    for v in range(N):
        clause = [var_id(v, c) for c in range(K)]
        clause.append(0)
        cnf.append(clause)

    # 2) Each vertex has at most one clique
    for v in range(N):
        for c1 in range(K):
            for c2 in range(c1 + 1, K):
                cnf.append([-var_id(v, c1), -var_id(v, c2), 0])

    # 3) Non-adjacent vertices cannot share a clique
    for (u, v) in NON_EDGES:
        for c in range(K):
            cnf.append([-var_id(u, c), -var_id(v, c), 0])

    return cnf, nr_vars


def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as f:
        f.write(f"p cnf {nr_vars} {len(cnf)}\n")
        for clause in cnf:
            f.write(" ".join(str(lit) for lit in clause) + "\n")

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)

def print_result(result):
    for line in result.stdout.decode("utf-8").splitlines():
        print(line)

    if result.returncode == 20:
        print()
        print("############################################################")
        print("###########[ Instance is UNSAT for this k ]#################")
        print("############################################################")
        print()
        print(f"No clique cover with at most {K} cliques exists.")
        return

    # parse the model
    model = []
    for line in result.stdout.decode("utf-8").splitlines():
        if line.startswith("v"):
            parts = line.split()
            parts.remove("v")
            model.extend(int(v) for v in parts)
    model.remove(0)

    print()
    print("############################################################")
    print("###########[ Human readable clique cover ]##################")
    print("############################################################")
    print()

    assignment = [[] for _ in range(N)] # list of cliques

    for v in range(N):
        for c in range(K):
            idx = var_id(v, c) - 1
            if idx < len(model) and model[idx] > 0:
                assignment[v].append(c)

    # print clique-wise
    for c in range(K):
        clique_vertices = [v for v in range(N) if c in assignment[v]]
        if clique_vertices:
            print(f"Clique {c}: " + " ".join(str(v) for v in clique_vertices))

    print()
    # print vertex-wise
    for v in range(N):
        if assignment[v]:
            cols_str = ", ".join(str(c) for c in assignment[v])
        else:
            cols_str = "-"
        print(f"Vertex {v}: {cols_str}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help="The instance file",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help="Output file for the DIMACS format (i.e. the CNF formula).",
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help="The SAT solver to be used.",
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=[0, 1],
        help="Verbosity of the SAT solver used.",
    )

    args = parser.parse_args()
    load_instance(args.input) # get the input instance
    cnf, nr_vars = encode() # encode the problem to create CNF formula
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb) # call the SAT solver and get the result
    print_result(result) # interpret the result and print it in a human-readable format
