from collections.abc import Callable
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def add(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.flush()
        return obj

    def get(self, primary_key: object) -> ModelT | None:
        return self.db.get(self.model, primary_key)

    def list(self, predicate: Callable | None = None) -> list[ModelT]:
        query = self.db.query(self.model)
        if predicate is not None:
            query = query.filter(predicate)
        return query.all()
