import itertools
from src import CSP, Variable, Constraint, BacktrackingSearch
from propagators import prop_FC, prop_GAC, ord_mrv
def test_tiny_adder_gac():
    dom=[1,2,3,4]; x=Variable('X',dom); y=Variable('Y',dom); z=Variable('Z',dom)
    c1=Constraint('X+Y=Z',[x,y,z]); c1.add_satisfying_tuples([t for t in itertools.product(dom, repeat=3) if t[0]+t[1]==t[2]])
    c2=Constraint('X>Y',[x,y]); c2.add_satisfying_tuples([t for t in itertools.product(dom, dom) if t[0]>t[1]])
    csp=CSP('TinyAdder',[x,y,z]); csp.add_constraint(c1); csp.add_constraint(c2)
    x.assign(3); status,_=prop_GAC(csp,x)
    assert status and y.cur_domain()==[1] and z.cur_domain()==[4]
def test_backtracking_solve_simple():
    x=Variable('X',[1,2,3]); y=Variable('Y',[1,2,3]); c=Constraint('X<Y',[x,y])
    c.add_satisfying_tuples([(a,b) for a in x.domain() for b in y.domain() if a<b])
    csp=CSP('Simple',[x,y]); csp.add_constraint(c)
    assert BacktrackingSearch(csp).search(prop_FC, ord_mrv)
    assert x.get_assigned_value()<y.get_assigned_value()
