import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .ledger import records, verify


def generate(private_path: str | Path, public_path: str | Path) -> str:
    key = Ed25519PrivateKey.generate()
    private_path, public_path = Path(private_path), Path(public_path)
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                               serialization.NoEncryption()))
    private_path.chmod(0o600)
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    public_path.write_text(base64.b64encode(public).decode() + "\n", encoding="utf-8")
    return base64.b64encode(public).decode()


def _message(seq: int, head: str) -> bytes:
    return f"lexcivis-ledger-head:{seq}:{head}".encode()


def seal(ledger_path: str | Path, private_path: str | Path, signer: str) -> dict:
    ok, count, _ = verify(ledger_path)
    if not ok:
        raise ValueError("cannot seal a broken ledger")
    head = records(ledger_path)[-1]
    key = serialization.load_pem_private_key(Path(private_path).read_bytes(), password=None)
    public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    body = {"seq": head["seq"], "head": head["hash"], "records": count, "signer": signer,
            "signed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "public_key": base64.b64encode(public).decode(),
            "signature": base64.b64encode(key.sign(_message(head["seq"], head["hash"]))).decode()}
    Path(ledger_path).with_suffix(".sig").write_text(json.dumps(body, indent=1), encoding="utf-8")
    return body


def check(ledger_path: str | Path, trusted_public: str | None = None) -> tuple[bool, str]:
    sig_path = Path(ledger_path).with_suffix(".sig")
    if not sig_path.exists():
        return False, "not sealed"
    body = json.loads(sig_path.read_text(encoding="utf-8"))
    if trusted_public and body["public_key"] != trusted_public.strip():
        return False, "signed with an untrusted key"
    ok, count, _ = verify(ledger_path)
    if not ok:
        return False, "hash chain broken"
    sealed = [r for r in records(ledger_path) if r["seq"] <= body["seq"]]
    if not sealed or sealed[-1]["hash"] != body["head"]:
        return False, "sealed head does not match the ledger"
    public = Ed25519PublicKey.from_public_bytes(base64.b64decode(body["public_key"]))
    try:
        public.verify(base64.b64decode(body["signature"]), _message(body["seq"], body["head"]))
    except Exception:
        return False, "invalid signature"
    tail = count - body["records"]
    return True, f"signature valid for {body['records']} records by {body['signer']}" + (f"; {tail} later records not yet sealed" if tail else "")
