"""Conservative, deterministic message classification.

This is a routing heuristic, not a truth detector. Ambiguous messages stay UNKNOWN.
"""

from .models import Intent

_PERSONAL = (
    "ich fühle", "ich fuehle", "ich habe angst", "ich bin traurig",
    "ich bin überfordert", "ich bin ueberfordert", "ich vermisse",
    "ich freue mich", "ich bin enttäuscht", "ich bin enttaeuscht",
)
_OPINION = (
    "ich finde", "meiner meinung", "ich mag", "ich glaube", "ich denke",
    "ich bevorzuge", "für mich", "fuer mich",
)
_PROPOSAL = (
    "ich möchte", "ich moechte", "ich will", "wir sollten", "lass uns",
    "ich schlage vor", "mein vorschlag", "ich plane", "wir könnten",
    "wir koennten",
)
_DECISION = (
    "wir entscheiden", "ich entscheide", "sollen wir", "soll ich",
    "sollen wir jetzt", "ich werde", "wir werden", "wir müssen",
    "wir muessen",
)
_QUESTION_STARTS = ("warum ", "wie ", "was ", "welche ", "welcher ", "kann ", "können ", "koennen ")
_FACTUAL_MARKERS = (
    "ist technisch möglich", "ist technisch moeglich", "funktioniert",
    "unterstützt", "unterstuetzt", "verursacht", "benötigt", "benoetigt",
    "garantiert", "immer", "niemals", "beweist", "ist kompatibel",
)


def classify_message(message: str) -> Intent:
    """Classify a single user message without storing or transmitting it."""
    if not isinstance(message, str) or not message.strip():
        return Intent.UNKNOWN

    text = " ".join(message.casefold().split())

    # Personal experience has priority: do not convert an emotional statement
    # into a debate simply because it contains technical vocabulary.
    if any(marker in text for marker in _PERSONAL):
        return Intent.PERSONAL_EXPERIENCE

    # Detect the actual proposal/decision before hedging phrases such as
    # "I think" or "I believe". Otherwise common proposal prefaces hide intent.
    if any(marker in text for marker in _DECISION):
        return Intent.DECISION
    if any(marker in text for marker in _PROPOSAL):
        return Intent.PROJECT_PROPOSAL

    if any(marker in text for marker in _OPINION):
        return Intent.OPINION
    if text.endswith("?") or text.startswith(_QUESTION_STARTS):
        return Intent.QUESTION
    if any(marker in text for marker in _FACTUAL_MARKERS):
        return Intent.FACTUAL_CLAIM
    return Intent.UNKNOWN
