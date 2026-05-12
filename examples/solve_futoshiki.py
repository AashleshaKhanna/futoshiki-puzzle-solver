from futoshiki_csp import futoshiki_csp_model_2
from propagators import prop_GAC, ord_mrv
from src import BacktrackingSearch
board=[[3,'.',0,'.',0,'<',0],[0,'.',0,'.',0,'.',0],[0,'.',0,'<',0,'.',0],[0,'.',0,'>',0,'.',1]]
csp,variables=futoshiki_csp_model_2(board)
solver=BacktrackingSearch(csp)
print('Solved:', solver.search(prop_GAC, ord_mrv))
for row in variables: print([v.get_assigned_value() for v in row])
