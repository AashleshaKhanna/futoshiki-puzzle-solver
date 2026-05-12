from __future__ import annotations
class Constraint:
    def __init__(self,name,scope): self.name=name; self._scope=list(scope); self._sat_tuples=set()
    def add_satisfying_tuples(self,tuples):
        for t in tuples:
            if len(t)!=len(self._scope): raise ValueError("Tuple length does not match constraint scope")
            self._sat_tuples.add(tuple(t))
    def get_scope(self): return list(self._scope)
    def get_n_unassigned_vars(self): return len(self.get_unassigned_vars())
    def get_unassigned_vars(self): return [v for v in self._scope if not v.is_assigned()]
    def check(self,values): return tuple(values) in self._sat_tuples
    def has_support(self,variable,value):
        if variable not in self._scope: raise ValueError("Variable not in constraint scope")
        idx=self._scope.index(variable)
        for tup in self._sat_tuples:
            if tup[idx]!=value: continue
            ok=True
            for i,v in enumerate(self._scope):
                if v.is_assigned():
                    if v.get_assigned_value()!=tup[i]: ok=False; break
                elif tup[i] not in v.cur_domain(): ok=False; break
            if ok: return True
        return False
    def __repr__(self): return f"Constraint({self.name})"
