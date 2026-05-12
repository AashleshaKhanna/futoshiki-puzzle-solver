"""Quick runner for custom tests, bypassing SIGALRM issues on Windows."""
import itertools
from src import CSP, Variable, Constraint, BacktrackingSearch
import propagators as sp
import futoshiki_csp as fm

def n_queens(n):
    dom = list(range(1, n + 1))
    vars_ = [Variable(f'Q{i}', dom) for i in dom]
    cons = []
    for qi in range(n):
        for qj in range(qi + 1, n):
            c = Constraint(f'C(Q{qi+1},Q{qj+1})', [vars_[qi], vars_[qj]])
            sat = [t for t in itertools.product(dom, repeat=2) if t[0]!=t[1] and abs(t[0]-t[1])!=abs(qi-qj)]
            c.add_satisfying_tuples(sat)
            cons.append(c)
    csp = CSP(f'{n}-Queens', vars_)
    for c_ in cons:
        csp.add_constraint(c_)
    return csp

passed = 0
failed = 0

def check(name, ok):
    global passed, failed
    status = "PASS" if ok else "FAIL"
    print(f"  {status}: {name}")
    if ok:
        passed += 1
    else:
        failed += 1

# === FC Tests ===
print("--- FC Tests ---")

csp = n_queens(8); v = csp.get_all_vars(); v[0].assign(1)
s, pruned = sp.prop_FC(csp, newVar=v[0])
check("fc_pruned_values_returned", s and len(set(pruned)) == len(pruned) == 14)

csp = n_queens(8); v = csp.get_all_vars()
v[0].assign(1); v[1].assign(5); v[2].assign(8)
s, _ = sp.prop_FC(csp)
check("fc_newvar_none_all_constraints", s and all(v[i].cur_domain_size() < 8 for i in range(3,8)))

x = Variable('X',[1,2,3]); y = Variable('Y',[1,2,3])
c1 = Constraint('C1',[x,y]); c1.add_satisfying_tuples([(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)])
c2 = Constraint('C2',[x,y]); c2.add_satisfying_tuples([(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)])
csp = CSP('DP',[x,y]); csp.add_constraint(c1); csp.add_constraint(c2)
x.assign(1)
s, pruned = sp.prop_FC(csp, newVar=x)
pv = [(v.name,val) for v,val in pruned]
check("fc_no_double_prune", s and pv.count(('Y',1)) <= 1 and y.cur_domain() == [2,3])

# === GAC Tests ===
print("--- GAC Tests ---")

csp = n_queens(8); v = csp.get_all_vars(); v[0].assign(1)
s, pruned = sp.prop_GAC(csp, newVar=v[0])
for var, val in pruned: var.unprune_value(val)
check("gac_pruned_values_returned", s and all(x.cur_domain_size() == 8 for x in v[1:]))

dom = (1,2,3,4)
vs = [Variable('X', list(dom)), Variable('Y', list(dom)), Variable('Z', list(dom))]
c1 = Constraint('X+Y=Z', [vs[0],vs[1],vs[2]])
c1.add_satisfying_tuples([t for t in itertools.product(dom,repeat=3) if t[0]+t[1]==t[2]])
c2 = Constraint('X>Y', [vs[0],vs[1]])
c2.add_satisfying_tuples([t for t in itertools.product(dom,dom) if t[0]>t[1]])
csp = CSP('TA', vs); csp.add_constraint(c1); csp.add_constraint(c2)
vs[0].assign(3)
_, pfc = sp.prop_FC(csp, newVar=vs[0])
for var,val in pfc: var.unprune_value(val)
_, pgac = sp.prop_GAC(csp, newVar=vs[0])
check("gac_iterative_propagation", len(pgac) > len(pfc) and [v.cur_domain() for v in vs] == [[3],[1],[4]])

dom = (1,2,3,4)
x = Variable('X',list(dom)); y = Variable('Y',list(dom)); z = Variable('Z',list(dom))
c1 = Constraint('X+Y=Z',[x,y,z])
c1.add_satisfying_tuples([t for t in itertools.product(dom,repeat=3) if t[0]+t[1]==t[2]])
c2 = Constraint('X>Y',[x,y])
c2.add_satisfying_tuples([t for t in itertools.product(dom,dom) if t[0]>t[1]])
csp = CSP('TA2',[x,y,z]); csp.add_constraint(c1); csp.add_constraint(c2)
s, _ = sp.prop_GAC(csp)
check("gac_no_newvar_full_propagation",
      1 not in x.cur_domain() and 4 not in y.cur_domain() and 1 not in z.cur_domain() and 2 not in z.cur_domain())

# === MRV Tests ===
print("--- MRV Tests ---")

a = Variable('A',[1,2,3,4,5]); b = Variable('B',[1,2,3,4,5]); c = Variable('C',[1,2,3,4,5])
csp = CSP('P',[a,b,c]); b.prune_value(1); b.prune_value(2); b.prune_value(3)
ok1 = sp.ord_mrv(csp).name == 'B'
c.prune_value(1); c.prune_value(2); c.prune_value(3); c.prune_value(4)
ok2 = sp.ord_mrv(csp).name == 'C'
check("mrv_after_pruning", ok1 and ok2)

a = Variable('A',[1]); b = Variable('B',[1,2,3]); c = Variable('C',[1,2])
csp = CSP('M',[a,b,c]); a.assign(1)
check("mrv_skips_assigned", sp.ord_mrv(csp).name == 'C')

# === Futoshiki Model Tests ===
print("--- Futoshiki Model Tests ---")

board = [[0,'<',0],[0,'.',0]]
csp, va = fm.futoshiki_csp_model_1(board)
bt = BacktrackingSearch(csp); bt.search(sp.prop_FC)
sol = [[va[i][j].get_assigned_value() for j in range(2)] for i in range(2)]
check("2x2_model1", sol[0][0]<sol[0][1] and len(set(sol[0]))==2 and len(set(sol[1]))==2 and sol[0][0]!=sol[1][0])

board = [[0,'>',0],[0,'.',0]]
csp, va = fm.futoshiki_csp_model_2(board)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
sol = [[va[i][j].get_assigned_value() for j in range(2)] for i in range(2)]
check("2x2_model2", sol[0][0]>sol[0][1] and len(set(sol[0]))==2 and len(set(sol[1]))==2 and sol[0][0]!=sol[1][0])

board = [[0,'<',0,'.',0],[0,'.',0,'>',0],[0,'.',0,'.',0]]
csp, _ = fm.futoshiki_csp_model_1(board)
check("model1_constraint_count", len(csp.get_all_cons()) == 20)

csp, _ = fm.futoshiki_csp_model_2(board)
check("model2_constraint_count", len(csp.get_all_cons()) == 8)

board = [[1,'.',2],[2,'.',1]]
csp, va = fm.futoshiki_csp_model_1(board)
doms = [va[i][j].cur_domain() for i in range(2) for j in range(2)]
check("prefilled_board", doms == [[1],[2],[2],[1]])

# Solve 4x4 model1+FC
board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]]
csp, va = fm.futoshiki_csp_model_1(board)
bt = BacktrackingSearch(csp); bt.search(sp.prop_FC)
sol = [[va[i][j].get_assigned_value() for j in range(4)] for i in range(4)]
valid = all(len(set(sol[i]))==4 for i in range(4)) and all(len(set(sol[i][j] for i in range(4)))==4 for j in range(4))
valid = valid and sol[0][0]==3 and sol[3][3]==1 and sol[0][2]<sol[0][3] and sol[2][1]<sol[2][2] and sol[3][1]>sol[3][2]
check("solve_4x4_model1_fc", valid)

# Solve 4x4 model2+GAC
csp, va = fm.futoshiki_csp_model_2(board)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
sol = [[va[i][j].get_assigned_value() for j in range(4)] for i in range(4)]
valid = all(len(set(sol[i]))==4 for i in range(4)) and all(len(set(sol[i][j] for i in range(4)))==4 for j in range(4))
valid = valid and sol[0][0]==3 and sol[3][3]==1 and sol[0][2]<sol[0][3] and sol[2][1]<sol[2][2] and sol[3][1]>sol[3][2]
check("solve_4x4_model2_gac", valid)

# Solve 5x5 model1+GAC+MRV
board = [[0,'.',0,'.',0,'<',0,'.',0],[0,'.',0,'.',0,'.',0,'.',0],[0,'.',0,'>',0,'.',0,'.',0],[0,'.',0,'.',0,'.',0,'.',0],[0,'.',0,'.',0,'.',0,'.',0]]
csp, va = fm.futoshiki_csp_model_1(board)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC, sp.ord_mrv)
sol = [[va[i][j].get_assigned_value() for j in range(5)] for i in range(5)]
valid = all(len(set(sol[i]))==5 for i in range(5)) and all(len(set(sol[i][j] for i in range(5)))==5 for j in range(5))
valid = valid and sol[0][2]<sol[0][3] and sol[2][1]>sol[2][2]
check("solve_5x5_model1_gac_mrv", valid)

# Solve 5x5 model2+GAC+MRV
csp, va = fm.futoshiki_csp_model_2(board)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC, sp.ord_mrv)
sol = [[va[i][j].get_assigned_value() for j in range(5)] for i in range(5)]
valid = all(len(set(sol[i]))==5 for i in range(5)) and all(len(set(sol[i][j] for i in range(5)))==5 for j in range(5))
valid = valid and sol[0][2]<sol[0][3] and sol[2][1]>sol[2][2]
check("solve_5x5_model2_gac_mrv", valid)

# === BT Tests ===
print("--- BT Tests ---")

csp = n_queens(8); v = csp.get_all_vars(); v[0].assign(1)
s, pruned = sp.prop_BT(csp, newVar=v[0])
check("bt_basic_no_prune", s and len(pruned) == 0)

x = Variable('X',[1,2]); y = Variable('Y',[1,2])
c = Constraint('X!=Y',[x,y]); c.add_satisfying_tuples([(1,2),(2,1)])
csp = CSP('BTC',[x,y]); csp.add_constraint(c)
x.assign(1); y.assign(1)
s, pruned = sp.prop_BT(csp, newVar=y)
check("bt_conflict_detection", not s and len(pruned) == 0)

csp = n_queens(4)
s, pruned = sp.prop_BT(csp)
check("bt_no_newvar", s and len(pruned) == 0)

# === Additional FC Tests ===
print("--- Additional FC Tests ---")

x = Variable('X',[1,2,3]); y = Variable('Y',[1,2,3])
csp = CSP('NC',[x,y]); x.assign(1)
s, pruned = sp.prop_FC(csp, newVar=x)
check("fc_no_constraints", s and len(pruned) == 0)

csp = n_queens(4)
bt = BacktrackingSearch(csp); bt.search(sp.prop_FC)
vals = [v.get_assigned_value() for v in csp.get_all_vars()]
valid4 = len(set(vals)) == 4 and all(abs(vals[i]-vals[j]) != abs(i-j) for i in range(4) for j in range(i+1,4))
check("fc_solve_4_queens", valid4)

csp = n_queens(8); v = csp.get_all_vars()
v[0].assign(1); sp.prop_FC(csp, newVar=v[0])
v[1].assign(5); sp.prop_FC(csp, newVar=v[1])
check("fc_exact_domains_two_assigns", v[2].cur_domain() == [2, 7, 8])

x = Variable('X',[1,2]); y = Variable('Y',[1])
c = Constraint('X!=Y',[x,y]); c.add_satisfying_tuples([(1,2),(2,1)])
csp = CSP('DWO',[x,y]); csp.add_constraint(c); x.assign(1)
s, pruned = sp.prop_FC(csp, newVar=x)
check("fc_dwo_returns_pruned", not s and len(pruned) > 0 and ('Y',1) in [(v.name,val) for v,val in pruned])

dom = (1,2,3,4,5)
x = Variable('X',list(dom)); y = Variable('Y',list(dom)); z = Variable('Z',list(dom))
c = Constraint('X+Y<Z',[x,y,z])
c.add_satisfying_tuples([t for t in itertools.product(dom,repeat=3) if t[0]+t[1]<t[2]])
csp = CSP('T',[x,y,z]); csp.add_constraint(c)
x.assign(1); s1, p1 = sp.prop_FC(csp, newVar=x)
check("fc_only_unary", s1 and len(p1) == 0)
y.assign(2); s2, p2 = sp.prop_FC(csp, newVar=y)
check("fc_checks_after_two_assigns", z.cur_domain() == [4, 5])

x = Variable('X',[1,2,3]); y = Variable('Y',[1,2,3])
c = Constraint('X!=Y',[x,y]); c.add_satisfying_tuples([(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)])
csp = CSP('AP',[x,y]); csp.add_constraint(c)
y.prune_value(1); x.assign(1)
s, pruned = sp.prop_FC(csp, newVar=x)
check("fc_respects_already_pruned", s and ('Y',1) not in [(v.name,val) for v,val in pruned] and y.cur_domain()==[2,3])

# FC and GAC agree on binary 8-queens single assignment
csp1 = n_queens(8); v1 = csp1.get_all_vars(); v1[0].assign(1)
sp.prop_FC(csp1, newVar=v1[0])
fc_doms = [v.cur_domain() for v in v1]
csp2 = n_queens(8); v2 = csp2.get_all_vars(); v2[0].assign(1)
sp.prop_GAC(csp2, newVar=v2[0])
gac_doms = [v.cur_domain() for v in v2]
check("fc_gac_agree_binary", fc_doms == gac_doms)

# === Additional GAC Tests ===
print("--- Additional GAC Tests ---")

x = Variable('X',[1,2,3]); y = Variable('Y',[1,2,3])
csp = CSP('NC',[x,y])
s, pruned = sp.prop_GAC(csp)
check("gac_no_constraints", s and len(pruned) == 0)

csp = n_queens(8)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
vals = [v.get_assigned_value() for v in csp.get_all_vars()]
valid8 = len(set(vals)) == 8 and all(abs(vals[i]-vals[j]) != abs(i-j) for i in range(8) for j in range(i+1,8))
check("gac_solve_8_queens", valid8)

csp = n_queens(8)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC, sp.ord_mrv)
vals = [v.get_assigned_value() for v in csp.get_all_vars()]
valid8m = len(set(vals)) == 8 and all(abs(vals[i]-vals[j]) != abs(i-j) for i in range(8) for j in range(i+1,8))
check("gac_solve_8_queens_mrv", valid8m)

x = Variable('X',[1,2]); y = Variable('Y',[1])
c = Constraint('X!=Y',[x,y]); c.add_satisfying_tuples([(1,2),(2,1)])
csp = CSP('DWO',[x,y]); csp.add_constraint(c); x.assign(1)
s, pruned = sp.prop_GAC(csp, newVar=x)
check("gac_dwo_returns_pruned", not s and len(pruned) > 0)

dom = [1,2,3,4,5]
x = Variable('X',list(dom)); y = Variable('Y',list(dom))
z = Variable('Z',list(dom)); w = Variable('W',list(dom))
c1 = Constraint('X<Y',[x,y]); c1.add_satisfying_tuples([t for t in itertools.product(dom,dom) if t[0]<t[1]])
c2 = Constraint('Y<Z',[y,z]); c2.add_satisfying_tuples([t for t in itertools.product(dom,dom) if t[0]<t[1]])
c3 = Constraint('Z<W',[z,w]); c3.add_satisfying_tuples([t for t in itertools.product(dom,dom) if t[0]<t[1]])
csp = CSP('Chain',[x,y,z,w]); csp.add_constraint(c1); csp.add_constraint(c2); csp.add_constraint(c3)
s, pruned = sp.prop_GAC(csp)
check("gac_chain_propagation", s and 4 not in x.cur_domain() and 5 not in x.cur_domain() and 1 not in w.cur_domain() and 2 not in w.cur_domain())

x = Variable('X',[1,2,3]); y = Variable('Y',[1,2,3])
c = Constraint('X!=Y',[x,y]); c.add_satisfying_tuples([(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)])
csp = CSP('AP',[x,y]); csp.add_constraint(c)
y.prune_value(1); x.assign(1)
s, pruned = sp.prop_GAC(csp, newVar=x)
check("gac_respects_already_pruned", s and ('Y',1) not in [(v.name,val) for v,val in pruned] and y.cur_domain()==[2,3])

# === Additional MRV Tests ===
print("--- Additional MRV Tests ---")

a = Variable('A',[1,2,3]); b = Variable('B',[1,2,3]); c = Variable('C',[1,2,3])
csp = CSP('SingleU',[a,b,c]); a.assign(1); b.assign(2)
check("mrv_single_unassigned", sp.ord_mrv(csp).name == 'C')

a = Variable('A',[1,2,3,4,5]); b = Variable('B',[1,2])
csp = CSP('CD',[a,b])
a.prune_value(2); a.prune_value(3); a.prune_value(4); a.prune_value(5)
check("mrv_uses_cur_domain", sp.ord_mrv(csp).name == 'A')

# === Additional Model Tests ===
print("--- Additional Model Tests ---")

# No inequalities
board = [[0,'.',0,'.',0],[0,'.',0,'.',0],[0,'.',0,'.',0]]
csp, _ = fm.futoshiki_csp_model_1(board)
check("model1_no_ineq_count", len(csp.get_all_cons()) == 18)
csp, _ = fm.futoshiki_csp_model_2(board)
check("model2_no_ineq_count", len(csp.get_all_cons()) == 6)

# 3x3 with prefilled and inequalities
board = [[1,'<',0,'.',0],[0,'.',0,'.',0],[0,'.',0,'>',0]]
csp, va = fm.futoshiki_csp_model_1(board); bt = BacktrackingSearch(csp); bt.search(sp.prop_FC)
sol = [[va[i][j].get_assigned_value() for j in range(3)] for i in range(3)]
valid = sol[0][0]==1 and sol[0][0]<sol[0][1] and sol[2][1]>sol[2][2]
valid = valid and all(len(set(sol[i]))==3 for i in range(3))
check("model1_3x3_prefilled", valid)

csp, va = fm.futoshiki_csp_model_2(board); bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
sol = [[va[i][j].get_assigned_value() for j in range(3)] for i in range(3)]
valid = sol[0][0]==1 and sol[0][0]<sol[0][1] and sol[2][1]>sol[2][2]
valid = valid and all(len(set(sol[i]))==3 for i in range(3))
check("model2_3x3_prefilled", valid)

# 1x1 board
board = [[0]]
csp, va = fm.futoshiki_csp_model_1(board)
check("model1_1x1_domain", va[0][0].cur_domain() == [1])
csp, va = fm.futoshiki_csp_model_2(board)
check("model2_1x1_domain", va[0][0].cur_domain() == [1])

# Variable counts
board = [[0,'.',0,'.',0,'.',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'.',0,'.',0]]
csp, _ = fm.futoshiki_csp_model_1(board)
check("model1_var_count_4x4", len(csp.get_all_vars()) == 16)
csp, _ = fm.futoshiki_csp_model_2(board)
check("model2_var_count_4x4", len(csp.get_all_vars()) == 16)

# Model 1 with GAC, Model 2 with FC
board = [[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]]
csp, va = fm.futoshiki_csp_model_1(board); bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
sol = [[va[i][j].get_assigned_value() for j in range(4)] for i in range(4)]
valid = all(len(set(sol[i]))==4 for i in range(4)) and sol[0][0]==3 and sol[3][3]==1
check("model1_solve_with_gac", valid)

csp, va = fm.futoshiki_csp_model_2(board); bt = BacktrackingSearch(csp); bt.search(sp.prop_FC)
sol = [[va[i][j].get_assigned_value() for j in range(4)] for i in range(4)]
valid = all(len(set(sol[i]))==4 for i in range(4)) and sol[0][0]==3 and sol[3][3]==1
check("model2_solve_with_fc", valid)

# Out-of-domain tuples
board = [[0,'.',2,'.',0,'.',0,'.',0],[0,'>',3,'.',0,'.',0,'<',0],[2,'.',0,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'<',0,'.',0],[0,'>',0,'.',0,'.',0,'.',5]]
csp, va = fm.futoshiki_csp_model_1(board)
var01 = va[0][1]
ok_ood = all(not c.has_support(var01, bv) for c in csp.get_cons_with_var(var01) if var01 in c.get_scope() for bv in [1,3,4,5])
check("model1_no_out_of_domain", ok_ood)

csp, va = fm.futoshiki_csp_model_2(board)
var01 = va[0][1]
ok_ood2 = all(not c.has_support(var01, bv) for c in csp.get_cons_with_var(var01) if var01 in c.get_scope() for bv in [1,3,4,5])
check("model2_no_out_of_domain", ok_ood2)

# Both < and > in same row
board = [[0,'<',0,'>',0],[0,'.',0,'.',0],[0,'.',0,'.',0]]
csp, va = fm.futoshiki_csp_model_1(board); bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
sol = [[va[i][j].get_assigned_value() for j in range(3)] for i in range(3)]
check("model1_both_ineq_dirs", sol[0][0]<sol[0][1] and sol[0][1]>sol[0][2])

csp, va = fm.futoshiki_csp_model_2(board); bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC)
sol = [[va[i][j].get_assigned_value() for j in range(3)] for i in range(3)]
check("model2_both_ineq_dirs", sol[0][0]<sol[0][1] and sol[0][1]>sol[0][2])

# 5x5 with many inequalities
board = [[0,'<',0,'<',0,'.',0,'.',0],[0,'.',0,'.',0,'>',0,'.',0],[0,'.',0,'.',0,'.',0,'<',0],[0,'>',0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0,'>',0]]
csp, va = fm.futoshiki_csp_model_1(board)
check("model1_5x5_many_ineq_count", len(csp.get_all_cons()) == 107)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC, sp.ord_mrv)
sol = [[va[i][j].get_assigned_value() for j in range(5)] for i in range(5)]
valid = all(len(set(sol[i]))==5 for i in range(5)) and sol[0][0]<sol[0][1]<sol[0][2] and sol[1][2]>sol[1][3]
check("model1_5x5_many_ineq_solve", valid)

csp, va = fm.futoshiki_csp_model_2(board)
check("model2_5x5_many_ineq_count", len(csp.get_all_cons()) == 17)
bt = BacktrackingSearch(csp); bt.search(sp.prop_GAC, sp.ord_mrv)
sol = [[va[i][j].get_assigned_value() for j in range(5)] for i in range(5)]
valid = all(len(set(sol[i]))==5 for i in range(5)) and sol[0][0]<sol[0][1]<sol[0][2] and sol[1][2]>sol[1][3]
check("model2_5x5_many_ineq_solve", valid)

print(f"\n{'='*40}")
print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
