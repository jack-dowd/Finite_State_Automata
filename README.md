# Finite_State_Automata
FSA Simulation for a 2D matrix, similar to Conway's Game of Life. Supports serial and parallel execution.

# Rules:
1. If alive ('O')
- Survives only if the number of alive neighbors is prime
- Otherwise it dies ('.').
2. If dead ('.')
- Becomes alive if the neighbor count is non‑zero and even
- Otherwise remains dead.

# Example usage:
- Serial execution:      python3 FSA.py -i time_step_0.dat -o my_time_step_100.dat
- Parallel execution:    python3 FSA.py -i time_step_0.dat -o my_time_step_100.dat -p 4
