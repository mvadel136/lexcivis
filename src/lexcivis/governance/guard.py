from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    ALLOWED = "ALLOWED"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    BLOCKED_MANDATE = "BLOCKED_MANDATE"
    BLOCKED_ORDER = "BLOCKED_ORDER"


@dataclass(frozen=True)
class OrderRule:
    id: str
    actions: frozenset
    requires_all: frozenset
    text: str


class Guard:
    def __init__(self, config: dict):
        self.agents = config["agents"]
        rules = config["coordination"]
        self.order = [OrderRule(r["id"], frozenset(r["actions"]), frozenset(r["requires_all"]), r["rule"])
                      for r in rules if r["type"] == "order"]
        gates = [r for r in rules if r["type"] == "human_gate"]
        self.human_gate = frozenset(a for r in gates for a in r["actions"])
        self.human_text = " ".join(r["rule"] for r in gates)

    def review(self, agent_id: str, actions: list[dict], done: set[str]) -> list[dict]:
        allowed = set(self.agents[agent_id]["may"])
        reviewed = []
        for action in actions:
            name = str(action.get("action", ""))
            status, rule = self._status(agent_id, name, allowed, done)
            if status is Status.ALLOWED:
                done.add(f"{agent_id}:{name}")
            reviewed.append({**action, "status": status.value, "rule": rule})
        return reviewed

    def _status(self, agent_id: str, name: str, allowed: set, done: set) -> tuple[Status, str]:
        if name not in allowed:
            return Status.BLOCKED_MANDATE, f"{agent_id} may not '{name}'"
        for rule in self.order:
            missing = sorted(rule.requires_all - done)
            if name in rule.actions and missing:
                return Status.BLOCKED_ORDER, f"{rule.id}: {rule.text} Missing: {', '.join(missing)}."
        if name in self.human_gate:
            return Status.AWAITING_HUMAN, self.human_text
        return Status.ALLOWED, ""
