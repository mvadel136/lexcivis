import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


def digest(record: dict) -> str:
    body = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, path: str | Path, seq: int = 0, prev: str = GENESIS):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.seq, self.prev = seq, prev

    @property
    def head_path(self) -> Path:
        return self.path.with_suffix(".head")

    @classmethod
    def resume(cls, path: str | Path) -> "Ledger":
        ok, count, bad = verify(path)
        if not ok:
            raise ValueError(f"ledger is broken at seq {bad}")
        last = json.loads(Path(path).read_text(encoding="utf-8").splitlines()[-1])
        return cls(path, last["seq"] + 1, last["hash"])

    def append(self, kind: str, actor: str, payload: dict, stage: str = "", day: int | None = None) -> dict:
        record = {"seq": self.seq, "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "stage": stage, "sim_day": day, "kind": kind, "actor": actor, "payload": payload, "prev": self.prev}
        record["hash"] = digest(record)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.seq, self.prev = self.seq + 1, record["hash"]
        self.head_path.write_text(f"{self.seq} {self.prev}\n", encoding="utf-8")
        return record


def records(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def verify(path: str | Path) -> tuple[bool, int, int | None]:
    prev, count = GENESIS, 0
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines()):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            return False, count, number
        if record.get("prev") != prev or digest(record) != record.get("hash"):
            return False, count, record.get("seq", number)
        prev, count = record["hash"], count + 1
    head = Path(path).with_suffix(".head")
    if head.exists():
        expected_count, expected_hash = head.read_text(encoding="utf-8").split()
        if int(expected_count) != count or expected_hash != prev:
            return False, count, count
    return True, count, None
