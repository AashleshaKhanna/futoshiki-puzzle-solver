import itertools

from src import (
    CSP,
    Variable,
    Constraint,
    BacktrackingSearch,
)

from test_utils import TestOutput, set_timeout, reset_timeout

try:
    import propagators as student_propagators
    import futoshiki_csp as student_models
except ImportError:
    pass


# Global timeout constant
TIMEOUT = 60

#######################################
# EXAMPLE CSP CONSTRUCTIONS
#######################################
def queens_check(qi, qj, i, j):
    """ Return true if i and j can be assigned to the queen
        in row qi and row qj respectively. """
    return i != j and abs(i - j) != abs(qi - qj)


def n_queens(n):
    """Construct an n-queens CSP."""
    dom = list(range(1, n + 1))
    vars_ = [Variable(f"Q{i}", dom) for i in dom]
    cons = []
    for qi in range(n):
        for qj in range(qi + 1, n):
            c_name = f"C(Q{qi + 1},Q{qj + 1})"
            c = Constraint(c_name, [vars_[qi], vars_[qj]])
            sat_tuples = []
            for t in itertools.product(dom, repeat=2):
                if queens_check(qi, qj, t[0], t[1]):
                    sat_tuples.append(t)
            c.add_satisfying_tuples(sat_tuples)
            cons.append(c)
    csp = CSP(f"{n}-Queens", vars_)
    for c_ in cons:
        csp.add_constraint(c_)
    return csp


def w_eq_sum_x_y_z(values):
    w, x, y, z = values
    return w == (x + y + z)


def even_odd_csp():
    """Construct a simple CSP where nothing is pruned via GAC."""
    dom = (1, 2, 3, 4)
    vars = []
    vars.append(Variable('X', list(dom)))
    vars.append(Variable('Y', list(dom)))

    con1 = Constraint("X+Y odd", [vars[0], vars[1]])
    sat_tuples = []
    for t in itertools.product(dom, dom):
        if (t[0] + t[1]) % 2 == 1:
            sat_tuples.append(t)
    con1.add_satisfying_tuples(sat_tuples)
    csp = CSP("X + Y odd", vars)
    csp.add_constraint(con1)

    return csp


def three_var_csp():
    dom = (1, 2, 3, 4)
    vars = []
    vars.append(Variable('W', list(dom)))
    vars.append(Variable('X', list(dom)))
    vars.append(Variable('Y', list(dom)))
    vars.append(Variable('Z', list(dom)))

    sat_tuples = []
    con1 = Constraint("W + X < Y", [vars[0], vars[1], vars[2]])
    for t in itertools.product(dom, repeat=3):
        if t[0] + t[1] < t[2]:
            sat_tuples.append(t)

    con1.add_satisfying_tuples(sat_tuples)
    sat_tuples = []
    con2 = Constraint("X + Y < Z", [vars[1], vars[2], vars[3]])
    for t in itertools.product(dom, repeat=3):
        if t[0] + t[1] < t[2]:
            sat_tuples.append(t)
    con2.add_satisfying_tuples(sat_tuples)
    csp = CSP("Tiny comparator", vars)
    csp.add_constraint(con1)
    csp.add_constraint(con2)

    return csp


def three_var_csp2():
    dom = (1, 2, 3, 4)
    vars = []
    vars.append(Variable('W', list(dom)))
    vars.append(Variable('X', list(dom)))
    vars.append(Variable('Y', list(dom)))
    vars.append(Variable('Z', list(dom)))

    sat_tuples = []
    con1 = Constraint("W < X", [vars[0], vars[1]])
    for t in itertools.product(dom, repeat=2):
        if t[0] < t[1]:
            sat_tuples.append(t)

    con1.add_satisfying_tuples(sat_tuples)
    sat_tuples = []
    con2 = Constraint("W + X + Y < Z", [vars[0], vars[1], vars[2], vars[3]])
    for t in itertools.product(dom, repeat=4):
        if t[0] + t[1] + t[2] < t[3]:
            sat_tuples.append(t)
    con2.add_satisfying_tuples(sat_tuples)
    csp = CSP("Tiny comparator2", vars)
    csp.add_constraint(con1)
    csp.add_constraint(con2)

    return csp


def tiny_adder_csp():
    """Construct a simple CSP where FC and GAC differ, Assign x = 3 when testing."""
    dom = (1, 2, 3, 4)
    vars = []
    vars.append(Variable('X', list(dom)))
    vars.append(Variable('Y', list(dom)))
    vars.append(Variable('Z', list(dom)))
    con1 = Constraint("X + Y = Z", [vars[0], vars[1], vars[2]])
    con2 = Constraint("X > Y", [vars[0], vars[1]])
    sat1 = []
    for t in itertools.product(dom, repeat=3):
        if t[0] + t[1] == t[2]:
            sat1.append(t)
    con1.add_satisfying_tuples(sat1)
    sat2 = []
    for t in itertools.product(dom, dom):
        if t[0] > t[1]:
            sat2.append(t)
    con2.add_satisfying_tuples(sat2)

    csp = CSP("Tiny adder", vars)
    csp.add_constraint(con1)
    csp.add_constraint(con2)
    return csp


def check_solution(sudoku_variable_array, greater_thans, less_thans):
    """
    Takes in a futoshiki_variable_array, as specified in futoshiki_csp
    variable_array[i][j] is the Variable (object) that represents the value to be placed in cell i,j of the futoshiki board.
    Returns True if the solution is a valid solution;
    Returns False otherwise.
    """

    ## Check the rows
    for i in range(7):
        row_sol = []
        for j in range(7):
            row_sol.append(sudoku_variable_array[i][j].get_assigned_value())
        if not check_list(row_sol):
            return False
    for j in range(7):
        col_sol = []
        for i in range(7):
            col_sol.append(sudoku_variable_array[i][j].get_assigned_value())
        if not check_list(col_sol):
            return False

    for g in greater_thans:
        if g[0].get_assigned_value() < g[1].get_assigned_value():
            return False

    for l in less_thans:
        if l[0].get_assigned_value() > l[1].get_assigned_value():
            return False

    return True


def check_list(solution_list):
    if None in solution_list:
        return False
    solution_list.sort()
    return solution_list == list(range(1, 8))


#######################################
# TEST FUNCTIONS
#######################################
def test_simple_fc(stu_propagators, test_name) -> TestOutput:
    """
    Tests FC after the first queen is placed in position 1.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        # Build CSP
        csp = n_queens(8)
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(1)
        # Propagate
        stu_propagators.prop_FC(csp, newVar=curr_vars[0])
        # Check
        expected = [
            [1],
            [3, 4, 5, 6, 7, 8],
            [2, 4, 5, 6, 7, 8],
            [2, 3, 5, 6, 7, 8],
            [2, 3, 4, 6, 7, 8],
            [2, 3, 4, 5, 7, 8],
            [2, 3, 4, 5, 6, 8],
            [2, 3, 4, 5, 6, 7]
        ]
        var_domain = [v.cur_domain() for v in curr_vars]
        if var_domain == expected:
            score = max_score
            output = "FC propagation successful"
        else:
            score = 0
            errors = "Failed simple FC test: variable domains differ"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests FC after the first queen is placed in position 1.",
        output=output,
        errors=errors
    )


def test_simple_gac(stu_propagators, test_name) -> TestOutput:
    """
    Tests GAC after the first queen is placed in position 1.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(1)
        stu_propagators.prop_GAC(csp, newVar=vars_[0])
        expected = [
            [1],
            [3, 4, 5, 6, 7, 8],
            [2, 4, 5, 6, 7, 8],
            [2, 3, 5, 6, 7, 8],
            [2, 3, 4, 6, 7, 8],
            [2, 3, 4, 5, 7, 8],
            [2, 3, 4, 5, 6, 8],
            [2, 3, 4, 5, 6, 7]
        ]
        var_domain = [v.cur_domain() for v in vars_]
        if var_domain == expected:
            score = max_score
            output = "GAC propagation successful"
        else:
            score = 0
            errors = "Failed simple GAC test: variable domains differ"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests GAC after the first queen is placed in position 1.",
        output=output,
        errors=errors
    )


def three_queen_gac(stu_propagators, test_name) -> TestOutput:
    """
    A 3-queen scenario that yields different prunings for FC vs GAC.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(4)
        vars_[2].assign(1)
        vars_[7].assign(5)
        stu_propagators.prop_GAC(csp)
        expected = [
            [4], [6, 7, 8], [1], [3, 8],
            [6, 7], [2, 8], [2, 3, 7, 8], [5]
        ]
        var_vals = [v.cur_domain() for v in vars_]
        if var_vals == expected:
            score = max_score
            output = "Three queens GAC propagation successful"
        else:
            score = 0
            errors = "Failed three queens GAC test: domain mismatch"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="A 3-queen scenario that yields different prunings for FC vs GAC.",
        output=output,
        errors=errors
    )


def three_queen_fc(stu_propagators, test_name) -> TestOutput:
    """
    Similar 3-queen scenario but checking FC specifically.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(4)
        vars_[2].assign(1)
        vars_[7].assign(5)
        stu_propagators.prop_FC(csp)
        expected = [
            [4], [6, 7, 8], [1], [3, 6, 8],
            [6, 7], [2, 6, 8], [2, 3, 7, 8], [5]
        ]
        var_vals = [v.cur_domain() for v in vars_]
        if var_vals == expected:
            score = max_score
            output = "Three queens FC propagation successful"
        else:
            score = 0
            errors = "Failed three queens FC test: domain mismatch"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Similar 3-queen scenario but checking FC specifically.",
        output=output,
        errors=errors
    )


def test_prop_1(propagator, test_name) -> TestOutput:
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])
        w = Variable('W', [1, 2, 3, 4])

        c1 = Constraint('C1', [x, y, z])
        # c1 is constraint x == y + z. Below are all of the satisfying tuples
        c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

        c2 = Constraint('C2', [w, x, y, z])
        # c2 is constraint w == x + y + z.
        var_doms = []
        for v in [w, x, y, z]:
            var_doms.append(v.domain())

        sat_tuples = []
        for t in itertools.product(*var_doms):
            if w_eq_sum_x_y_z(t):
                sat_tuples.append(t)

        c2.add_satisfying_tuples(sat_tuples)

        simple_csp = CSP("SimpleEqs", [x, y, z, w])
        simple_csp.add_constraint(c1)
        simple_csp.add_constraint(c2)

        btracker = BacktrackingSearch(simple_csp)
        # btracker.trace_on()

        set_timeout(TIMEOUT)
        btracker.search(propagator)
        curr_vars = simple_csp.get_all_vars()
        answer = [[2], [1], [1], [4]]
        var_vals = [x.cur_domain() for x in curr_vars]
        reset_timeout()
        if var_vals != answer:
            score = 0
            errors = f"Failed while testing a propagator ({test_name}): variable domains don't match expected results"
        else:
            score = max_score
            output = f"Test {test_name} passed successfully"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description=f"Tests a propagator ({test_name}) on a simple CSP.",
        output=output,
        errors=errors
    )


def test_prop_2(propagator, test_name) -> TestOutput:
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])

        c1 = Constraint('C1', [x, y, z])
        c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

        c2 = Constraint('C2', [x, y])
        c2.add_satisfying_tuples([[1, 2], [2, 1], [2, 3], [3, 2]])

        c3 = Constraint('C3', [y, z])
        c3.add_satisfying_tuples([[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]])

        simple_csp = CSP("ParityEqs", [x, y, z])
        simple_csp.add_constraint(c1)
        simple_csp.add_constraint(c2)
        simple_csp.add_constraint(c3)

        btracker = BacktrackingSearch(simple_csp)
        # btracker.trace_on()

        set_timeout(TIMEOUT)
        btracker.search(propagator)
        reset_timeout()
        curr_vars = simple_csp.get_all_vars()
        answer = [[3], [2], [1]]
        var_vals = [x.cur_domain() for x in curr_vars]
        if var_vals != answer:
            score = 0
            errors = f"Failed while testing a propagator ({test_name}): variable domains don't match expected results"
        else:
            score = max_score
            output = f"Test {test_name} passed successfully"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description=f"Tests a propagator ({test_name}) on a CSP with parity constraints.",
        output=output,
        errors=errors
    )


def test_prop_3(propagator, test_name) -> TestOutput:
    """
    Tests a CSP with parity constraints.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        z = Variable('Z', [1, 2, 3])

        c1 = Constraint('C1', [x, y, z])
        c1.add_satisfying_tuples([[2, 1, 1], [3, 1, 2], [3, 2, 1]])

        c2 = Constraint('C2', [y, z])
        c2.add_satisfying_tuples([[1, 1], [1, 3], [2, 2], [3, 1], [3, 3]])

        c3 = Constraint('C3', [x, y])
        c3.add_satisfying_tuples([[1, 1], [1, 3], [2, 2], [3, 1], [3, 3]])

        simple_csp = CSP("ParityEqs", [x, y, z])
        simple_csp.add_constraint(c1)
        simple_csp.add_constraint(c2)
        simple_csp.add_constraint(c3)

        btracker = BacktrackingSearch(simple_csp)
        # btracker.trace_on()

        set_timeout(TIMEOUT)
        btracker.search(propagator)
        reset_timeout()
        curr_vars = simple_csp.get_all_vars()
        answer = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        var_vals = [v.cur_domain() for v in curr_vars]

        if var_vals != answer:
            score = 0
            errors = f"Failed while testing a propagator ({test_name}): variable domains don't match expected results"
        else:
            score = max_score
            output = f"Test {test_name} passed successfully"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description=f"Tests a propagator ({test_name}) on a CSP with parity constraints.",
        output=output,
        errors=errors
    )


def test_tiny_adder_fc(stu_propagators, test_name) -> TestOutput:
    max_score = 5
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = tiny_adder_csp()
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(3)
        set_timeout(TIMEOUT)
        stu_propagators.prop_FC(csp, newVar=curr_vars[0])
        reset_timeout()
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[3], [1, 2], [1, 2, 3, 4]]
        if var_domain == answer:
            score = max_score
            output = "Tiny adder FC test passed"
        else:
            score = 0
            errors = "Failed small FC test: variable domains don't match expected results"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests FC on a tiny adder CSP.",
        output=output,
        errors=errors
    )


def test_tiny_adder_gac(stu_propagators, test_name) -> TestOutput:
    max_score = 5
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = tiny_adder_csp()
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(3)
        set_timeout(TIMEOUT)
        stu_propagators.prop_GAC(csp, newVar=curr_vars[0])
        reset_timeout()
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[3], [1], [4]]
        if var_domain == answer:
            score = max_score
            output = "Tiny adder GAC test passed"
        else:
            score = 0
            errors = "Failed small GAC test: variable domains don't match expected results"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests GAC on a tiny adder CSP.",
        output=output,
        errors=errors
    )


def test_no_pruning_fc(stu_propagators, test_name) -> TestOutput:
    max_score = 3
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = three_var_csp()
        curr_vars = csp.get_all_vars()
        curr_vars[1].assign(3)
        set_timeout(TIMEOUT)
        stu_propagators.prop_FC(csp, newVar=curr_vars[1])
        reset_timeout()
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[1, 2, 3, 4], [3], [1, 2, 3, 4], [1, 2, 3, 4]]
        if var_domain == answer:
            score = max_score
            output = "FC test with no pruning passed"
        else:
            score = 0
            errors = "Failed FC test that should have resulted in no pruning"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests FC on a CSP that should result in no pruning.",
        output=output,
        errors=errors
    )


def test_no_pruning2_fc(stu_propagators, test_name) -> TestOutput:
    max_score = 3
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = three_var_csp2()
        curr_vars = csp.get_all_vars()
        curr_vars[1].assign(1)
        curr_vars[2].assign(1)
        set_timeout(TIMEOUT)
        stu_propagators.prop_FC(csp, newVar=curr_vars[2])
        reset_timeout()
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[1, 2, 3, 4], [1], [1], [1, 2, 3, 4]]
        if var_domain == answer:
            score = max_score
            output = "FC test with no pruning (variant 2) passed"
        else:
            score = 0
            errors = "Failed FC test that should have resulted in no pruning"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests FC on a CSP that should result in no pruning (variant 2).",
        output=output,
        errors=errors
    )


def test_no_pruning_gac(stu_propagators, test_name) -> TestOutput:
    max_score = 6
    score = 0
    output = ""
    errors = ""
    
    try:
        csp = even_odd_csp()
        set_timeout(TIMEOUT)
        stu_propagators.prop_GAC(csp)
        reset_timeout()
        curr_vars = csp.get_all_vars()
        var_domain = [x.cur_domain() for x in curr_vars]
        answer = [[1, 2, 3, 4], [1, 2, 3, 4]]
        if var_domain == answer:
            score = max_score
            output = "GAC test with no pruning passed"
        else:
            score = 0
            errors = "Failed GAC test that should have resulted in no pruning"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests GAC on a CSP that should result in no pruning.",
        output=output,
        errors=errors
    )

def test_dwo_gac(stu_propagators, test_name) -> TestOutput:
    max_score = 5
    score = 0
    output = ""
    errors = ""

    try:
        csp = n_queens(6)
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(2)
        set_timeout(TIMEOUT)
        pruned = stu_propagators.prop_GAC(csp, newVar=curr_vars[0])
        if not pruned[0]:
            score = 0
            errors = "Failed a GAC test: returned DWO too early"
        else:
            curr_vars[1].assign(5)
            pruned = stu_propagators.prop_GAC(csp, newVar=curr_vars[1])
            reset_timeout()
            if pruned[0]:
                score = 0
                errors = "Failed a GAC test: should have resulted in a DWO"
            else:
                score = max_score
                output = "GAC DWO test passed"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests GAC on a CSP that should result in a domain wipeout.",
        output=output,
        errors=errors
    )


def test_dwo_fc(stu_propagators, test_name) -> TestOutput:
    max_score = 5
    score = 0
    output = ""
    errors = ""

    try:
        csp = n_queens(6)
        curr_vars = csp.get_all_vars()
        curr_vars[0].assign(2)
        set_timeout(TIMEOUT)
        pruned = stu_propagators.prop_FC(csp, newVar=curr_vars[0])
        if not pruned[0]:
            score = 0
            errors = "Failed a FC test: returned DWO too early"
        else:
            curr_vars[1].assign(5)
            pruned = stu_propagators.prop_FC(csp, newVar=curr_vars[1])
            if not pruned[0]:
                score = 0
                errors = "Failed a FC test: returned DWO too early"
            else:
                curr_vars[4].assign(1)
                pruned = stu_propagators.prop_FC(csp, newVar=curr_vars[4])
                reset_timeout()
                if pruned[0]:
                    score = 0
                    errors = "Failed a FC test: should have resulted in a DWO"
                else:
                    score = max_score
                    output = "FC DWO test passed"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests FC on a CSP that should result in a domain wipeout.",
        output=output,
        errors=errors
    )


def test_futoshiki_model_1(stu_models, test_name) -> TestOutput:
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        board = [[3, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 1]]
        answer = [[3], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                  [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                  [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                  [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1]]

        set_timeout(TIMEOUT)
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        reset_timeout()
        if csp is None or len(var_array) == 0:
            score = 0
            errors = "Failed to import a board into model 1"
        else:
            lister = []
            for i in range(4):
                for j in range(4):
                    lister.append(var_array[i][j].cur_domain())

            if lister != answer:
                score = 0
                errors = "Failed to import a board into model 1: initial domains don't match"
            else:
                score = max_score
                output = "Futoshiki model 1 board import successful"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests importing a board into Futoshiki model 1.",
        output=output,
        errors=errors
    )


def test_futoshiki_model_2(stu_models, test_name) -> TestOutput:
    """
    Checks that importing a board into model 2 works as expected.
    Passing this test is a prerequisite for passing check_model_2_constraints.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        board = [[3, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 1]]
        answer = [[3], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                  [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                  [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4],
                  [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1]]

        set_timeout(TIMEOUT)
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        reset_timeout()
        if csp is None:
            score = 0
            errors = "Failed to construct CSP"
        else:
            lister = [var_array[i][j].cur_domain() for i in range(4) for j in range(4)]
            if lister != answer:
                score = 0
                errors = "Failed to import a board into model 2: initial domains don't match"
            else:
                score = max_score
                output = "Futoshiki model 2 board import successful"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests importing a board into Futoshiki model 2.",
        output=output,
        errors=errors
    )


def check_model_1_constraints_enum_ineqs(stu_models, test_name) -> TestOutput:
    """
    Checks that model 1 constraints pass when all different, and fail when not all different.
    """
    max_score = 1
    score = max_score
    output = "Model 1 constraints enum ineqs check passed"
    errors = ""

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that model 1 constraints pass when all different, and fail when not all different.",
        output=output,
        errors=errors
    )


def check_model_2_constraints_enum_ineqs(stu_models, test_name) -> TestOutput:
    """
    Checks that model 2 constraints pass when all different, and fail when not all different.
    """
    max_score = 1
    score = max_score
    output = "Model 2 constraints enum ineqs check passed"
    errors = ""

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that model 2 constraints pass when all different, and fail when not all different.",
        output=output,
        errors=errors
    )


def check_model_1_constraints_enum_rewscols(stu_models, test_name) -> TestOutput:
    """
    Checks that model 1 constraints pass when all different, and fail when not all different.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        board = [[3, '.', 2, '.', 0],
                 [1, '.', 3, '.', 0],
                 [0, '.', 0, '.', 0]]

        set_timeout(TIMEOUT)
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        reset_timeout()
        if csp is None:
            score = 0
            errors = "Failed to construct Model 1"
        else:
            for cons in csp.get_all_cons():
                all_vars = cons.get_scope()
                taken = []
                domain_list = []
                should_pass = []
                should_fail = []
                for va in all_vars:
                    domain_list.append(va.cur_domain())
                    if len(va.cur_domain()) == 1:
                        taken.append(va.cur_domain()[0])
                for i in range(len(all_vars)):
                    va = all_vars[i]
                    domain = domain_list[i]
                    if len(domain) == 1:
                        should_pass.append(domain[0])
                        should_fail.append(domain[0])
                    else:
                        for i in range(1, 4):
                            if i in domain and i in taken:
                                should_fail.append(i)
                                break
                        for i in range(1, 4):
                            if i in domain and i not in taken:
                                should_pass.append(i)
                                taken.append(i)
                                break
                if cons.check(should_fail) != cons.check(should_pass):
                    if cons.check(should_fail) or not cons.check(should_pass):
                        if not cons.check(should_fail):
                            score = 0
                            errors = f"Failed constraint test in model 1: {cons} should be falsified by {should_fail}"
                            break
                        if cons.check(should_pass):
                            score = 0
                            errors = f"Failed constraint test in model 1: {cons} should be satisfied by {should_fail}"
                            break
            else:
                score = max_score
                output = "Model 1 constraints enum rewscols check passed"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that model 1 constraints pass when all different, and fail when not all different.",
        output=output,
        errors=errors
    )


def check_model_2_constraints_enum_rewscols(stu_models, test_name) -> TestOutput:
    """
    Checks that model 2 constraints pass when all different, and fail when not all different.
    """
    max_score = 1
    score = 0
    output = ""
    errors = ""
    
    try:
        board = [[3, '.', 2, '.', 0],
                 [1, '.', 3, '.', 0],
                 [0, '.', 0, '.', 0]]

        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        if csp is None:
            score = 0
            errors = "Tried to make CSP, got nothing"
        else:
            for cons in csp.get_all_cons():
                all_vars = cons.get_scope()
                taken = []
                domain_list = []
                should_pass = []
                should_fail = []
                for va in all_vars:
                    domain_list.append(va.cur_domain())
                    if len(va.cur_domain()) == 1:
                        taken.append(va.cur_domain()[0])
                for i in range(len(all_vars)):
                    va = all_vars[i]
                    domain = domain_list[i]
                    if len(domain) == 1:
                        should_pass.append(domain[0])
                        should_fail.append(domain[0])
                    else:
                        for i in range(1, 4):
                            if i in domain and i in taken:
                                should_fail.append(i)
                                break
                        for i in range(1, 4):
                            if i in domain and i not in taken:
                                should_pass.append(i)
                                taken.append(i)
                                break
                if cons.check(should_fail) != cons.check(should_pass):
                    if cons.check(should_fail) or not cons.check(should_pass):
                        if not cons.check(should_fail):
                            score = 0
                            errors = f"Failed constraint test in model 2: {cons} should be falsified by {should_fail}"
                            break
                        if cons.check(should_pass):
                            score = 0
                            errors = f"Failed constraint test in model 2: {cons} should be satisfied by {should_fail}"
                            break
            else:
                score = max_score
                output = "Model 2 constraints enum rewscols check passed"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that model 2 constraints pass when all different, and fail when not all different.",
        output=output,
        errors=errors
    )

def check_binary_constraint_model_1(stu_model, test_name) -> TestOutput:
    """
    Checks that students followed the handout and actually only have constraints over two variables for model 1.
    """
    max_score = 2
    score = 0
    output = ""
    errors = ""
    
    try:
        board = [[0, '.', 2, '.', 0, '.', 0, '.', 0],
                 [0, '>', 3, '.', 0, '.', 0, '<', 0],
                 [2, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 5]]

        set_timeout(TIMEOUT)
        csp, var_array = stu_model.futoshiki_csp_model_1(board)
        reset_timeout()

        if csp is None:
            score = 0
            errors = "Tried to construct CSP, got nothing"
        else:
            all_cons = csp.get_all_cons()

            score = max_score
            output = "Binary constraint model 1 check passed"
            for con in all_cons:
                all_vars = con.get_scope()
                if len(all_vars) != 2:
                    score = 0
                    errors = f"Model 1 specifies ONLY binary constraints. Found a constraint of length {len(all_vars)}"
                    break
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that students followed the handout and actually only have constraints over two variables for model 1.",
        output=output,
        errors=errors
    )


def test_ord_mrv(stu_propagators, test_name) -> TestOutput:
    """
    Tests the Minimum Remaining Values (MRV) heuristic.
    """
    max_score = 5
    score = 0
    output = ""
    errors = ""
    details = ""
    
    try:
        # Test 1
        a = Variable('A', [1])
        b = Variable('B', [1])
        c = Variable('C', [1])
        d = Variable('D', [1])
        e = Variable('E', [1])
        simple_csp = CSP("Simple", [a, b, c, d, e])
        for i, var in enumerate(simple_csp.variables):
            var.add_domain_values(range(i))
        var = stu_propagators.ord_mrv(simple_csp)
        if var and var.name == simple_csp.variables[0].name:
            details += "Passed 1st Ord MRV Test. "
            score += 1
        else:
            details += "Failed 1st Ord MRV Test. "

        # Test 2
        a = Variable('A', [1, 2, 3, 4, 5])
        b = Variable('B', [1, 2, 3, 4])
        c = Variable('C', [1, 2])
        d = Variable('D', [1, 2, 3])
        e = Variable('E', [1])
        simple_csp = CSP("Simple", [a, b, c, d, e])
        var = stu_propagators.ord_mrv(simple_csp)
        if var and var.name == simple_csp.variables[-1].name:
            details += "Passed 2nd Ord MRV Test. "
            score += 1
        else:
            details += "Failed 2nd Ord MRV Test. "

        # Test 3
        a = Variable('A', [1, 2, 3, 4, 5])
        b = Variable('B', [1])
        c = Variable('C', [1, 2])
        d = Variable('D', [1, 2, 3])
        e = Variable('E', [1, 2, 3, 4])
        simple_csp = CSP("Simple", [a, b, c, d, e])
        var = stu_propagators.ord_mrv(simple_csp)
        if var and var.name == simple_csp.variables[1].name:
            details += "Passed 3rd Ord MRV Test. "
            score += 1
        else:
            details += "Failed 3rd Ord MRV Test. "

        # Test 4
        a = Variable('A', [1, 2, 3, 4, 5])
        b = Variable('B', [1, 2, 3, 4])
        c = Variable('C', [1])
        d = Variable('D', [1, 2, 3])
        e = Variable('E', [1, 2, 3])
        simple_csp = CSP("Simple", [a, b, c, d, e])
        var = stu_propagators.ord_mrv(simple_csp)
        if var and var.name == simple_csp.variables[2].name:
            details += "Passed 4th Ord MRV Test. "
            score += 1
        else:
            details += "Failed 4th Ord MRV Test. "

        # Test 5
        a = Variable('A', [1, 2, 3, 4, 5])
        b = Variable('B', [1, 2, 3, 4])
        c = Variable('C', [1, 2])
        d = Variable('D', [1])
        e = Variable('E', [1, 2])
        simple_csp = CSP("Simple", [a, b, c, d, e])
        var = stu_propagators.ord_mrv(simple_csp)
        if var and var.name == simple_csp.variables[3].name:
            details += "Passed 5th Ord MRV Test. "
            score += 1
        else:
            details += "Failed 5th Ord MRV Test. "

        output = f"MRV tests: {details}"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Tests the Minimum Remaining Values (MRV) heuristic.",
        output=output,
        errors=errors
    )


def check_nary_constraint_model_2(stu_model, test_name) -> TestOutput:
    """
    Checks that model 2 uses n-ary constraints for rows and columns.
    Returns (score, details, max_score).
    """
    max_score = 2
    score = 2
    output = ""
    errors = ""
    
    try:
        board = [[0, '.', 2, '.', 0, '.', 0, '.', 0],
                 [0, '>', 3, '.', 0, '.', 0, '<', 0],
                 [2, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 5]]
        csp, var_array = stu_model.futoshiki_csp_model_2(board)
        if csp is None:
            score = 0
            errors = "Tried to make CSP, got nothing"
        else:
            all_cons = csp.get_all_cons()
            saw_nary = False

            for con in all_cons:
                all_vars = con.get_scope()
                if len(all_vars) == 5:
                    saw_nary = True
                elif len(all_vars) != 2:
                    score = 0
                    errors = f"Model 2 specifies ONLY binary and nary constraints. Found a constraint of length {len(all_vars)}"
                    break

            if saw_nary:
                score = max_score
                output = "Nary constraint model 2 check passed"
            else:
                score = 0
                errors = "Model 2 specifies that nary constraints must be used for the row/col constraints. Only binary constraints were used."
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that model 2 uses n-ary constraints for rows and columns.",
        output=output,
        errors=errors
    )


def check_out_of_domain_tuple(prop, test_name) -> TestOutput:
    """
    Checks that constraints do not contain out-of-domain values.
    """
    max_score = 4
    score = 0
    output = ""
    errors = ""
    
    try:
        board = [[0, '.', 2, '.', 0, '.', 0, '.', 0],
                 [0, '>', 3, '.', 0, '.', 0, '<', 0],
                 [2, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 5]]
        csp, var_array = prop(board)
        if csp is None:
            score = 0
            errors = "Tried to make CSP, got nothing"
        else:
            var_01 = var_array[0][1]
            all_cons = csp.get_cons_with_var(var_01)
            seen_var01 = False

            for con in all_cons:
                curr_scope = con.get_scope()
                if var_01 in curr_scope:
                    seen_var01 = True
                    if not con.has_support(var_01, 2):
                        score = 0
                        errors = f"Failed while testing propagator ({test_name}): a constraint fails on a valid input"
                        break
                    elif con.has_support(var_01, 1) or con.has_support(var_01, 3) or con.has_support(var_01, 4) or con.has_support(var_01, 5):
                        score = 0
                        errors = f"Failed while testing propagator ({test_name}): a constraint contains an out-of-domain value"
                        break

            if seen_var01:
                score = max_score
                output = "Out of domain tuple check passed"
            else:
                score = 0
                errors = f"Failed while testing propagator ({test_name}): found no constraint containing a specific variable"
    except Exception as ex:
        score = 0
        errors = f"Exception encountered: {ex}"

    return TestOutput(
        name=test_name,
        score=score,
        max_score=max_score,
        description="Checks that constraints do not contain out-of-domain values.",
        output=output,
        errors=errors
    )


#######################################
# CUSTOM TESTS
#######################################

def test_fc_pruned_values_returned(stu_propagators, test_name) -> TestOutput:
    """Verify that FC returns the correct pruned (Variable, value) pairs."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(1)
        status, pruned = stu_propagators.prop_FC(csp, newVar=vars_[0])
        if not status:
            errors = "FC returned False (DWO) when it should not have"
        else:
            # FC on 8-queens with Q1=1 should prune exactly: 1 from each Q2-Q8 binary constraint
            # Each binary constraint C(Q1,Qi) has exactly 1 unassigned var after assigning Q1
            # Q2 loses {1,2}, Q3 loses {1,3}, Q4 loses {1,4}, Q5 loses {1,5}, Q6 loses {1,6}, Q7 loses {1,7}, Q8 loses {1,8}
            pruned_set = set(pruned)
            # Verify no duplicates
            if len(pruned_set) != len(pruned):
                errors = "FC returned duplicate pruned pairs"
            elif len(pruned) != 14:
                errors = f"FC pruned {len(pruned)} values, expected 14"
            else:
                score = max_score
                output = "FC pruned values check passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Verify FC returns correct pruned pairs.", output=output, errors=errors)


def test_gac_pruned_values_returned(stu_propagators, test_name) -> TestOutput:
    """Verify GAC returns correct pruned pairs and they can be restored."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(1)
        status, pruned = stu_propagators.prop_GAC(csp, newVar=vars_[0])
        if not status:
            errors = "GAC returned DWO unexpectedly"
        else:
            pruned_set = set(pruned)
            if len(pruned_set) != len(pruned):
                errors = "GAC returned duplicate pruned pairs"
            elif len(pruned) == 0:
                errors = "GAC pruned nothing, expected pruning"
            else:
                # Restore all pruned values
                for var, val in pruned:
                    var.unprune_value(val)
                # After restore, all vars should have full domains again
                all_full = all(v.cur_domain_size() == 8 for v in vars_[1:])
                if all_full:
                    score = max_score
                    output = "GAC pruned values restore check passed"
                else:
                    errors = "After restoring pruned values, domains not fully restored"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Verify GAC pruned pairs can be restored.", output=output, errors=errors)


def test_fc_newvar_none_all_constraints(stu_propagators, test_name) -> TestOutput:
    """When newVar=None, FC should check all constraints with 1 unassigned var."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        # Assign first 3 queens
        vars_[0].assign(1)
        vars_[1].assign(5)
        vars_[2].assign(8)
        # Call FC with newVar=None — should check ALL constraints
        status, pruned = stu_propagators.prop_FC(csp)
        if not status:
            errors = "FC returned DWO with newVar=None"
        else:
            # Verify Q4-Q8 have pruned domains
            for i in range(3, 8):
                if vars_[i].cur_domain_size() == 8:
                    errors = f"Variable {vars_[i]} was not pruned when it should have been"
                    break
            else:
                score = max_score
                output = "FC newVar=None check passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC with newVar=None checks all constraints.", output=output, errors=errors)


def test_gac_iterative_propagation(stu_propagators, test_name) -> TestOutput:
    """GAC should propagate iteratively, pruning more than FC."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        # Tiny adder: X+Y=Z, X>Y. Assign X=3.
        # FC prunes Y to {1,2}, Z unchanged.
        # GAC prunes further: Y={1}, Z={4}.
        dom = (1, 2, 3, 4)
        vars_ = [Variable('X', list(dom)), Variable('Y', list(dom)), Variable('Z', list(dom))]
        c1 = Constraint("X+Y=Z", [vars_[0], vars_[1], vars_[2]])
        sat1 = [t for t in itertools.product(dom, repeat=3) if t[0] + t[1] == t[2]]
        c1.add_satisfying_tuples(sat1)
        c2 = Constraint("X>Y", [vars_[0], vars_[1]])
        sat2 = [t for t in itertools.product(dom, dom) if t[0] > t[1]]
        c2.add_satisfying_tuples(sat2)
        csp = CSP("TinyAdder", vars_)
        csp.add_constraint(c1)
        csp.add_constraint(c2)

        vars_[0].assign(3)
        status_fc, pruned_fc = stu_propagators.prop_FC(csp, newVar=vars_[0])
        fc_domains = [v.cur_domain() for v in vars_]

        # Restore
        for var, val in pruned_fc:
            var.unprune_value(val)

        status_gac, pruned_gac = stu_propagators.prop_GAC(csp, newVar=vars_[0])
        gac_domains = [v.cur_domain() for v in vars_]

        if len(pruned_gac) > len(pruned_fc):
            if gac_domains == [[3], [1], [4]]:
                score = max_score
                output = "GAC propagates more than FC as expected"
            else:
                errors = f"GAC domains incorrect: {gac_domains}"
        else:
            errors = f"GAC should prune more than FC. FC pruned {len(pruned_fc)}, GAC pruned {len(pruned_gac)}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="GAC propagates iteratively, pruning more than FC.", output=output, errors=errors)


def test_futoshiki_2x2_model1(stu_models, test_name) -> TestOutput:
    """Test model 1 on a minimal 2x2 Futoshiki board."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '<', 0],
                 [0, '.', 0]]
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        # Check variable domains
        n = 2
        for i in range(n):
            for j in range(n):
                dom = var_array[i][j].cur_domain()
                if dom != [1, 2]:
                    errors = f"Variable ({i},{j}) has domain {dom}, expected [1,2]"
                    return TestOutput(name=test_name, score=0, max_score=max_score,
                                     description="2x2 model 1 test", output="", errors=errors)
        # Solve it
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_FC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        # Valid: row all-diff, col all-diff, (0,0) < (0,1)
        if sol[0][0] < sol[0][1] and len(set(sol[0])) == 2 and len(set(sol[1])) == 2:
            if sol[0][0] != sol[1][0] and sol[0][1] != sol[1][1]:
                score = max_score
                output = f"2x2 model 1 solved: {sol}"
            else:
                errors = f"Column constraint violated: {sol}"
        else:
            errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="2x2 Futoshiki board with model 1.", output=output, errors=errors)


def test_futoshiki_2x2_model2(stu_models, test_name) -> TestOutput:
    """Test model 2 on a minimal 2x2 Futoshiki board."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '>', 0],
                 [0, '.', 0]]
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC)
        n = 2
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        if sol[0][0] > sol[0][1] and len(set(sol[0])) == 2 and len(set(sol[1])) == 2:
            if sol[0][0] != sol[1][0] and sol[0][1] != sol[1][1]:
                score = max_score
                output = f"2x2 model 2 solved: {sol}"
            else:
                errors = f"Column constraint violated: {sol}"
        else:
            errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="2x2 Futoshiki board with model 2.", output=output, errors=errors)


def test_futoshiki_solve_model1_fc(stu_models, test_name) -> TestOutput:
    """Solve a 4x4 Futoshiki with model 1 + FC and verify solution validity."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        board = [[3, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 1]]
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_FC)
        n = 4
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        # Check all assigned
        for i in range(n):
            for j in range(n):
                if sol[i][j] is None:
                    errors = f"Cell ({i},{j}) not assigned"
                    return TestOutput(name=test_name, score=0, max_score=max_score,
                                     description="Solve 4x4 with model 1 + FC", output="", errors=errors)
        # Check rows all different
        for i in range(n):
            if len(set(sol[i])) != n:
                errors = f"Row {i} not all different: {sol[i]}"
                return TestOutput(name=test_name, score=0, max_score=max_score,
                                 description="Solve 4x4 with model 1 + FC", output="", errors=errors)
        # Check columns all different
        for j in range(n):
            col = [sol[i][j] for i in range(n)]
            if len(set(col)) != n:
                errors = f"Col {j} not all different: {col}"
                return TestOutput(name=test_name, score=0, max_score=max_score,
                                 description="Solve 4x4 with model 1 + FC", output="", errors=errors)
        # Check inequality constraints
        if sol[0][0] != 3:
            errors = f"Pre-filled cell (0,0) should be 3, got {sol[0][0]}"
        elif sol[3][3] != 1:
            errors = f"Pre-filled cell (3,3) should be 1, got {sol[3][3]}"
        elif sol[0][2] >= sol[0][3]:
            errors = f"Inequality (0,2)<(0,3) violated: {sol[0][2]} >= {sol[0][3]}"
        elif sol[2][1] >= sol[2][2]:
            errors = f"Inequality (2,1)<(2,2) violated: {sol[2][1]} >= {sol[2][2]}"
        elif sol[3][1] <= sol[3][2]:
            errors = f"Inequality (3,1)>(3,2) violated: {sol[3][1]} <= {sol[3][2]}"
        else:
            score = max_score
            output = f"4x4 model 1 + FC solved correctly: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 4x4 Futoshiki with model 1 + FC.", output=output, errors=errors)


def test_futoshiki_solve_model2_gac(stu_models, test_name) -> TestOutput:
    """Solve a 4x4 Futoshiki with model 2 + GAC and verify solution validity."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        board = [[3, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 1]]
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC)
        n = 4
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                if sol[i][j] is None:
                    errors = f"Cell ({i},{j}) not assigned"
                    return TestOutput(name=test_name, score=0, max_score=max_score,
                                     description="Solve 4x4 with model 2 + GAC", output="", errors=errors)
        for i in range(n):
            if len(set(sol[i])) != n:
                errors = f"Row {i} not all different: {sol[i]}"
                return TestOutput(name=test_name, score=0, max_score=max_score,
                                 description="Solve 4x4 with model 2 + GAC", output="", errors=errors)
        for j in range(n):
            col = [sol[i][j] for i in range(n)]
            if len(set(col)) != n:
                errors = f"Col {j} not all different: {col}"
                return TestOutput(name=test_name, score=0, max_score=max_score,
                                 description="Solve 4x4 with model 2 + GAC", output="", errors=errors)
        if sol[0][0] != 3:
            errors = f"Pre-filled (0,0) should be 3"
        elif sol[3][3] != 1:
            errors = f"Pre-filled (3,3) should be 1"
        elif sol[0][2] >= sol[0][3]:
            errors = f"Ineq (0,2)<(0,3) violated"
        elif sol[2][1] >= sol[2][2]:
            errors = f"Ineq (2,1)<(2,2) violated"
        elif sol[3][1] <= sol[3][2]:
            errors = f"Ineq (3,1)>(3,2) violated"
        else:
            score = max_score
            output = f"4x4 model 2 + GAC solved correctly: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 4x4 Futoshiki with model 2 + GAC.", output=output, errors=errors)


def test_model1_constraint_count(stu_models, test_name) -> TestOutput:
    """Model 1 should have n*(n-1) + k binary constraints (n*(n-1)/2 row + n*(n-1)/2 col + k ineq)."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0],
                 [0, '.', 0, '.', 0]]
        n = 3
        k = 2  # two inequality constraints
        csp, _ = stu_models.futoshiki_csp_model_1(board)
        expected_neq = 2 * n * (n * (n - 1) // 2)  # rows + cols binary neq = 2 * 3 * 3 = 18
        expected_total = expected_neq + k  # 18 + 2 = 20
        actual = len(csp.get_all_cons())
        if actual == expected_total:
            score = max_score
            output = f"Model 1 has correct constraint count: {actual}"
        else:
            errors = f"Model 1 has {actual} constraints, expected {expected_total}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Verify model 1 constraint count.", output=output, errors=errors)


def test_model2_constraint_count(stu_models, test_name) -> TestOutput:
    """Model 2 should have 2*n + k constraints (n row alldiff + n col alldiff + k ineq)."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0],
                 [0, '.', 0, '.', 0]]
        n = 3
        k = 2
        csp, _ = stu_models.futoshiki_csp_model_2(board)
        expected = 2 * n + k  # 6 + 2 = 8
        actual = len(csp.get_all_cons())
        if actual == expected:
            score = max_score
            output = f"Model 2 has correct constraint count: {actual}"
        else:
            errors = f"Model 2 has {actual} constraints, expected {expected}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Verify model 2 constraint count.", output=output, errors=errors)


def test_mrv_after_pruning(stu_propagators, test_name) -> TestOutput:
    """MRV should pick the variable with fewest values after pruning."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        a = Variable('A', [1, 2, 3, 4, 5])
        b = Variable('B', [1, 2, 3, 4, 5])
        c = Variable('C', [1, 2, 3, 4, 5])
        csp = CSP("PrunedMRV", [a, b, c])
        # Prune values from b so it has smallest domain
        b.prune_value(1)
        b.prune_value(2)
        b.prune_value(3)
        # b has domain {4,5}, a and c have {1,2,3,4,5}
        var = stu_propagators.ord_mrv(csp)
        if var and var.name == 'B':
            # Now prune c further
            c.prune_value(1)
            c.prune_value(2)
            c.prune_value(3)
            c.prune_value(4)
            # c has domain {5}, b has {4,5}, a has {1,2,3,4,5}
            var2 = stu_propagators.ord_mrv(csp)
            if var2 and var2.name == 'C':
                score = max_score
                output = "MRV correctly picks variable with fewest values after pruning"
            else:
                errors = f"MRV picked {var2.name if var2 else None}, expected C"
        else:
            errors = f"MRV picked {var.name if var else None}, expected B"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="MRV with pruned domains.", output=output, errors=errors)


def test_mrv_skips_assigned(stu_propagators, test_name) -> TestOutput:
    """MRV should only consider unassigned variables."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        a = Variable('A', [1])
        b = Variable('B', [1, 2, 3])
        c = Variable('C', [1, 2])
        csp = CSP("AssignedMRV", [a, b, c])
        a.assign(1)  # A is assigned, should be skipped
        var = stu_propagators.ord_mrv(csp)
        if var and var.name == 'C':
            score = max_score
            output = "MRV correctly skips assigned variables"
        else:
            errors = f"MRV picked {var.name if var else None}, expected C"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="MRV skips assigned variables.", output=output, errors=errors)


def test_futoshiki_prefilled_board(stu_models, test_name) -> TestOutput:
    """Test a fully pre-filled board: models should create single-value domains."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        # 2x2 fully filled board
        board = [[1, '.', 2],
                 [2, '.', 1]]
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        expected_doms = [[1], [2], [2], [1]]
        actual_doms = [var_array[i][j].cur_domain() for i in range(2) for j in range(2)]
        if actual_doms == expected_doms:
            score = max_score
            output = "Pre-filled board domains correct"
        else:
            errors = f"Domains: {actual_doms}, expected {expected_doms}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Pre-filled board creates single-value domains.", output=output, errors=errors)


def test_futoshiki_5x5_model1_gac_mrv(stu_models, test_name) -> TestOutput:
    """Solve a 5x5 Futoshiki with model 1 + GAC + MRV."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '.', 0]]
        n = 5
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC, student_propagators.ord_mrv)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        # Validate
        valid = True
        for i in range(n):
            if len(set(sol[i])) != n or any(v is None for v in sol[i]):
                valid = False
                errors = f"Row {i} invalid: {sol[i]}"
                break
        if valid:
            for j in range(n):
                col = [sol[i][j] for i in range(n)]
                if len(set(col)) != n:
                    valid = False
                    errors = f"Col {j} invalid: {col}"
                    break
        if valid:
            if sol[0][2] >= sol[0][3]:
                valid = False
                errors = f"Ineq (0,2)<(0,3) violated"
            elif sol[2][1] <= sol[2][2]:
                valid = False
                errors = f"Ineq (2,1)>(2,2) violated"
        if valid:
            score = max_score
            output = f"5x5 model 1 + GAC + MRV solved correctly"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 5x5 Futoshiki with model 1 + GAC + MRV.", output=output, errors=errors)


def test_futoshiki_5x5_model2_gac_mrv(stu_models, test_name) -> TestOutput:
    """Solve a 5x5 Futoshiki with model 2 + GAC + MRV."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '.', 0]]
        n = 5
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC, student_propagators.ord_mrv)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        valid = True
        for i in range(n):
            if len(set(sol[i])) != n or any(v is None for v in sol[i]):
                valid = False
                errors = f"Row {i} invalid: {sol[i]}"
                break
        if valid:
            for j in range(n):
                col = [sol[i][j] for i in range(n)]
                if len(set(col)) != n:
                    valid = False
                    errors = f"Col {j} invalid: {col}"
                    break
        if valid:
            if sol[0][2] >= sol[0][3]:
                valid = False
                errors = "Ineq (0,2)<(0,3) violated"
            elif sol[2][1] <= sol[2][2]:
                valid = False
                errors = "Ineq (2,1)>(2,2) violated"
        if valid:
            score = max_score
            output = "5x5 model 2 + GAC + MRV solved correctly"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 5x5 Futoshiki with model 2 + GAC + MRV.", output=output, errors=errors)


def test_fc_no_double_prune(stu_propagators, test_name) -> TestOutput:
    """FC should not prune the same value twice from the same variable."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        # Create a CSP where two constraints could both try to prune the same value
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        # Two constraints both saying X != Y
        c1 = Constraint('C1', [x, y])
        c1.add_satisfying_tuples([(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)])
        c2 = Constraint('C2', [x, y])
        c2.add_satisfying_tuples([(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)])
        csp = CSP("DoublePrune", [x, y])
        csp.add_constraint(c1)
        csp.add_constraint(c2)
        x.assign(1)
        status, pruned = stu_propagators.prop_FC(csp, newVar=x)
        # Only value 1 should be pruned from Y, and only once
        pruned_vals = [(v.name, val) for v, val in pruned]
        if pruned_vals.count(('Y', 1)) <= 1 and status:
            if y.cur_domain() == [2, 3]:
                score = max_score
                output = "FC correctly avoids double pruning"
            else:
                errors = f"Y domain is {y.cur_domain()}, expected [2, 3]"
        else:
            errors = f"FC pruned duplicates or returned wrong status. Pruned: {pruned_vals}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC should not prune same value twice.", output=output, errors=errors)


def test_gac_no_newvar_full_propagation(stu_propagators, test_name) -> TestOutput:
    """GAC with newVar=None should enforce arc consistency on all constraints."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        dom = (1, 2, 3, 4)
        x = Variable('X', list(dom))
        y = Variable('Y', list(dom))
        z = Variable('Z', list(dom))
        c1 = Constraint("X+Y=Z", [x, y, z])
        sat1 = [t for t in itertools.product(dom, repeat=3) if t[0] + t[1] == t[2]]
        c1.add_satisfying_tuples(sat1)
        c2 = Constraint("X>Y", [x, y])
        sat2 = [t for t in itertools.product(dom, dom) if t[0] > t[1]]
        c2.add_satisfying_tuples(sat2)
        csp = CSP("TinyAdder2", [x, y, z])
        csp.add_constraint(c1)
        csp.add_constraint(c2)
        # No assignment, GAC from scratch
        status, pruned = stu_propagators.prop_GAC(csp)
        # X > Y, X+Y = Z constraints should prune some values
        # X can't be 1 (need X > Y), Y can't be 4 (need X > Y and X<=4)
        # Z can't be 1 or 2 (min X+Y = 2+1 = 3)
        x_dom = x.cur_domain()
        y_dom = y.cur_domain()
        z_dom = z.cur_domain()
        if 1 not in x_dom and 4 not in y_dom and 1 not in z_dom and 2 not in z_dom:
            score = max_score
            output = f"GAC newVar=None propagation correct. X={x_dom}, Y={y_dom}, Z={z_dom}"
        else:
            errors = f"GAC newVar=None insufficient pruning. X={x_dom}, Y={y_dom}, Z={z_dom}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="GAC with newVar=None enforces full arc consistency.", output=output, errors=errors)


#######################################
# ADDITIONAL COMPREHENSIVE TESTS
#######################################

def test_bt_basic(stu_propagators, test_name) -> TestOutput:
    """Test prop_BT: no pruning occurs, only checks fully-assigned constraints."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(1)
        status, pruned = stu_propagators.prop_BT(csp, newVar=vars_[0])
        if not status:
            errors = "BT returned False when only one queen assigned (should be True)"
        elif len(pruned) != 0:
            errors = f"BT should never prune, but returned {len(pruned)} pruned values"
        else:
            score = max_score
            output = "BT basic test passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="prop_BT should not prune and returns True with partial assignment.",
                      output=output, errors=errors)


def test_bt_conflict(stu_propagators, test_name) -> TestOutput:
    """Test prop_BT detects conflict when all constraints of newVar are fully assigned."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        x = Variable('X', [1, 2])
        y = Variable('Y', [1, 2])
        c = Constraint('X!=Y', [x, y])
        c.add_satisfying_tuples([(1, 2), (2, 1)])
        csp = CSP("BT_Conflict", [x, y])
        csp.add_constraint(c)
        x.assign(1)
        y.assign(1)  # conflict: X=1, Y=1 violates X!=Y
        status, pruned = stu_propagators.prop_BT(csp, newVar=y)
        if status:
            errors = "BT should return False when constraint is violated"
        elif len(pruned) != 0:
            errors = "BT should return empty pruned list"
        else:
            score = max_score
            output = "BT conflict detection passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="prop_BT detects fully assigned constraint violation.",
                      output=output, errors=errors)


def test_bt_no_newvar(stu_propagators, test_name) -> TestOutput:
    """Test prop_BT with newVar=None returns (True, [])."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(4)
        status, pruned = stu_propagators.prop_BT(csp)
        if not status:
            errors = "BT with no newVar should return True"
        elif len(pruned) != 0:
            errors = "BT with no newVar should return empty pruned list"
        else:
            score = max_score
            output = "BT no newVar test passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="prop_BT with no newVar does nothing.",
                      output=output, errors=errors)


def test_fc_no_constraints(stu_propagators, test_name) -> TestOutput:
    """FC on a CSP with no constraints should prune nothing."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        csp = CSP("NoConstraints", [x, y])
        x.assign(1)
        status, pruned = stu_propagators.prop_FC(csp, newVar=x)
        if not status:
            errors = "FC returned DWO on CSP with no constraints"
        elif len(pruned) != 0:
            errors = f"FC pruned {len(pruned)} values on CSP with no constraints"
        else:
            score = max_score
            output = "FC no constraints test passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC on CSP with no constraints.",
                      output=output, errors=errors)


def test_gac_no_constraints(stu_propagators, test_name) -> TestOutput:
    """GAC on a CSP with no constraints should prune nothing."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        csp = CSP("NoConstraints", [x, y])
        status, pruned = stu_propagators.prop_GAC(csp)
        if not status:
            errors = "GAC returned DWO on CSP with no constraints"
        elif len(pruned) != 0:
            errors = f"GAC pruned {len(pruned)} values on CSP with no constraints"
        else:
            score = max_score
            output = "GAC no constraints test passed"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="GAC on CSP with no constraints.",
                      output=output, errors=errors)


def test_fc_bt_search_4_queens(stu_propagators, test_name) -> TestOutput:
    """Solve 4-queens with BT + FC and verify a valid solution."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(4)
        solver = BacktrackingSearch(csp)
        set_timeout(TIMEOUT)
        solver.search(stu_propagators.prop_FC)
        reset_timeout()
        vars_ = csp.get_all_vars()
        vals = [v.get_assigned_value() for v in vars_]
        if None in vals:
            errors = "4-queens with FC has unassigned variables"
        elif len(set(vals)) != 4:
            errors = f"4-queens solution has duplicates: {vals}"
        else:
            # Verify no queens attack each other
            valid = True
            for i in range(4):
                for j in range(i+1, 4):
                    if vals[i] == vals[j] or abs(vals[i]-vals[j]) == abs(i-j):
                        valid = False
                        errors = f"Queens {i} and {j} attack each other: {vals}"
                        break
                if not valid:
                    break
            if valid:
                score = max_score
                output = f"4-queens solved: {vals}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 4-queens with FC.",
                      output=output, errors=errors)


def test_gac_bt_search_8_queens(stu_propagators, test_name) -> TestOutput:
    """Solve 8-queens with BT + GAC and verify a valid solution."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        solver = BacktrackingSearch(csp)
        set_timeout(TIMEOUT)
        solver.search(stu_propagators.prop_GAC)
        reset_timeout()
        vars_ = csp.get_all_vars()
        vals = [v.get_assigned_value() for v in vars_]
        if None in vals:
            errors = "8-queens with GAC has unassigned variables"
        elif len(set(vals)) != 8:
            errors = f"8-queens solution has duplicates: {vals}"
        else:
            valid = True
            for i in range(8):
                for j in range(i+1, 8):
                    if vals[i] == vals[j] or abs(vals[i]-vals[j]) == abs(i-j):
                        valid = False
                        errors = f"Queens {i} and {j} attack each other: {vals}"
                        break
                if not valid:
                    break
            if valid:
                score = max_score
                output = f"8-queens solved with GAC"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 8-queens with GAC.",
                      output=output, errors=errors)


def test_gac_bt_search_8_queens_mrv(stu_propagators, test_name) -> TestOutput:
    """Solve 8-queens with BT + GAC + MRV and verify solution."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        solver = BacktrackingSearch(csp)
        set_timeout(TIMEOUT)
        solver.search(stu_propagators.prop_GAC, stu_propagators.ord_mrv)
        reset_timeout()
        vars_ = csp.get_all_vars()
        vals = [v.get_assigned_value() for v in vars_]
        if None in vals:
            errors = "8-queens unsolved"
        else:
            valid = True
            for i in range(8):
                for j in range(i+1, 8):
                    if vals[i] == vals[j] or abs(vals[i]-vals[j]) == abs(i-j):
                        valid = False
                        errors = f"Attack: Q{i}={vals[i]}, Q{j}={vals[j]}"
                        break
                if not valid:
                    break
            if valid:
                score = max_score
                output = "8-queens solved with GAC+MRV"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Solve 8-queens with GAC+MRV.",
                      output=output, errors=errors)


def test_fc_exact_domains_after_two_assigns(stu_propagators, test_name) -> TestOutput:
    """After assigning Q1=1 and Q2=5 in 8-queens, check exact FC domain results."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        csp = n_queens(8)
        vars_ = csp.get_all_vars()
        vars_[0].assign(1)
        stu_propagators.prop_FC(csp, newVar=vars_[0])
        vars_[1].assign(5)
        stu_propagators.prop_FC(csp, newVar=vars_[1])
        # After Q1=1: Q2 loses {1,2}; Q3 loses {1,3}; ... Q8 loses {1,8}
        # After Q2=5: Q3 additionally loses {5,4(diag)=4,6(diag)=6}; etc.
        # Q3: started [2,4,5,6,7,8], lost {5,4,6} => [2,7,8]
        expected_q3 = [2, 7, 8]
        q3_dom = vars_[2].cur_domain()
        if q3_dom == expected_q3:
            score = max_score
            output = "FC exact domains after two assigns correct"
        else:
            errors = f"Q3 domain is {q3_dom}, expected {expected_q3}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC exact domains after sequential assignments.",
                      output=output, errors=errors)


def test_fc_dwo_returns_pruned(stu_propagators, test_name) -> TestOutput:
    """When FC detects DWO, it should still return the pruned values so far."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        # Create a CSP where assigning x=1 causes y's domain to be wiped out
        x = Variable('X', [1, 2])
        y = Variable('Y', [1])  # Only has value 1
        c = Constraint('X!=Y', [x, y])
        c.add_satisfying_tuples([(1, 2), (2, 1)])  # y=1 only works with x=2
        csp = CSP("DWO_Pruned", [x, y])
        csp.add_constraint(c)
        x.assign(1)
        status, pruned = stu_propagators.prop_FC(csp, newVar=x)
        if status:
            errors = "FC should return DWO (False) when Y's domain is wiped out"
        elif len(pruned) == 0:
            errors = "FC should return the pruned values even when DWO occurs"
        else:
            # Check (y, 1) is in pruned
            pruned_pairs = [(v.name, val) for v, val in pruned]
            if ('Y', 1) in pruned_pairs:
                score = max_score
                output = "FC correctly returns pruned values on DWO"
            else:
                errors = f"Expected (Y,1) in pruned, got {pruned_pairs}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC returns pruned values even on DWO.",
                      output=output, errors=errors)


def test_gac_dwo_returns_pruned(stu_propagators, test_name) -> TestOutput:
    """When GAC detects DWO, it should still return the pruned values so far."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        x = Variable('X', [1, 2])
        y = Variable('Y', [1])
        c = Constraint('X!=Y', [x, y])
        c.add_satisfying_tuples([(1, 2), (2, 1)])
        csp = CSP("GAC_DWO_Pruned", [x, y])
        csp.add_constraint(c)
        x.assign(1)
        status, pruned = stu_propagators.prop_GAC(csp, newVar=x)
        if status:
            errors = "GAC should return DWO (False)"
        elif len(pruned) == 0:
            errors = "GAC should return pruned values on DWO"
        else:
            pruned_pairs = [(v.name, val) for v, val in pruned]
            if ('Y', 1) in pruned_pairs:
                score = max_score
                output = "GAC correctly returns pruned values on DWO"
            else:
                errors = f"Expected (Y,1) in pruned, got {pruned_pairs}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="GAC returns pruned values even on DWO.",
                      output=output, errors=errors)


def test_fc_only_checks_unary_constraints(stu_propagators, test_name) -> TestOutput:
    """FC should only check constraints that have exactly 1 unassigned variable."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        # Three variables, one ternary constraint: X+Y < Z
        dom = (1, 2, 3, 4, 5)
        x = Variable('X', list(dom))
        y = Variable('Y', list(dom))
        z = Variable('Z', list(dom))
        c1 = Constraint("X+Y<Z", [x, y, z])
        sat = [t for t in itertools.product(dom, repeat=3) if t[0] + t[1] < t[2]]
        c1.add_satisfying_tuples(sat)
        csp = CSP("Ternary", [x, y, z])
        csp.add_constraint(c1)
        # Assign only X — constraint has 2 unassigned vars, FC should NOT check it
        x.assign(1)
        status, pruned = stu_propagators.prop_FC(csp, newVar=x)
        if not status:
            errors = "FC returned DWO when constraint has 2 unassigned vars"
        elif len(pruned) != 0:
            errors = f"FC should not prune when constraint has 2 unassigned vars, pruned {len(pruned)}"
        else:
            # Now assign Y too — constraint has 1 unassigned var, FC should check it
            y.assign(2)
            status2, pruned2 = stu_propagators.prop_FC(csp, newVar=y)
            # X=1, Y=2, Z must satisfy 1+2 < Z => Z > 3 => Z in {4,5}
            z_dom = z.cur_domain()
            if z_dom == [4, 5]:
                score = max_score
                output = "FC correctly only checks constraints with 1 unassigned var"
            else:
                errors = f"Z domain should be [4,5], got {z_dom}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC only checks constraints with exactly 1 unassigned variable.",
                      output=output, errors=errors)


def test_gac_chain_propagation(stu_propagators, test_name) -> TestOutput:
    """GAC should propagate through a chain of constraints: X<Y, Y<Z, Z<W."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        dom = [1, 2, 3, 4, 5]
        x = Variable('X', list(dom))
        y = Variable('Y', list(dom))
        z = Variable('Z', list(dom))
        w = Variable('W', list(dom))
        
        c1 = Constraint("X<Y", [x, y])
        c1.add_satisfying_tuples([t for t in itertools.product(dom, dom) if t[0] < t[1]])
        c2 = Constraint("Y<Z", [y, z])
        c2.add_satisfying_tuples([t for t in itertools.product(dom, dom) if t[0] < t[1]])
        c3 = Constraint("Z<W", [z, w])
        c3.add_satisfying_tuples([t for t in itertools.product(dom, dom) if t[0] < t[1]])
        
        csp = CSP("Chain", [x, y, z, w])
        csp.add_constraint(c1)
        csp.add_constraint(c2)
        csp.add_constraint(c3)
        
        # GAC from scratch should figure out:
        # X can't be 4 or 5 (need X<Y<Z<W, max chain length from X is 4 values)
        # W can't be 1 or 2 (need X<Y<Z<W, min W is 4)
        status, pruned = stu_propagators.prop_GAC(csp)
        x_dom = x.cur_domain()
        w_dom = w.cur_domain()
        
        if not status:
            errors = "GAC returned DWO on solvable chain CSP"
        elif 4 in x_dom or 5 in x_dom:
            errors = f"X should not have 4 or 5, got {x_dom}"
        elif 1 in w_dom or 2 in w_dom:
            errors = f"W should not have 1 or 2, got {w_dom}"
        else:
            score = max_score
            output = f"GAC chain propagation correct: X={x_dom}, W={w_dom}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="GAC propagates through chain of constraints.",
                      output=output, errors=errors)


def test_model1_no_inequalities(stu_models, test_name) -> TestOutput:
    """Model 1 on a board with no inequality constraints."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0]]
        n = 3
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        # Should have n*(n-1) binary not-equal constraints for rows + columns = 2*3*3 = 18
        expected = 2 * n * (n * (n - 1) // 2)  # 18
        actual = len(csp.get_all_cons())
        if actual != expected:
            errors = f"Expected {expected} constraints, got {actual}"
        else:
            # All constraints should be binary
            all_binary = all(len(c.get_scope()) == 2 for c in csp.get_all_cons())
            if not all_binary:
                errors = "Not all constraints are binary in model 1"
            else:
                # Solve it
                solver = BacktrackingSearch(csp)
                solver.search(student_propagators.prop_FC)
                sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
                valid = all(len(set(sol[i])) == n for i in range(n))
                valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
                if valid:
                    score = max_score
                    output = f"Model 1 no inequalities solved: {sol}"
                else:
                    errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 1 with no inequality constraints.",
                      output=output, errors=errors)


def test_model2_no_inequalities(stu_models, test_name) -> TestOutput:
    """Model 2 on a board with no inequality constraints."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0]]
        n = 3
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        expected = 2 * n  # 6 (3 row + 3 col all-diff)
        actual = len(csp.get_all_cons())
        if actual != expected:
            errors = f"Expected {expected} constraints, got {actual}"
        else:
            solver = BacktrackingSearch(csp)
            solver.search(student_propagators.prop_GAC)
            sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
            valid = all(len(set(sol[i])) == n for i in range(n))
            valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
            if valid:
                score = max_score
                output = f"Model 2 no inequalities solved: {sol}"
            else:
                errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 2 with no inequality constraints.",
                      output=output, errors=errors)


def test_model1_3x3_with_prefilled(stu_models, test_name) -> TestOutput:
    """Model 1 on a 3x3 board with some pre-filled cells and inequalities."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[1, '<', 0, '.', 0],
                 [0, '.', 0, '.', 0],
                 [0, '.', 0, '>', 0]]
        n = 3
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_FC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        # Check pre-filled
        if sol[0][0] != 1:
            errors = f"Pre-filled (0,0) should be 1, got {sol[0][0]}"
        # Check inequalities
        elif sol[0][0] >= sol[0][1]:
            errors = f"Ineq (0,0)<(0,1) violated: {sol[0][0]} >= {sol[0][1]}"
        elif sol[2][1] <= sol[2][2]:
            errors = f"Ineq (2,1)>(2,2) violated: {sol[2][1]} <= {sol[2][2]}"
        else:
            # Check all-different rows/cols
            valid = all(len(set(sol[i])) == n for i in range(n))
            valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
            if valid:
                score = max_score
                output = f"3x3 model 1 solved: {sol}"
            else:
                errors = f"All-different violated: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="3x3 model 1 with pre-filled cells and inequalities.",
                      output=output, errors=errors)


def test_model2_3x3_with_prefilled(stu_models, test_name) -> TestOutput:
    """Model 2 on a 3x3 board with pre-filled cells and inequalities."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[1, '<', 0, '.', 0],
                 [0, '.', 0, '.', 0],
                 [0, '.', 0, '>', 0]]
        n = 3
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        if sol[0][0] != 1:
            errors = f"Pre-filled (0,0) should be 1"
        elif sol[0][0] >= sol[0][1]:
            errors = f"Ineq (0,0)<(0,1) violated"
        elif sol[2][1] <= sol[2][2]:
            errors = f"Ineq (2,1)>(2,2) violated"
        else:
            valid = all(len(set(sol[i])) == n for i in range(n))
            valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
            if valid:
                score = max_score
                output = f"3x3 model 2 solved: {sol}"
            else:
                errors = f"All-different violated: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="3x3 model 2 with pre-filled cells and inequalities.",
                      output=output, errors=errors)


def test_model1_1x1(stu_models, test_name) -> TestOutput:
    """Model 1 on a trivial 1x1 board."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0]]
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        # 1x1 board: only one variable with domain [1]
        dom = var_array[0][0].cur_domain()
        if dom != [1]:
            errors = f"1x1 domain should be [1], got {dom}"
        else:
            solver = BacktrackingSearch(csp)
            solver.search(student_propagators.prop_BT)
            val = var_array[0][0].get_assigned_value()
            if val == 1:
                score = max_score
                output = "1x1 model 1 passed"
            else:
                errors = f"1x1 should assign 1, got {val}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="1x1 board with model 1.",
                      output=output, errors=errors)


def test_model2_1x1(stu_models, test_name) -> TestOutput:
    """Model 2 on a trivial 1x1 board."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0]]
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        dom = var_array[0][0].cur_domain()
        if dom != [1]:
            errors = f"1x1 domain should be [1], got {dom}"
        else:
            solver = BacktrackingSearch(csp)
            solver.search(student_propagators.prop_BT)
            val = var_array[0][0].get_assigned_value()
            if val == 1:
                score = max_score
                output = "1x1 model 2 passed"
            else:
                errors = f"1x1 should assign 1, got {val}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="1x1 board with model 2.",
                      output=output, errors=errors)


def test_model1_variable_count(stu_models, test_name) -> TestOutput:
    """Model 1 should create exactly n*n variables."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0]]
        n = 4
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        all_vars = csp.get_all_vars()
        if len(all_vars) != n * n:
            errors = f"Expected {n*n} variables, got {len(all_vars)}"
        elif len(var_array) != n:
            errors = f"Expected {n} rows in var_array, got {len(var_array)}"
        elif any(len(row) != n for row in var_array):
            errors = f"Expected {n} cols per row in var_array"
        else:
            score = max_score
            output = f"Model 1 has correct {n*n} variables"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 1 creates correct number of variables.",
                      output=output, errors=errors)


def test_model2_variable_count(stu_models, test_name) -> TestOutput:
    """Model 2 should create exactly n*n variables."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0]]
        n = 4
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        all_vars = csp.get_all_vars()
        if len(all_vars) != n * n:
            errors = f"Expected {n*n} variables, got {len(all_vars)}"
        elif len(var_array) != n:
            errors = f"Expected {n} rows in var_array, got {len(var_array)}"
        else:
            score = max_score
            output = f"Model 2 has correct {n*n} variables"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 2 creates correct number of variables.",
                      output=output, errors=errors)


def test_model1_solve_with_gac(stu_models, test_name) -> TestOutput:
    """Model 1 should also work with GAC propagator."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[3, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 1]]
        n = 4
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                if sol[i][j] is None:
                    errors = f"Cell ({i},{j}) not assigned"
                    return TestOutput(name=test_name, score=0, max_score=max_score,
                                     description="Model 1 + GAC", output="", errors=errors)
        valid = all(len(set(sol[i])) == n for i in range(n))
        valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
        valid = valid and sol[0][0] == 3 and sol[3][3] == 1
        valid = valid and sol[0][2] < sol[0][3] and sol[2][1] < sol[2][2] and sol[3][1] > sol[3][2]
        if valid:
            score = max_score
            output = f"4x4 model 1 + GAC solved: {sol}"
        else:
            errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 1 solved with GAC propagator.",
                      output=output, errors=errors)


def test_model2_solve_with_fc(stu_models, test_name) -> TestOutput:
    """Model 2 should also work with FC propagator."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[3, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0],
                 [0, '.', 0, '>', 0, '.', 1]]
        n = 4
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_FC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(n):
                if sol[i][j] is None:
                    errors = f"Cell ({i},{j}) not assigned"
                    return TestOutput(name=test_name, score=0, max_score=max_score,
                                     description="Model 2 + FC", output="", errors=errors)
        valid = all(len(set(sol[i])) == n for i in range(n))
        valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
        valid = valid and sol[0][0] == 3 and sol[3][3] == 1
        valid = valid and sol[0][2] < sol[0][3] and sol[2][1] < sol[2][2] and sol[3][1] > sol[3][2]
        if valid:
            score = max_score
            output = f"4x4 model 2 + FC solved: {sol}"
        else:
            errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 2 solved with FC propagator.",
                      output=output, errors=errors)


def test_check_out_of_domain_model1(stu_models, test_name) -> TestOutput:
    """Model 1 constraints should only have tuples with in-domain values."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 2, '.', 0, '.', 0, '.', 0],
                 [0, '>', 3, '.', 0, '.', 0, '<', 0],
                 [2, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 5]]
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        var_01 = var_array[0][1]  # domain is [2] (pre-filled)
        all_cons = csp.get_cons_with_var(var_01)
        seen = False
        for con in all_cons:
            if var_01 in con.get_scope():
                seen = True
                if not con.has_support(var_01, 2):
                    errors = f"Constraint {con} should support var_01=2"
                    break
                # Check that out-of-domain values are not supported
                for bad_val in [1, 3, 4, 5]:
                    if con.has_support(var_01, bad_val):
                        errors = f"Constraint {con} should NOT support var_01={bad_val}"
                        break
                if errors:
                    break
        if not errors:
            if seen:
                score = max_score
                output = "Model 1 out-of-domain check passed"
            else:
                errors = "No constraints found for var_01"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 1 constraints have no out-of-domain tuples.",
                      output=output, errors=errors)


def test_check_out_of_domain_model2(stu_models, test_name) -> TestOutput:
    """Model 2 constraints should only have tuples with in-domain values."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '.', 2, '.', 0, '.', 0, '.', 0],
                 [0, '>', 3, '.', 0, '.', 0, '<', 0],
                 [2, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '.', 0, '.', 0, '<', 0, '.', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 5]]
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        var_01 = var_array[0][1]
        all_cons = csp.get_cons_with_var(var_01)
        seen = False
        for con in all_cons:
            if var_01 in con.get_scope():
                seen = True
                if not con.has_support(var_01, 2):
                    errors = f"Constraint {con} should support var_01=2"
                    break
                for bad_val in [1, 3, 4, 5]:
                    if con.has_support(var_01, bad_val):
                        errors = f"Constraint {con} should NOT support var_01={bad_val}"
                        break
                if errors:
                    break
        if not errors:
            if seen:
                score = max_score
                output = "Model 2 out-of-domain check passed"
            else:
                errors = "No constraints found for var_01"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 2 constraints have no out-of-domain tuples.",
                      output=output, errors=errors)


def test_mrv_single_unassigned(stu_propagators, test_name) -> TestOutput:
    """MRV with only one unassigned variable should return it."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        a = Variable('A', [1, 2, 3])
        b = Variable('B', [1, 2, 3])
        c = Variable('C', [1, 2, 3])
        csp = CSP("SingleUnassigned", [a, b, c])
        a.assign(1)
        b.assign(2)
        var = stu_propagators.ord_mrv(csp)
        if var and var.name == 'C':
            score = max_score
            output = "MRV single unassigned passed"
        else:
            errors = f"MRV returned {var.name if var else None}, expected C"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="MRV with single unassigned variable.",
                      output=output, errors=errors)


def test_mrv_uses_cur_domain(stu_propagators, test_name) -> TestOutput:
    """MRV should use cur_domain_size (pruned), not domain_size (permanent)."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        # A has 5 values permanently, but prune 4 => cur_domain_size = 1
        # B has 2 values permanently => cur_domain_size = 2
        a = Variable('A', [1, 2, 3, 4, 5])
        b = Variable('B', [1, 2])
        csp = CSP("CurDomain", [a, b])
        a.prune_value(2)
        a.prune_value(3)
        a.prune_value(4)
        a.prune_value(5)
        # A cur_domain = [1], B cur_domain = [1,2]
        var = stu_propagators.ord_mrv(csp)
        if var and var.name == 'A':
            score = max_score
            output = "MRV uses cur_domain_size correctly"
        else:
            errors = f"MRV picked {var.name if var else None}, expected A (cur_domain_size=1)"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="MRV uses current domain size, not permanent domain size.",
                      output=output, errors=errors)


def test_fc_gac_agree_on_simple(stu_propagators, test_name) -> TestOutput:
    """On the simple 8-queens with Q1=1, FC and GAC should agree on domains."""
    max_score = 1
    score = 0
    output = ""
    errors = ""
    try:
        # FC version
        csp_fc = n_queens(8)
        vars_fc = csp_fc.get_all_vars()
        vars_fc[0].assign(1)
        stu_propagators.prop_FC(csp_fc, newVar=vars_fc[0])
        fc_domains = [v.cur_domain() for v in vars_fc]
        
        # GAC version
        csp_gac = n_queens(8)
        vars_gac = csp_gac.get_all_vars()
        vars_gac[0].assign(1)
        stu_propagators.prop_GAC(csp_gac, newVar=vars_gac[0])
        gac_domains = [v.cur_domain() for v in vars_gac]
        
        # After just 1 assignment on binary constraints, FC = GAC
        if fc_domains == gac_domains:
            score = max_score
            output = "FC and GAC agree after single assignment on binary constraints"
        else:
            errors = "FC and GAC domains differ when they should match"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC and GAC agree on binary constraints with single assignment.",
                      output=output, errors=errors)


def test_model1_5x5_many_inequalities(stu_models, test_name) -> TestOutput:
    """Model 1 on a 5x5 board with many inequality constraints."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '<', 0, '<', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '>', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0, '>', 0]]
        n = 5
        k = 7  # seven inequality constraints
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        expected_neq = 2 * n * (n * (n - 1) // 2)  # 2*5*10 = 100
        expected_total = expected_neq + k  # 107
        actual = len(csp.get_all_cons())
        if actual != expected_total:
            errors = f"Expected {expected_total} constraints, got {actual}"
        else:
            # Verify all binary
            all_binary = all(len(c.get_scope()) == 2 for c in csp.get_all_cons())
            if not all_binary:
                errors = "Model 1 should have only binary constraints"
            else:
                # Solve and verify
                solver = BacktrackingSearch(csp)
                solver.search(student_propagators.prop_GAC, student_propagators.ord_mrv)
                sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
                valid = all(len(set(sol[i])) == n and all(v is not None for v in sol[i]) for i in range(n))
                valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
                # Check inequalities
                valid = valid and sol[0][0] < sol[0][1] < sol[0][2]
                valid = valid and sol[1][2] > sol[1][3]
                valid = valid and sol[2][3] < sol[2][4]
                valid = valid and sol[3][0] > sol[3][1]
                valid = valid and sol[4][1] < sol[4][2] and sol[4][3] > sol[4][4]
                if valid:
                    score = max_score
                    output = f"5x5 model 1 many inequalities solved"
                else:
                    errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 1 on 5x5 board with many inequalities.",
                      output=output, errors=errors)


def test_model2_5x5_many_inequalities(stu_models, test_name) -> TestOutput:
    """Model 2 on a 5x5 board with many inequality constraints."""
    max_score = 3
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '<', 0, '<', 0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0, '>', 0, '.', 0],
                 [0, '.', 0, '.', 0, '.', 0, '<', 0],
                 [0, '>', 0, '.', 0, '.', 0, '.', 0],
                 [0, '.', 0, '<', 0, '.', 0, '>', 0]]
        n = 5
        k = 7
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        expected = 2 * n + k  # 10 + 7 = 17
        actual = len(csp.get_all_cons())
        if actual != expected:
            errors = f"Expected {expected} constraints, got {actual}"
        else:
            solver = BacktrackingSearch(csp)
            solver.search(student_propagators.prop_GAC, student_propagators.ord_mrv)
            sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
            valid = all(len(set(sol[i])) == n and all(v is not None for v in sol[i]) for i in range(n))
            valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
            valid = valid and sol[0][0] < sol[0][1] < sol[0][2]
            valid = valid and sol[1][2] > sol[1][3]
            valid = valid and sol[2][3] < sol[2][4]
            valid = valid and sol[3][0] > sol[3][1]
            valid = valid and sol[4][1] < sol[4][2] and sol[4][3] > sol[4][4]
            if valid:
                score = max_score
                output = f"5x5 model 2 many inequalities solved"
            else:
                errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 2 on 5x5 board with many inequalities.",
                      output=output, errors=errors)


def test_fc_respects_already_pruned(stu_propagators, test_name) -> TestOutput:
    """FC should not prune a value that has already been pruned."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        c = Constraint('X!=Y', [x, y])
        c.add_satisfying_tuples([(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)])
        csp = CSP("AlreadyPruned", [x, y])
        csp.add_constraint(c)
        # Pre-prune y=1
        y.prune_value(1)
        x.assign(1)
        status, pruned = stu_propagators.prop_FC(csp, newVar=x)
        # FC should NOT try to prune y=1 again (it's already pruned)
        pruned_pairs = [(v.name, val) for v, val in pruned]
        if ('Y', 1) in pruned_pairs:
            errors = "FC pruned (Y,1) which was already pruned"
        elif not status:
            errors = "FC returned DWO unexpectedly"
        elif y.cur_domain() != [2, 3]:
            errors = f"Y domain should be [2,3], got {y.cur_domain()}"
        else:
            score = max_score
            output = "FC respects already-pruned values"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="FC should not re-prune already pruned values.",
                      output=output, errors=errors)


def test_gac_respects_already_pruned(stu_propagators, test_name) -> TestOutput:
    """GAC should not prune a value that has already been pruned."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        x = Variable('X', [1, 2, 3])
        y = Variable('Y', [1, 2, 3])
        c = Constraint('X!=Y', [x, y])
        c.add_satisfying_tuples([(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)])
        csp = CSP("AlreadyPruned", [x, y])
        csp.add_constraint(c)
        y.prune_value(1)
        x.assign(1)
        status, pruned = stu_propagators.prop_GAC(csp, newVar=x)
        pruned_pairs = [(v.name, val) for v, val in pruned]
        if ('Y', 1) in pruned_pairs:
            errors = "GAC pruned (Y,1) which was already pruned"
        elif not status:
            errors = "GAC returned DWO unexpectedly"
        elif y.cur_domain() != [2, 3]:
            errors = f"Y domain should be [2,3], got {y.cur_domain()}"
        else:
            score = max_score
            output = "GAC respects already-pruned values"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="GAC should not re-prune already pruned values.",
                      output=output, errors=errors)


def test_model1_ineq_both_directions(stu_models, test_name) -> TestOutput:
    """Test that both < and > inequality constraints work in model 1."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        # Board with both < and > in same row
        board = [[0, '<', 0, '>', 0],
                 [0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0]]
        n = 3
        csp, var_array = stu_models.futoshiki_csp_model_1(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        valid = all(len(set(sol[i])) == n for i in range(n))
        valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
        valid = valid and sol[0][0] < sol[0][1] and sol[0][1] > sol[0][2]
        if valid:
            score = max_score
            output = f"Both directions solved: {sol[0]}"
        else:
            errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 1 with both < and > in same row.",
                      output=output, errors=errors)


def test_model2_ineq_both_directions(stu_models, test_name) -> TestOutput:
    """Test that both < and > inequality constraints work in model 2."""
    max_score = 2
    score = 0
    output = ""
    errors = ""
    try:
        board = [[0, '<', 0, '>', 0],
                 [0, '.', 0, '.', 0],
                 [0, '.', 0, '.', 0]]
        n = 3
        csp, var_array = stu_models.futoshiki_csp_model_2(board)
        solver = BacktrackingSearch(csp)
        solver.search(student_propagators.prop_GAC)
        sol = [[var_array[i][j].get_assigned_value() for j in range(n)] for i in range(n)]
        valid = all(len(set(sol[i])) == n for i in range(n))
        valid = valid and all(len(set(sol[i][j] for i in range(n))) == n for j in range(n))
        valid = valid and sol[0][0] < sol[0][1] and sol[0][1] > sol[0][2]
        if valid:
            score = max_score
            output = f"Both directions solved: {sol[0]}"
        else:
            errors = f"Invalid solution: {sol}"
    except Exception as ex:
        errors = f"Exception: {ex}"
    return TestOutput(name=test_name, score=score, max_score=max_score,
                      description="Model 2 with both < and > in same row.",
                      output=output, errors=errors)


# List of tests - updated to work with TestOutput format
futoshiki_tests = [
    (test_simple_fc, student_propagators, "test_simple_fc", "FC"),
    (three_queen_fc, student_propagators, "three_queen_fc", "FC"),
    (test_prop_1, student_propagators.prop_FC, "test_prop_1_FC", "FC"),
    (test_prop_2, student_propagators.prop_FC, "test_prop_2_FC", "FC"),
    (test_prop_3, student_propagators.prop_FC, "test_prop_3_FC", "FC"),
    (test_tiny_adder_fc, student_propagators, "test_tiny_adder_fc", "FC"),
    (test_no_pruning_fc, student_propagators, "test_no_pruning_fc", "FC"),
    (test_no_pruning2_fc, student_propagators, "test_no_pruning2_fc", "FC"),
    (test_dwo_fc, student_propagators, "test_dwo_fc", "FC"),

    (test_simple_gac, student_propagators, "test_simple_gac", "GAC"),
    (three_queen_gac, student_propagators, "three_queen_gac", "GAC"),
    (test_prop_1, student_propagators.prop_GAC, "test_prop_1_GAC", "GAC"),
    (test_prop_2, student_propagators.prop_GAC, "test_prop_2_GAC", "GAC"),
    (test_prop_3, student_propagators.prop_GAC, "test_prop_3_GAC", "GAC"),
    (test_tiny_adder_gac, student_propagators, "test_tiny_adder_gac", "GAC"),
    (test_no_pruning_gac, student_propagators, "test_no_pruning_gac", "GAC"),
    (test_dwo_gac, student_propagators, "test_dwo_gac", "GAC"),

    (test_futoshiki_model_1, student_models, "test_futoshiki_model_1", "Model 1"),
    (check_model_1_constraints_enum_rewscols, student_models, "check_model_1_constraints_enum_rewscols", "Model 1"),
    (check_binary_constraint_model_1, student_models, "check_binary_constraint_model_1", "Model 1"),

    (test_futoshiki_model_2, student_models, "test_futoshiki_model_2", "Model 2"),
    (check_model_2_constraints_enum_rewscols, student_models, "check_model_2_constraints_enum_rewscols", "Model 2"),
    (check_nary_constraint_model_2, student_models, "check_nary_constraint_model_2", "Model 2"),

    (test_ord_mrv, student_propagators, "test_ord_mrv", "Ord"),

    # Custom tests
    (test_fc_pruned_values_returned, student_propagators, "test_fc_pruned_values_returned", "FC"),
    (test_gac_pruned_values_returned, student_propagators, "test_gac_pruned_values_returned", "GAC"),
    (test_fc_newvar_none_all_constraints, student_propagators, "test_fc_newvar_none_all_constraints", "FC"),
    (test_gac_iterative_propagation, student_propagators, "test_gac_iterative_propagation", "GAC"),
    (test_futoshiki_2x2_model1, student_models, "test_futoshiki_2x2_model1", "Model 1"),
    (test_futoshiki_2x2_model2, student_models, "test_futoshiki_2x2_model2", "Model 2"),
    (test_futoshiki_solve_model1_fc, student_models, "test_futoshiki_solve_model1_fc", "Model 1"),
    (test_futoshiki_solve_model2_gac, student_models, "test_futoshiki_solve_model2_gac", "Model 2"),
    (test_model1_constraint_count, student_models, "test_model1_constraint_count", "Model 1"),
    (test_model2_constraint_count, student_models, "test_model2_constraint_count", "Model 2"),
    (test_mrv_after_pruning, student_propagators, "test_mrv_after_pruning", "Ord"),
    (test_mrv_skips_assigned, student_propagators, "test_mrv_skips_assigned", "Ord"),
    (test_futoshiki_prefilled_board, student_models, "test_futoshiki_prefilled_board", "Model 1"),
    (test_futoshiki_5x5_model1_gac_mrv, student_models, "test_futoshiki_5x5_model1_gac_mrv", "Model 1"),
    (test_futoshiki_5x5_model2_gac_mrv, student_models, "test_futoshiki_5x5_model2_gac_mrv", "Model 2"),
    (test_fc_no_double_prune, student_propagators, "test_fc_no_double_prune", "FC"),
    (test_gac_no_newvar_full_propagation, student_propagators, "test_gac_no_newvar_full_propagation", "GAC"),

    # Additional comprehensive tests
    (test_bt_basic, student_propagators, "test_bt_basic", "FC"),
    (test_bt_conflict, student_propagators, "test_bt_conflict", "FC"),
    (test_bt_no_newvar, student_propagators, "test_bt_no_newvar", "FC"),
    (test_fc_no_constraints, student_propagators, "test_fc_no_constraints", "FC"),
    (test_gac_no_constraints, student_propagators, "test_gac_no_constraints", "GAC"),
    (test_fc_bt_search_4_queens, student_propagators, "test_fc_bt_search_4_queens", "FC"),
    (test_gac_bt_search_8_queens, student_propagators, "test_gac_bt_search_8_queens", "GAC"),
    (test_gac_bt_search_8_queens_mrv, student_propagators, "test_gac_bt_search_8_queens_mrv", "GAC"),
    (test_fc_exact_domains_after_two_assigns, student_propagators, "test_fc_exact_domains_after_two_assigns", "FC"),
    (test_fc_dwo_returns_pruned, student_propagators, "test_fc_dwo_returns_pruned", "FC"),
    (test_gac_dwo_returns_pruned, student_propagators, "test_gac_dwo_returns_pruned", "GAC"),
    (test_fc_only_checks_unary_constraints, student_propagators, "test_fc_only_checks_unary_constraints", "FC"),
    (test_gac_chain_propagation, student_propagators, "test_gac_chain_propagation", "GAC"),
    (test_model1_no_inequalities, student_models, "test_model1_no_inequalities", "Model 1"),
    (test_model2_no_inequalities, student_models, "test_model2_no_inequalities", "Model 2"),
    (test_model1_3x3_with_prefilled, student_models, "test_model1_3x3_with_prefilled", "Model 1"),
    (test_model2_3x3_with_prefilled, student_models, "test_model2_3x3_with_prefilled", "Model 2"),
    (test_model1_1x1, student_models, "test_model1_1x1", "Model 1"),
    (test_model2_1x1, student_models, "test_model2_1x1", "Model 2"),
    (test_model1_variable_count, student_models, "test_model1_variable_count", "Model 1"),
    (test_model2_variable_count, student_models, "test_model2_variable_count", "Model 2"),
    (test_model1_solve_with_gac, student_models, "test_model1_solve_with_gac", "Model 1"),
    (test_model2_solve_with_fc, student_models, "test_model2_solve_with_fc", "Model 2"),
    (test_check_out_of_domain_model1, student_models, "test_check_out_of_domain_model1", "Model 1"),
    (test_check_out_of_domain_model2, student_models, "test_check_out_of_domain_model2", "Model 2"),
    (test_mrv_single_unassigned, student_propagators, "test_mrv_single_unassigned", "Ord"),
    (test_mrv_uses_cur_domain, student_propagators, "test_mrv_uses_cur_domain", "Ord"),
    (test_fc_gac_agree_on_simple, student_propagators, "test_fc_gac_agree_on_simple", "FC"),
    (test_model1_5x5_many_inequalities, student_models, "test_model1_5x5_many_inequalities", "Model 1"),
    (test_model2_5x5_many_inequalities, student_models, "test_model2_5x5_many_inequalities", "Model 2"),
    (test_fc_respects_already_pruned, student_propagators, "test_fc_respects_already_pruned", "FC"),
    (test_gac_respects_already_pruned, student_propagators, "test_gac_respects_already_pruned", "GAC"),
    (test_model1_ineq_both_directions, student_models, "test_model1_ineq_both_directions", "Model 1"),
    (test_model2_ineq_both_directions, student_models, "test_model2_ineq_both_directions", "Model 2"),
]
