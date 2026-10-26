"""Command-line entry point for the modular BookForge V2 prototype."""

import argparse
from pathlib import Path

from .models import BookConfig
from .renderer import render_book
from .templates import VehicleMaintenanceTemplate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a printable vehicle maintenance logbook PDF.")
    parser.add_argument("--vehicle", default="My Vehicle", help="Vehicle name shown on the cover")
    parser.add_argument("--subtitle", default="Vehicle Maintenance Logbook", help="Subtitle shown on the cover")
    parser.add_argument("--records", type=int, default=10, help="Number of record pages to generate")
    parser.add_argument("--output", default="output/vehicle_logbook_v2.pdf", help="Destination PDF path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = BookConfig(title=f"{args.vehicle.strip()} Maintenance Logbook", subtitle=args.subtitle, page_count=args.records)
        output = render_book(config, VehicleMaintenanceTemplate(), Path(args.output))
    except (ValueError, OSError) as error:
        print(f"Error: {error}")
        return 2
    print(f"Created PDF: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
