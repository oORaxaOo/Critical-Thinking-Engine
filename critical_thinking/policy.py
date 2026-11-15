"""Review-level selection kept separate from language-model reasoning."""

from .models import Intent, ReviewLevel, ReviewRequest

_CRITICAL_TERMS = (
    "sicherheit", "security", "datenschutz", "privacy", "zugriff",
    "berechtigung", "irreversibel", "unwiderruflich", "migration",
    "löschen", "loeschen", "produktive umgebung", "systemweit",
    "architektur ändern", "architektur aendern", "komplette architektur",
)
_TECHNICAL_TERMS = (
    "hermes", "plugin", "modell", "llm", "ki-modell", "api",
    "architektur", "code", "software", "datenbank", "server",
    "hardware", "integration", "automatisierung", "workflow",
)
_REVIEW_REQUESTS = (
    "/ct review", "/ct critical", "prüfe kritisch", "pruefe kritisch",
    "hinterfrage das", "red team", "red-team", "widersprich mir",
)


def choose_review_level(message: str, intent: Intent) -> ReviewRequest:
    """Choose the smallest review level justified by explicit signals."""
    text = " ".join(message.casefold().split())
    requested = any(token in text for token in _REVIEW_REQUESTS)
    critical_hits = tuple(term for term in _CRITICAL_TERMS if term in text)
    technical = any(term in text for term in _TECHNICAL_TERMS)

    if intent in (Intent.PERSONAL_EXPERIENCE, Intent.OPINION):
        return ReviewRequest(intent, ReviewLevel.NORMAL, "Personal experience and opinions are not automatically challenged.")

    if critical_hits:
        return ReviewRequest(
            intent, ReviewLevel.CRITICAL,
            "High-impact or sensitive decision signal detected.",
            requested, critical_hits,
        )

    if requested:
        return ReviewRequest(intent, ReviewLevel.CRITICAL, "The user explicitly requested a critical review.", True)

    if intent in (Intent.PROJECT_PROPOSAL, Intent.DECISION) and technical:
        return ReviewRequest(
            intent, ReviewLevel.REVIEW,
            "Technical proposal or decision detected.",
            False, ("technical_project_signal",),
        )

    return ReviewRequest(intent, ReviewLevel.NORMAL, "No sufficient signal for an unsolicited review.")


def should_inject_review(request: ReviewRequest) -> bool:
    """Return whether this request should add review guidance to the turn."""
    return request.level is not ReviewLevel.NORMAL
