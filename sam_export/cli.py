"""Command-line interface for SAM.gov export tool."""

import argparse
import sys
from datetime import datetime, timedelta

from .client import SamGovClient
from .exporter import export_to_csv


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Export SAM.gov contract opportunities to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m sam_export.cli                    # Last 30 days, NAICS 212
  python -m sam_export.cli --days 90          # Last 90 days
  python -m sam_export.cli --naics 236        # Construction NAICS codes
  python -m sam_export.cli --output my.csv    # Custom output filename
        """,
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30, max: 365)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output CSV filename (auto-generated if not specified)",
    )
    parser.add_argument(
        "--naics",
        type=str,
        default="212",
        help="NAICS code prefix to filter (default: 212 for Mining)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of records to fetch (default: all)",
    )

    args = parser.parse_args()

    # Validate days
    if args.days < 1 or args.days > 365:
        print("Error: --days must be between 1 and 365")
        sys.exit(1)

    # Calculate date range
    date_to = datetime.now()
    date_from = date_to - timedelta(days=args.days)

    print(f"SAM.gov Opportunities Export")
    print(f"=" * 40)
    print(f"NAICS prefix: {args.naics}")
    print(f"Date range: {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}")
    print()

    # Initialize client
    try:
        client = SamGovClient()
    except ValueError as e:
        print(f"Error: {e}")
        print("Create a .env file with SAM_API_KEY=your_key")
        sys.exit(1)

    # Fetch opportunities
    print("Fetching opportunities...")
    try:
        opportunities = client.search_opportunities(
            naics_code=args.naics,
            posted_from=date_from,
            posted_to=date_to,
            limit=args.limit,
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    if not opportunities:
        print("No opportunities found matching criteria.")
        sys.exit(0)

    print(f"Found {len(opportunities)} opportunities")
    print()

    # Export to CSV
    print("Exporting to CSV...")
    output_path = export_to_csv(
        opportunities,
        output_path=args.output,
        date_from=date_from,
        date_to=date_to,
    )

    print(f"Export complete: {output_path}")
    print(f"Total records: {len(opportunities)}")


if __name__ == "__main__":
    main()
