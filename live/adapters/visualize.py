"""
visualize.py

Command-line interface for Stage 2C visualization.

Examples:

Generate all visualizations:

    python -m live.adapters.visualize \
        --edition wc2026 \
        --all

Generate probability timeline:

    python -m live.adapters.visualize \
        --edition wc2026 \
        --timeline

Generate timeline for selected teams:

    python -m live.adapters.visualize \
        --edition wc2026 \
        --timeline \
        --teams Spain Argentina France

Generate top-10 table:

    python -m live.adapters.visualize \
        --edition wc2026 \
        --top10
"""

from __future__ import annotations

import argparse

from live.visualization import (
    generate_top_10_by_snapshot,
    plot_team_probability_timeline,
)


def generate_timeline(
    edition: str,
    teams: list[str] | None = None,
):
    """
    Generate the champion probability timeline chart.
    """

    output_path = plot_team_probability_timeline(
        edition=edition,
        teams=teams,
    )

    print(f"Timeline chart: {output_path}")

    return output_path


def generate_top_10(edition: str):
    """
    Generate the top-10 favorites table for every snapshot.
    """

    output_path = generate_top_10_by_snapshot(
        edition=edition
    )

    print(f"Top-10 table:  {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate FIFA World Cup champion "
            "probability visualizations."
        )
    )

    parser.add_argument(
        "--edition",
        required=True,
        help="Tournament edition, for example wc2026",
    )

    parser.add_argument(
        "--timeline",
        action="store_true",
        help="Generate champion probability timeline chart",
    )

    parser.add_argument(
        "--top10",
        action="store_true",
        help="Generate top-10 favorites table",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all Stage 2C visualization outputs",
    )

    parser.add_argument(
        "--teams",
        nargs="+",
        default=None,
        help=(
            "Teams to include in the timeline chart. "
            "If omitted, the latest top five teams are used."
        ),
    )

    args = parser.parse_args()

    if args.teams and not (args.timeline or args.all):
        parser.error(
            "--teams can only be used with --timeline or --all"
        )

    if not any([
        args.timeline,
        args.top10,
        args.all,
    ]):
        parser.error(
            "Select --timeline, --top10, or --all"
        )

    print("=" * 80)
    print(f"{args.edition.upper()} VISUALIZATION")
    print("=" * 80)

    if args.timeline or args.all:
        generate_timeline(
            edition=args.edition,
            teams=args.teams,
        )

    if args.top10 or args.all:
        generate_top_10(
            edition=args.edition
        )

    print("=" * 80)
    print("Visualization generation completed.")
    print("=" * 80)


if __name__ == "__main__":
    main()