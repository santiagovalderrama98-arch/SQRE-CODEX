from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd


class BasicEventReport:
    def write(self, events: pd.DataFrame, output_path: Path | str) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["SQRE Event Detection Report", "=" * 27, ""]
        lines.append(f"Total events: {len(events)}")

        if events.empty:
            lines.append("No events detected.")
        else:
            lines.append("")
            lines.append("Events by type:")
            counts = Counter(events["EventType"])
            for event_type, count in sorted(counts.items()):
                lines.append(f"- {event_type}: {count}")
            lines.append("")
            lines.append(f"First event: {events.iloc[0]['Date']}")
            lines.append(f"Last event: {events.iloc[-1]['Date']}")

        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
