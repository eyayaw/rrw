"""
Download CBS Kerncijfers Wijken en Buurten (KWB) data via OData API.

Source: https://www.cbs.nl/nl-nl/reeksen/publicatie/kerncijfers-wijken-en-buurten
OData docs: https://www.cbs.nl/nl-nl/onze-diensten/open-data/statline-als-open-data/snelstartgids-odata-v4
"""

import csv
import urllib.request
import urllib.error
import urllib.parse
import json
from pathlib import Path

ODATA_BASE = "https://datasets.cbs.nl/odata/v1/CBS"

# Common measure codes
MEASURES = {
    "woz": "M001642",        # Gemiddelde WOZ-waarde van woningen
    "koopwoningen": "1014800_1",  # Koopwoningen (owner-occupied)
    "huurwoningen": "1014850_2",  # Huurwoningen totaal
    "woningvoorraad": "M000297",  # Housing stock
}

# KWB table IDs (2013+ use OData v1 with consistent structure)
KWB_TABLES = {
    2013: "82339NED",
    2014: "82931NED",
    2015: "83220NED",
    2016: "83487NED",
    2017: "83765NED",
    2018: "84286NED",
    2019: "84583NED",
    2020: "84799NED",
    2021: "85039NED",
    2022: "85318NED",
    2023: "85618NED",
    2024: "85984NED",
    2025: "86165NED",
}

OUT_DIR = Path("data/raw/cbs")


def download_kwb(
    year: int,
    output_dir: Path = OUT_DIR,
    measures: list[str] | None = None,
    suffix: str = "",
) -> Path | None:
    """Download KWB data via OData API, saving paginated results to CSV.

    Args:
        year: Year to download (2013-2025)
        output_dir: Output directory
        measures: List of measure codes to filter (e.g., ["M001642", "1014800_1"])
        suffix: Filename suffix (e.g., "-woz-koopwoningen")
    """
    table_id = KWB_TABLES.get(year)
    if not table_id:
        print(f"No table ID found for {year}")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"kwb-{year}{suffix}.csv"

    if output_path.exists():
        print(f"Already exists: {output_path}")
        return output_path

    url = f"{ODATA_BASE}/{table_id}/Observations"

    if measures:
        filter_expr = " or ".join(f"Measure eq '{m}'" for m in measures)
        url = f"{url}?$filter={urllib.parse.quote(filter_expr)}"

    print(f"Fetching {year} from {url} ...")

    try:
        writer = None
        row_count = 0
        page = 0

        with open(output_path, "w", newline="") as f:
            while url:
                page += 1
                with urllib.request.urlopen(url) as response:
                    result = json.load(response)
                    rows = result.get("value", [])

                    if rows and writer is None:
                        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                        writer.writeheader()

                    if writer:
                        writer.writerows(rows)
                        row_count += len(rows)

                    url = result.get("@odata.nextLink")
                    if url:
                        print(f"  Page {page}: {row_count} rows so far...")

        print(f"Saved {row_count} rows to: {output_path}")
        return output_path

    except urllib.error.HTTPError as e:
        print(f"Error fetching {year}: {e}")
        output_path.unlink(missing_ok=True)
        return None


def list_tables():
    """Print available KWB tables."""
    print("Available KWB tables:\n")
    print(f"{'Year':<12} {'Table ID':<12} {'OData URL'}")
    print("-" * 70)
    for year, table_id in KWB_TABLES.items():
        print(f"{year:<12} {table_id:<12} {ODATA_BASE}/{table_id}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Download CBS KWB data via OData API",
        epilog=f"Available measure shortcuts: {', '.join(MEASURES.keys())}",
    )
    parser.add_argument(
        "years",
        nargs="*",
        help="Years to download (e.g., 2020 2021 2022). Use 'all' for all years.",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=OUT_DIR, help="Output directory"
    )
    parser.add_argument(
        "-m", "--measures",
        nargs="+",
        help="Filter by measure codes (e.g., M001642 woz koopwoningen)",
    )
    parser.add_argument("--list", action="store_true", help="List available tables")
    args = parser.parse_args()

    if args.list:
        list_tables()
    else:
        if not args.years or args.years == ["all"]:
            years = list(KWB_TABLES.keys())
        else:
            years = [int(y) for y in args.years]

        # Resolve measure shortcuts
        measures = None
        suffix = ""
        if args.measures:
            measures = [MEASURES.get(m, m) for m in args.measures]
            suffix = "-" + "-".join(args.measures)

        for year in years:
            download_kwb(year, args.output_dir, measures, suffix)
