from datetime import datetime

from gemma_service.domain.models import SessionSnapshot


class SessionDistiller:
    def distill(self, snapshot: SessionSnapshot) -> str:
        lines = [
            "# Session Artifact",
            f"- Session ID: {snapshot.session_id}",
            f"- Label: {snapshot.label or 'Unlabeled'}",
            f"- Started: {self._prune_timestamp(snapshot.started_at)}",
            f"- Ended: {self._prune_timestamp(snapshot.ended_at) if snapshot.ended_at else 'Active'}",
            "",
            "## Quantitative Snapshot",
            f"- Average Focus: {snapshot.average_focus:.1f}%",
            f"- Drift Count: {snapshot.drift_count}",
            f"- Top Apps: {', '.join(snapshot.top_apps) if snapshot.top_apps else 'None'}",
            "",
            "## Timeline of Friction",
        ]
        if snapshot.drift_timeline:
            lines.extend(f"- {item}" for item in snapshot.drift_timeline)
        else:
            lines.append("- No major friction detected")
        lines.extend(
            [
                "",
                "## Subjective Layer",
                f"- Journal: {snapshot.journal_entry or 'No journal entry provided'}",
                "",
                "## Historical Baseline",
                f"- {snapshot.historical_baseline or 'No baseline available'}",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _prune_timestamp(value: datetime | None) -> str:
        if value is None:
            return "Unknown"
        return value.replace(microsecond=0).isoformat()
