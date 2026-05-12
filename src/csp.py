from __future__ import annotations
class CSP:
    def __init__(self,name,variables):
        self.name=name; self._variables=list(variables); self._constraints=[]; self._var_to_constraints={v:[] for v in self._variables}
    def add_constraint(self,constraint):
        self._constraints.append(constraint)
        for v in constraint.get_scope():
            if v not in self._var_to_constraints:
                self._var_to_constraints[v]=[]; self._variables.append(v)
            self._var_to_constraints[v].append(constraint)
    def get_all_vars(self): return list(self._variables)
    def get_all_cons(self): return list(self._constraints)
    def get_cons_with_var(self,variable): return list(self._var_to_constraints.get(variable,[]))
    def get_all_unasgn_vars(self): return [v for v in self._variables if not v.is_assigned()]
    def restore_all_variable_domains(self):
        for v in self._variables: v.restore_curdom()
    def unassign_all_vars(self):
        for v in self._variables: v.unassign()
    def __repr__(self): return f"CSP({self.name}, vars={len(self._variables)}, cons={len(self._constraints)})"
