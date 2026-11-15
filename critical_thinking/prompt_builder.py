"""Build concise, bounded instructions for the active model."""

from .models import ReviewLevel, ReviewRequest

_BASE = """Critical Thinking Engine — response guidance:
Do not agree merely to be agreeable. Form an independent, reasoned position.
Choose one: SUPPORT, CHANGE, REJECT, or INSUFFICIENT_INFORMATION.
State the decisive reasons plainly. If the proposal is flawed, say so directly and
explain why; offer a practical better alternative. If it is sound, say so and explain
why. Do not manufacture disagreement or artificial balance.
Separate known facts, assumptions, and unknowns. Never present an unverified claim
as proven. If new evidence defeats your position, revise it openly.
Respect personal feelings; do not treat emotions or preferences as propositions to refute.
The goal is better decisions and stronger critical thinking, not winning an argument."""


def build_review_context(request: ReviewRequest) -> str:
    """Return a small instruction block; never include the original user message."""
    if request.level is ReviewLevel.NORMAL:
        return ""

    if request.level is ReviewLevel.CRITICAL:
        extra = """Review intensity: CRITICAL.
Check material assumptions, dependencies, security/privacy implications, failure modes,
reversibility, simpler alternatives, and what evidence would change the recommendation.
Be decisive, but make uncertainty explicit."""
    else:
        extra = """Review intensity: REVIEW.
Evaluate whether the proposal solves the stated problem. Give a clear recommendation,
the strongest reasons, important trade-offs, and a better alternative if warranted."""

    return f"{_BASE}\n\n{extra}\n\nRouting reason: {request.reason}"
