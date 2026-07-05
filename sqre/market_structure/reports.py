"""Market Structure report writer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class MarketStructureReport:
    """Write a concise descriptive market structure report."""

    def write(self, structures: pd.DataFrame, output_path: Path | str) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._build_report(structures), encoding="utf-8")
        return path

    def _build_report(self, structures: pd.DataFrame) -> str:
        if structures.empty:
            return "\n".join(
                [
                    "SQRE Market Structure Report",
                    "============================",
                    "",
                    "Symbol: UNKNOWN",
                    "Timeframe: UNKNOWN",
                    "Total Events Processed: 0",
                    "Total Structural Points: 0",
                    "Total Legs: 0",
                    "Total Structures Detected: 0",
                    "",
                    "Key observations:",
                    "- No market structures were detected.",
                    "- This report is descriptive and does not generate trading decisions.",
                    "",
                ]
            )

        first = structures.iloc[0]
        total_events = int(structures["Event_Count"].sum())
        total_points = int(structures["Point_Count"].sum())
        total_legs = int(structures["Leg_Count"].sum())
        most_common_direction = structures["Direction"].mode().iloc[0] if not structures["Direction"].mode().empty else "UNKNOWN"

        lines = [
            "SQRE Market Structure Report",
            "============================",
            "",
            f"Symbol: {first['Symbol']}",
            f"Timeframe: {first['Timeframe']}",
            f"Period: {structures['Start_Time'].min()} -> {structures['End_Time'].max()}",
            f"Total Events Processed: {total_events}",
            f"Total Structural Points: {total_points}",
            f"Total Legs: {total_legs}",
            f"Total Structures Detected: {len(structures)}",
            "",
            f"Average Structure Duration: {structures['Duration_Seconds'].mean():.2f} seconds",
            f"Average Price Displacement: {structures['Price_Displacement'].mean():.6f}",
            f"Most Common Direction: {most_common_direction}",
            f"Average Persistence Index: {structures['Persistence_Index'].mean():.4f}",
            f"Average Structural Complexity: {structures['Structural_Complexity'].mean():.4f}",
            f"Average Structural Stability: {structures['Structural_Stability'].mean():.4f}",
            f"Average Structural Confidence: {structures['Structural_Confidence'].mean():.4f}",
            "",
            "Top structures:",
        ]

        top_columns = [
            "Structure_ID",
            "Direction",
            "Lifecycle_Stage",
            "Persistence_Index",
            "Structural_Complexity",
            "Structural_Efficiency",
            "Structural_Confidence",
        ]
        top = structures.sort_values("Structural_Confidence", ascending=False).head(5)
        for _, row in top[top_columns].iterrows():
            lines.append(
                "- "
                f"{row['Structure_ID']}: "
                f"direction={row['Direction']}, "
                f"stage={row['Lifecycle_Stage']}, "
                f"persistence={row['Persistence_Index']:.4f}, "
                f"complexity={row['Structural_Complexity']:.4f}, "
                f"efficiency={row['Structural_Efficiency']:.4f}, "
                f"confidence={row['Structural_Confidence']:.4f}"
            )

        lines.extend(
            [
                "",
                "Key observations:",
                "- This report is descriptive and does not generate trading decisions.",
                "- Structural metrics should be reviewed before later SQRE research modules.",
                "- Sparse or noisy event datasets may produce fewer reliable structures.",
                "",
            ]
        )
        return "\n".join(lines)
