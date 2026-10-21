"""Shared data models used by BookForge templates and renderers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BookConfig:
    """Configuration shared by a generated book."""

    title: str
    subtitle: str = ""
    page_count: int = 10

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be blank")
        if self.page_count < 1:
            raise ValueError("page_count must be at least 1")
