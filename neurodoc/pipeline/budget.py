"""LLM prompt budget tracker."""
from __future__ import annotations


class BudgetExhausted(Exception):
    pass


class Budget:
    def __init__(self, total: int = 500):
        self.total = total
        self.used = 0
        self.breakdown: dict[str, int] = {}

    def charge(self, phase: str, n: int = 1) -> None:
        if self.used + n > self.total:
            raise BudgetExhausted(
                f"Budget exhausted: {self.used}/{self.total} used. "
                f"Attempted to charge {n} more in phase '{phase}'."
            )
        self.used += n
        self.breakdown[phase] = self.breakdown.get(phase, 0) + n

    def remaining(self) -> int:
        return self.total - self.used

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "used": self.used,
            "remaining": self.remaining(),
            "breakdown": self.breakdown,
        }

    def load_dict(self, d: dict) -> None:
        self.total = d.get("total", self.total)
        self.used = d.get("used", 0)
        self.breakdown = d.get("breakdown", {})
