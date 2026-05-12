"""
General notes to consider:
    * The input to these model-generating functions is shaped
      like the following example:

            e.g.
                 [[0,>,0,.,2],
                  [0,.,0,.,0],
                  [0,.,0,<,0]]

            0             -  an empty cell
            .             -  no inequality constraint
            <             -  left cell less than right cell
            >             -  left cell greater than rightcell
            range(1,n+1)  -  pre-set value at this position

      This grid represents the following Futoshiki board:

            e.g.
                -------------
                | _ > _ | 2 |
                | _ | _ | _ |
                | _ | _ < _ |
                -------------

      Note that the input is hence a list of lists where each inner list
      of length 2n - 1 represents a row of the board, where n is the dimension
      of the board.

    * Both models return a tuple (csp, variables):

      csp        - the CSP object representing the Futoshiki game
      variables  - a list of lists of variables corresponding to the
                   solved variables for csp. This list of lists is how
                   the solution to the csp is accessed.

    * An example of how models can be used in conjunction with the
      provided backend:

            e.g.
                 csp, variables = futoshiki_csp_model_1(board)
                 solver = BT(csp)
                 solver.bt_search(prop_FC)

      Upon completion of search, `variables[0][0].get_assigned_value()`
      will return the correct value in the top-left cell of the Futoshiki board.

"""
# CSC384 Lab 2 by Aashlesha Khanna
from typing import Any
from src import Variable, Constraint, CSP, BacktrackingSearch
import itertools


def _parse_grid(grid):
    """Parse the grid to extract n, cell values, and inequality constraints."""
    n = len(grid)
    # Each row has 2n-1 entries: n cell values and n-1 inequality symbols
    cells = []
    inequalities = []
    for i in range(n):
        row_cells = []
        for j in range(n):
            row_cells.append(grid[i][2 * j])
        cells.append(row_cells)
        # Extract inequalities between adjacent cells in this row
        for j in range(n - 1):
            symbol = grid[i][2 * j + 1]
            if symbol == '<':
                inequalities.append((i, j, i, j + 1, '<'))
            elif symbol == '>':
                inequalities.append((i, j, i, j + 1, '>'))
    return n, cells, inequalities


def _create_variables(n, cells):
    """Create Variable objects for each cell."""
    variables = []
    for i in range(n):
        row_vars = []
        for j in range(n):
            val = cells[i][j]
            if val != 0:
                dom = [val]
            else:
                dom = list(range(1, n + 1))
            var = Variable(f"V{i}{j}", dom)
            row_vars.append(var)
        variables.append(row_vars)
    return variables


def futoshiki_csp_model_1(grid: list[list[Any]]) -> tuple['CSP', list[list['Variable']]]:
    """
    Return a tuple consisting of the constraint satisfaction problem constructed
    according to the input Futoshiki puzzle grid, and a list of lists of Variable
    objects that represents the matrix of values corresponding to the input grid
    indexed from (0, 0) to (n-1, n-1).

    Constraints for model 1 are built using only binary inequality for both rows
    and columns. That is, all constraints are fixed to two variables in scope.

    :param grid: a list of lists of objects representing the Futoshiki grid, e.g.
                    grid = [[0,>,0,.,2], [0,.,0,.,0], [0,.,0,<,0]]
    """
    n, cells, inequalities = _parse_grid(grid)
    variables = _create_variables(n, cells)

    all_vars = []
    for row in variables:
        all_vars.extend(row)

    csp = CSP("Futoshiki_M1", all_vars)
    constraints = []

    # Binary not-equal constraints for rows
    for i in range(n):
        for j1 in range(n):
            for j2 in range(j1 + 1, n):
                v1 = variables[i][j1]
                v2 = variables[i][j2]
                con = Constraint(f"NEQ_R{i}_{j1}_{j2}", [v1, v2])
                sat_tuples = []
                for t in itertools.product(v1.domain(), v2.domain()):
                    if t[0] != t[1]:
                        sat_tuples.append(t)
                con.add_satisfying_tuples(sat_tuples)
                constraints.append(con)

    # Binary not-equal constraints for columns
    for j in range(n):
        for i1 in range(n):
            for i2 in range(i1 + 1, n):
                v1 = variables[i1][j]
                v2 = variables[i2][j]
                con = Constraint(f"NEQ_C{j}_{i1}_{i2}", [v1, v2])
                sat_tuples = []
                for t in itertools.product(v1.domain(), v2.domain()):
                    if t[0] != t[1]:
                        sat_tuples.append(t)
                con.add_satisfying_tuples(sat_tuples)
                constraints.append(con)

    # Binary inequality constraints
    for (r1, c1, r2, c2, symbol) in inequalities:
        v1 = variables[r1][c1]
        v2 = variables[r2][c2]
        con = Constraint(f"INEQ_{r1}{c1}_{r2}{c2}", [v1, v2])
        sat_tuples = []
        for t in itertools.product(v1.domain(), v2.domain()):
            if symbol == '<' and t[0] < t[1]:
                sat_tuples.append(t)
            elif symbol == '>' and t[0] > t[1]:
                sat_tuples.append(t)
        con.add_satisfying_tuples(sat_tuples)
        constraints.append(con)
# Note: The code for futoshiki_csp_model_1 and futoshiki_csp_model_2 is very similar, with the main difference being the use of binary not-equal constraints for rows and columns in model 1, and n-ary all-different constraints for rows and columns in model 2. The binary inequality constraints are constructed in the same way in both models.
    for con in constraints:
        csp.add_constraint(con)

    return csp, variables


def futoshiki_csp_model_2(grid: list[list[Any]]) -> tuple['CSP', list[list['Variable']]]:
    """
    Return a tuple consisting of the constraint satisfaction problem constructed
    according to the input Futoshiki puzzle grid, and a list of lists of Variable
    objects that represents the matrix of values corresponding to the input grid
    indexed from (0, 0) to (n-1, n-1).

    Constraints for model 2 are built using n-ary all-different constraints
    for both rows and columns. That is, there are 2*n + k total constraints:
    n all-different constraints for rows, n all-different constraints for columns,
    and k binary inequality constraints for the inequalities on the board.

    :param grid: a list of lists of objects representing the Futoshiki grid, e.g.
                    grid = [[0,>,0,.,2], [0,.,0,.,0], [0,.,0,<,0]]
    """
    n, cells, inequalities = _parse_grid(grid)
    variables = _create_variables(n, cells)
# Note: The code for futoshiki_csp_model_2 is very similar to futoshiki_csp_model_1, with the main difference being the use of n-ary all-different constraints instead of binary not-equal constraints for rows and columns. The binary inequality constraints are constructed in the same way in both models.
    all_vars = []
    for row in variables:
        all_vars.extend(row)

    csp = CSP("Futoshiki_M2", all_vars)
    constraints = []

    # N-ary all-different constraints for rows
    for i in range(n):
        row_vars = variables[i]
        con = Constraint(f"ALLDIFF_R{i}", row_vars)
        var_doms = [v.domain() for v in row_vars]
        sat_tuples = []
        for t in itertools.product(*var_doms):
            if len(set(t)) == len(t):
                sat_tuples.append(t)
        con.add_satisfying_tuples(sat_tuples)
        constraints.append(con)

    # N-ary all-different constraints for columns
    for j in range(n):
        col_vars = [variables[i][j] for i in range(n)]
        con = Constraint(f"ALLDIFF_C{j}", col_vars)
        var_doms = [v.domain() for v in col_vars]
        sat_tuples = []
        for t in itertools.product(*var_doms):
            if len(set(t)) == len(t):
                sat_tuples.append(t)
        con.add_satisfying_tuples(sat_tuples)
        constraints.append(con)

    # Binary inequality constraints
    for (r1, c1, r2, c2, symbol) in inequalities:
        v1 = variables[r1][c1]
        v2 = variables[r2][c2]
        con = Constraint(f"INEQ_{r1}{c1}_{r2}{c2}", [v1, v2])
        sat_tuples = []
        for t in itertools.product(v1.domain(), v2.domain()):
            if symbol == '<' and t[0] < t[1]:
                sat_tuples.append(t)
            elif symbol == '>' and t[0] > t[1]: 
                sat_tuples.append(t)
        con.add_satisfying_tuples(sat_tuples)
        constraints.append(con)
# Note: The code for futoshiki_csp_model_2 is very similar to futoshiki_csp_model_1, with the main difference being the use of n-ary all-different constraints instead of binary not-equal constraints for rows and columns. The binary inequality constraints are constructed in the same way in both models.
    for con in constraints:
        csp.add_constraint(con)

    return csp, variables