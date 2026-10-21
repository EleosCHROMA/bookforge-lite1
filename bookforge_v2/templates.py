"""Book-specific content templates, kept separate from PDF rendering."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TablePage:
    """A simple page of tabular content for the PDF renderer."""

    heading: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


class BookTemplate(Protocol):
    """Interface implemented by each type of book BookForge can generate."""

    def build_pages(self, page_count: int) -> list[TablePage]:
        """Return the content pages for a requested book length."""
        ...


class VehicleMaintenanceTemplate:
    """Build blank service-record pages for a vehicle maintenance logbook."""

    columns = ("Date", "Mileage", "Service / Repairs", "Cost", "Next Due")

    def build_pages(self, page_count: int) -> list[TablePage]:
        if page_count < 1:
            raise ValueError("page_count must be at least 1")
        blank_rows = tuple(("", "", "", "", "") for _ in range(12))
        return [
            TablePage(
                heading=f"Maintenance Records — Page {number}",
                columns=self.columns,
                rows=blank_rows,
            )
            for number in range(1, page_count + 1)
        ]
