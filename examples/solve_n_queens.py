import itertools
from src import CSP,Variable,Constraint,BacktrackingSearch
from propagators import prop_GAC,ord_mrv
def n_queens(n):
    dom=list(range(1,n+1)); vars=[Variable(f'Q{i}',dom) for i in dom]; csp=CSP(f'{n}-Queens',vars)
    for qi in range(n):
        for qj in range(qi+1,n):
            c=Constraint(f'C(Q{qi+1},Q{qj+1})',[vars[qi],vars[qj]])
            c.add_satisfying_tuples([t for t in itertools.product(dom,dom) if t[0]!=t[1] and abs(t[0]-t[1])!=abs(qi-qj)])
            csp.add_constraint(c)
    return csp
csp=n_queens(8); solver=BacktrackingSearch(csp); solver.search(prop_GAC,ord_mrv); print([v.get_assigned_value() for v in csp.get_all_vars()])
