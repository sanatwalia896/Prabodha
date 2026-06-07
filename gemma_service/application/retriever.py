from collections import Counter


class SimilarityRetriever:
    def retrieve(self, query: str, corpus: list[str], top_k: int = 3) -> list[str]:
        query_tokens = self._tokens(query)
        scored = []
        for item in corpus:
            score = self._score(query_tokens, self._tokens(item))
            scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for score, item in scored[:top_k] if score > 0]

    @staticmethod
    def _tokens(text: str) -> Counter[str]:
        tokens = [token.lower().strip(".,:;()[]{}") for token in text.split()]
        return Counter(token for token in tokens if token)

    @staticmethod
    def _score(left: Counter[str], right: Counter[str]) -> int:
        overlap = 0
        for token, count in left.items():
            overlap += min(count, right.get(token, 0))
        return overlap
