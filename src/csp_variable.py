from __future__ import annotations
from typing import Any
class Variable:
    def __init__(self,name:str,domain:list[Any]):
        self.name=name; self._domain=list(domain); self._cur_domain=list(domain); self._assigned_value=None
    def domain(self): return list(self._domain)
    def cur_domain(self): return [self._assigned_value] if self.is_assigned() else list(self._cur_domain)
    def cur_domain_size(self): return len(self.cur_domain())
    def prune_value(self,value):
        if value in self._cur_domain: self._cur_domain.remove(value)
    def unprune_value(self,value):
        if value in self._domain and value not in self._cur_domain:
            self._cur_domain.append(value); self._cur_domain.sort()
    def assign(self,value):
        if value not in self._domain: raise ValueError(f"{value} not in domain for {self.name}")
        self._assigned_value=value
    def unassign(self): self._assigned_value=None
    def is_assigned(self): return self._assigned_value is not None
    def get_assigned_value(self): return self._assigned_value
    def restore_curdom(self): self._cur_domain=list(self._domain)
    def __repr__(self): return f"Variable({self.name}, cur_domain={self.cur_domain()}, assigned={self._assigned_value})"
    def __hash__(self): return id(self)
