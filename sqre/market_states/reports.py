"""Market States report writer."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from sqre.market_states.models import MarketState


STATE_ORDER = [
    "DIRECTIONAL_EXPANSION",
    "DIRECTIONAL_DISPLACEMENT",
    "DIRECTIONAL_DRIFT",
    "NEUTRAL_COMPRESSION",
    "COMPLEX_CONSOLIDATION",
    "VOLATILE_ROTATION",
    "LOW_QUALITY_STRUCTURE",
    "UNCLASSIFIED",
]

DISPLAY_NAMES = {
    "DIRECTIONAL_EXPANSION": "Directional Expansion",
    "DIRECTIONAL_DISPLACEMENT": "Directional Displacement",
    "DIRECTIONAL_DRIFT": "Directional Drift",
    "NEUTRAL_COMPRESSION": "Neutral Compression",
    "COMPLEX_CONSOLIDATION": "Complex Consolidation",
    "VOLATILE_ROTATION": "Volatile Rotation",
    "LOW_QUALITY_STRUCTURE": "Low Quality Structure",
    "UNCLASSIFIED": "Unclassified",
}


class MarketStatesReport:
    """Write a descriptive Market States report."""

    def write(self, states: list[MarketState], output_path: Path | str) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._build_report(states), encoding="utf-8")
        return path

    def _build_report(self, states: list[MarketState]) -> str:
        if not states:
            return self._empty_report()

        counts = Counter(state.market_state for state in states)
        most_common_state = self._most_common_state(counts)
        highest_confidence_state = max(states, key=lambda state: state.state_confidence)
        average_confidence = sum(state.state_confidence for state in states) / len(states)

        lines = [
            "SQRE Market States Report",
            "=========================",
            "",
            f"Symbol: {states[0].symbol}",
            f"Timeframe: {states[0].timeframe}",
            f"Period: {min(state.start_time for state in states)} -> {max(state.end_time for state in states)}",
            f"Structures Processed: {len(states)}",
            f"States Generated: {len(states)}",
            "",
            "States by Type:",
        ]
        lines.extend(f"- {DISPLAY_NAMES[state]}: {counts.get(state, 0)}" for state in STATE_ORDER)
        lines.extend(
            [
                "",
                f"Average State Confidence: {average_confidence:.4f}",
                f"Most Common State: {DISPLAY_NAMES[most_common_state]}",
                (
                    "Highest Confidence State: "
                    f"{highest_confidence_state.state_id} "
                    f"({DISPLAY_NAMES[highest_confidence_state.market_state]}, "
                    f"{highest_confidence_state.state_confidence:.4f})"
                ),
                "",
                "Key Observations:",
                "- This report is descriptive and summarizes structure classifications.",
                "- State counts describe how current structures fit the v1.0 taxonomy.",
                "- Unclassified structures do not match the configured v1.0 rules.",
                "",
            ]
        )
        return "\n".join(lines)

    def _empty_report(self) -> str:
        lines = [
            "SQRE Market States Report",
            "=========================",
            "",
            "Symbol: UNKNOWN",
            "Timeframe: UNKNOWN",
            "Period: UNKNOWN",
            "Structures Processed: 0",
            "States Generated: 0",
            "",
            "States by Type:",
        ]
        lines.extend(f"- {DISPLAY_NAMES[state]}: 0" for state in STATE_ORDER)
        lines.extend(
            [
                "",
                "Average State Confidence: 0.0000",
                "Most Common State: Unclassified",
                "Highest Confidence State: NONE",
                "",
                "Key Observations:",
                "- No structures were available for classification.",
                "",
            ]
        )
        return "\n".join(lines)

    def _most_common_state(self, counts: Counter[str]) -> str:
        return max(STATE_ORDER, key=lambda state: (counts.get(state, 0), -STATE_ORDER.index(state)))
