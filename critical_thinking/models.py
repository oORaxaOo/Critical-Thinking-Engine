"""Small, explicit data models used by the CTE.

The core intentionally has no third-party runtime dependencies.
"""

from dataclasses import dataclass, field
from enum import Enum


class Intent(str, Enum):
    PERSONAL_EXPERIENCE = "personal_experience"
    OPINION = "opinion"
    FACTUAL_CLAIM = "factual_claim"
    PROJECT_PROPOSAL = "project_proposal"
    DECISION = "decision"
    QUESTION = "question"
    UNKNOWN = "unknown"


class ReviewLevel(str, Enum):
    NORMAL = "normal"
    REVIEW = "review"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ReviewRequest:
    intent: Intent
    level: ReviewLevel
    reason: str
    user_requested: bool = False
    signals: tuple[str, ...] = field(default_factory=tuple)
