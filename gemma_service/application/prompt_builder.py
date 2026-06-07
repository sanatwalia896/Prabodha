from gemma_service.domain.models import SessionSnapshot


class PromptBuilder:
    SYSTEM_PERSONA = "You are a Cognitive Performance Coach."

    def build_summary_prompt(self, artifact: str) -> str:
        return (
            f"System: {self.SYSTEM_PERSONA}\n"
            "Task: Analyze the session artifact.\n"
            "Instruction: Identify the peak focus window, the primary friction point, and provide three actionable tips.\n"
            "Constraint: Use only the provided data. Do not diagnose medical conditions.\n\n"
            f"Context:\n{artifact}\n"
        )

    def build_pattern_prompt(self, comparison_block: str) -> str:
        return (
            "System: You are a Behavioral Data Analyst.\n"
            "Task: Discover correlations between application usage and attention drift.\n"
            "Output: Produce a distraction correlation map.\n\n"
            f"Context:\n{comparison_block}\n"
        )

    def build_motivation_prompt(self, snapshot: SessionSnapshot) -> str:
        wins = "\n".join(f"- {item}" for item in snapshot.recent_wins) or "- No recent wins recorded"
        return (
            "System: You are a motivational strategist.\n"
            "Task: Encourage the user by referencing a recent win.\n\n"
            f"Recent Wins:\n{wins}\n"
            f"Current Focus Baseline: {snapshot.historical_baseline or 'Unavailable'}\n"
        )
