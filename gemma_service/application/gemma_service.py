from gemma_service.application.distiller import SessionDistiller
from gemma_service.application.prompt_builder import PromptBuilder
from gemma_service.application.retriever import SimilarityRetriever
from gemma_service.domain.models import ReflectionResult, SessionSnapshot
from gemma_service.application.client import LLMClient, DummyLLMClient


class GemmaReflectionService:
    def __init__(
        self,
        client: LLMClient | None = None,
        model: str = "gemma4:31b",
    ) -> None:
        self.client = client or DummyLLMClient()
        self.model = model
        self.distiller = SessionDistiller()
        self.prompt_builder = PromptBuilder()
        self.retriever = SimilarityRetriever()

    def reflect(self, snapshot: SessionSnapshot, historical_summaries: list[str] | None = None) -> ReflectionResult:
        artifact = self.distiller.distill(snapshot)
        historical_summaries = historical_summaries or []
        retrieval_query = f"{snapshot.label or ''} {snapshot.journal_entry or ''} {snapshot.top_apps}"
        similar_context = self.retriever.retrieve(retrieval_query, historical_summaries, top_k=2)
        prompt_parts = [self.prompt_builder.build_summary_prompt(artifact)]
        if similar_context:
            prompt_parts.append("Similar Past Experiences:\n" + "\n".join(f"- {item}" for item in similar_context))
        prompt = "\n".join(prompt_parts)
        raw_response = self.client.generate(prompt, self.model)
        summary = self._extract_summary(raw_response)
        recommendations = self._extract_recommendations(raw_response)
        return ReflectionResult(summary=summary, recommendations=recommendations, prompt=prompt, model=self.model)

    @staticmethod
    def _extract_summary(raw_response: str) -> str:
        cleaned = raw_response.strip()
        if not cleaned:
            return "No reflection generated."
        return cleaned

    @staticmethod
    def _extract_recommendations(raw_response: str) -> list[str]:
        if not raw_response.strip():
            return ["Review the session artifact again."]
        return ["Review the peak-focus window.", "Reduce the dominant friction source.", "Test one schedule change tomorrow."]
