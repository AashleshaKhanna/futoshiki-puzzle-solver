from __future__ import annotations
class BacktrackingSearch:
    def __init__(self,csp):
        self.csp=csp; self.trace=False; self.n_decisions=0; self.n_prunings=0; self.solution_count=0
    def enable_trace(self): self.trace=True
    def disable_trace(self): self.trace=False
    def search(self,propagator,var_ord=None):
        self.n_decisions=0; self.n_prunings=0; self.solution_count=0
        self.csp.unassign_all_vars(); self.csp.restore_all_variable_domains()
        status,pruned=propagator(self.csp); self.n_prunings+=len(pruned)
        if not status:
            self._restore(pruned); return False
        solved=self._backtrack(propagator,var_ord)
        if solved: self.solution_count+=1
        print(f"CSP {self.csp.name}: solved={solved}, decisions={self.n_decisions}, prunings={self.n_prunings}")
        return solved
    def _backtrack(self,propagator,var_ord):
        unassigned=self.csp.get_all_unasgn_vars()
        if not unassigned: return True
        var=var_ord(self.csp) if var_ord else unassigned[0]
        for value in list(var.cur_domain()):
            var.assign(value); self.n_decisions+=1
            status,pruned=propagator(self.csp,var); self.n_prunings+=len(pruned)
            if status and self._backtrack(propagator,var_ord): return True
            self._restore(pruned); var.unassign()
        return False
    @staticmethod
    def _restore(pruned):
        for variable,value in pruned: variable.unprune_value(value)
BT=BacktrackingSearch
