# CTE Architecture — v0.1

## Purpose

The Critical Thinking Engine (CTE) is a lightweight decision-support layer for Hermes Agent. It reduces reflexive agreement by injecting bounded review guidance when deterministic routing identifies a technical proposal, decision, technical factual claim, or explicit review request.

## Boundaries

- CTE: classifies the conversational intent, selects review intensity, and supplies decision-quality instructions.
- Reliability Engine: observes technical runtime/model reliability signals.
- Evidence Engine: verifies concrete software/project outcomes using tests and other evidence.
- Hermes: remains responsible for model execution, tools, permissions, approvals, and provider behavior.

The CTE is not a truth oracle. Its classifier is heuristic, and the active model can still produce incorrect reasoning.

## v0.1 flow

1. Hermes calls the plugin's `pre_llm_call` hook once per turn.
2. CTE reads only the current `user_message` field.
3. A conservative deterministic classifier assigns an intent.
4. A policy selects NORMAL, REVIEW, or CRITICAL.
5. Only REVIEW/CRITICAL turns receive a short context block.
6. All exceptions fail open: Hermes continues without CTE guidance.

## Review policy

- NORMAL: personal experiences, opinions, routine questions, ambiguous messages, and non-technical factual statements.
- REVIEW: technical project proposals and decisions; technical factual claims receive a separate evidence-focused review.
- CRITICAL: explicit critical-review requests and high-impact decisions such as security, privacy, irreversible changes, or system-wide architecture changes.

Personal experiences take precedence over keyword matches so they are not automatically challenged. Opinions are not automatically challenged unless the user explicitly requests a review. The classifier recognizes common hedged proposals while avoiding generic wish phrases that would turn questions such as "I want to know how this works" into project decisions.

## Position contract

For reviewed proposals and decisions, the model is asked to choose SUPPORT, CHANGE, REJECT, or INSUFFICIENT_INFORMATION; state decisive reasons; separate facts, assumptions, and unknowns; and suggest a better alternative when appropriate.

For technical factual claims, the model is asked to distinguish verified evidence from inference and unknowns. It must not invent tests, source checks, or citations. If the claim cannot be verified, it should say so and identify what evidence would settle it.

This is an instruction contract, not a verified structured output. The hook appends guidance to the current user message; it is not a privileged system-level policy and does not guarantee that the model will follow it. v0.1 does not claim to validate the truth of the model's answer.

## Privacy and performance

- No additional model calls.
- No network access.
- No third-party runtime dependencies.
- No transcript, prompt, or response storage.
- No Decision Ledger in v0.1.
- The hook inspects only the current user message and returns a small instruction block.
