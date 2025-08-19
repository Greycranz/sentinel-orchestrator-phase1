from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Dict, List

# We only *detect* keys for now; no outbound calls (safe in sandbox)
PROVIDER_VARS = {
    "openai":     ["OPENAI_API_KEY"],
    "anthropic":  ["ANTHROPIC_API_KEY"],
    "cohere":     ["COHERE_API_KEY"],
    "google":     ["GOOGLE_API_KEY", "GOOGLE_VERTEX_PROJECT_ID"],
    "mistral":    ["MISTRAL_API_KEY"],
    "groq":       ["GROQ_API_KEY"],
}

@dataclass
class Provider:
    name: str
    keys_present: bool
    details: Dict[str, bool]

def detect_providers() -> List[Provider]:
    out: List[Provider] = []
    for name, vars_ in PROVIDER_VARS.items():
        details = {v: bool(os.getenv(v, "")) for v in vars_}
        any_key = any(details.values())
        out.append(Provider(name=name, keys_present=any_key, details=details))
    return out

def aggregate_stub(prompt: str, providers: List[str]) -> Dict:
    enabled = [p.name for p in detect_providers() if p.keys_present]
    use = providers or enabled or ["openai"]  # default to openai label if nothing set
    # No real LLM calls here; we just echo structure you can wire later.
    answers = [{"provider": p, "text": f"[stub:{p}] {prompt}"} for p in use]
    # naive "best" = first
    best = answers[0] if answers else {"provider": None, "text": ""}
    return {"used_providers": use, "answers": answers, "best": best}
