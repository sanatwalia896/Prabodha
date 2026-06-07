from dataclasses import dataclass
from datetime import datetime

from gemma_service.domain.models import ConversationTurn


@dataclass(frozen=True, slots=True)
class ConversationState:
    user_goal: str
    advice_given: str
    user_reaction: str


class ConversationMemory:
    def __init__(self, max_turns: int = 6, summarize_after: int = 10) -> None:
        self.max_turns = max_turns
        self.summarize_after = summarize_after
        self._turns: list[ConversationTurn] = []
        self._state_blocks: list[ConversationState] = []
        self._turns_added = 0
        self._last_summarized_turn = 0

    def add_turn(self, turn: ConversationTurn) -> None:
        self._turns.append(turn)
        self._turns_added += 1
        if self._turns_added - self._last_summarized_turn > self.summarize_after:
            self._compress_oldest_turns()
            self._last_summarized_turn = self._turns_added
        self._trim_window()

    def snapshot(self) -> list[ConversationTurn]:
        return list(self._turns)

    def state_blocks(self) -> list[ConversationState]:
        return list(self._state_blocks)

    def _compress_oldest_turns(self) -> None:
        if len(self._turns) < 4:
            return
        oldest = self._turns[:4]
        self._state_blocks.append(
            ConversationState(
                user_goal=oldest[0].content,
                advice_given=oldest[1].content if len(oldest) > 1 else "",
                user_reaction=oldest[3].content if len(oldest) > 3 else "",
            )
        )
        self._turns = self._turns[4:]

    def _trim_window(self) -> None:
        if len(self._turns) > self.max_turns:
            self._turns = self._turns[-self.max_turns :]
