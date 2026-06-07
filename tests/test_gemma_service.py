from datetime import datetime, timezone

from gemma_service.application.gemma_service import GemmaReflectionService
from gemma_service.application.memory import ConversationMemory
from gemma_service.application.prompt_builder import PromptBuilder
from gemma_service.domain.models import ConversationTurn, SessionSnapshot


def make_snapshot() -> SessionSnapshot:
    return SessionSnapshot(
        session_id="session-1",
        user_id="user-1",
        label="Deep Work",
        started_at=datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc),
        ended_at=datetime(2026, 1, 1, 11, 0, tzinfo=timezone.utc),
        average_focus=84.5,
        drift_count=3,
        top_apps=["VSCode", "Slack"],
        drift_timeline=["T+42m: drift after Slack switch"],
        journal_entry="Felt productive early, then got pulled into messages.",
        recent_wins=["Completed a 90-minute coding block"],
        historical_baseline="Usually strongest between 9 and 11 AM",
    )


def test_distilled_prompt_contains_session_artifact() -> None:
    builder = PromptBuilder()
    prompt = builder.build_summary_prompt("artifact content")

    assert "Cognitive Performance Coach" in prompt
    assert "artifact content" in prompt


def test_conversation_memory_compresses_oldest_turns() -> None:
    memory = ConversationMemory(max_turns=6, summarize_after=10)
    for index in range(11):
        memory.add_turn(ConversationTurn(role="user", content=f"turn-{index}", created_at=datetime.now(timezone.utc)))

    assert len(memory.state_blocks()) == 1
    assert len(memory.snapshot()) <= 6


def test_reflection_service_builds_local_result() -> None:
    service = GemmaReflectionService()
    result = service.reflect(make_snapshot(), historical_summaries=["App usage and drift repeated around Slack."])

    assert result.model == "gemma4:31b"
    assert "Session Artifact" in result.prompt
    assert result.recommendations
