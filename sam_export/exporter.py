"""CSV exporter for SAM.gov opportunities."""

import csv
import io
from datetime import datetime
from typing import Any, Optional


# All columns to export, in order
COLUMNS = [
    # Basic info
    "noticeId",
    "title",
    "solicitationNumber",
    "type",
    "postedDate",
    "archiveDate",
    "active",
    # Classification
    "naicsCode",
    "classificationCode",
    "typeOfSetAside",
    "typeOfSetAsideDescription",
    # Organization
    "fullParentPathName",
    "organizationType",
    "officeAddress_city",
    "officeAddress_state",
    "officeAddress_zipcode",
    # Primary contact
    "contact_name",
    "contact_email",
    "contact_phone",
    "contact_title",
    # Place of performance
    "pop_street",
    "pop_city",
    "pop_state",
    "pop_zip",
    "pop_country",
    # Award info
    "award_number",
    "award_amount",
    "award_date",
    "award_awardee_name",
    "award_awardee_location",
    # Links
    "uiLink",
    "description_url",
    "resourceLinks",
]


def flatten_opportunity(opp: dict) -> dict:
    """Flatten a nested opportunity dict into a flat dict for CSV export."""
    flat = {}

    # Basic fields (direct copy)
    for field in [
        "noticeId",
        "title",
        "solicitationNumber",
        "type",
        "postedDate",
        "archiveDate",
        "active",
        "naicsCode",
        "classificationCode",
        "typeOfSetAside",
        "typeOfSetAsideDescription",
        "fullParentPathName",
        "organizationType",
        "uiLink",
    ]:
        flat[field] = opp.get(field, "")

    # Office address
    office_addr = opp.get("officeAddress", {}) or {}
    flat["officeAddress_city"] = office_addr.get("city", "")
    flat["officeAddress_state"] = office_addr.get("state", "")
    flat["officeAddress_zipcode"] = office_addr.get("zipcode", "")

    # Primary contact (first in list)
    contacts = opp.get("pointOfContact", []) or []
    if contacts:
        contact = contacts[0]
        flat["contact_name"] = contact.get("fullName", "")
        flat["contact_email"] = contact.get("email", "")
        flat["contact_phone"] = contact.get("phone", "")
        flat["contact_title"] = contact.get("title", "")
    else:
        flat["contact_name"] = ""
        flat["contact_email"] = ""
        flat["contact_phone"] = ""
        flat["contact_title"] = ""

    # Place of performance
    pop = opp.get("placeOfPerformance", {}) or {}
    street_addr = pop.get("streetAddress", "")
    if isinstance(street_addr, dict):
        street_addr = street_addr.get("streetAddress", "")
    flat["pop_street"] = street_addr
    flat["pop_city"] = pop.get("city", {}).get("name", "") if isinstance(pop.get("city"), dict) else pop.get("city", "")
    flat["pop_state"] = pop.get("state", {}).get("code", "") if isinstance(pop.get("state"), dict) else pop.get("state", "")
    flat["pop_zip"] = pop.get("zip", "")
    flat["pop_country"] = pop.get("country", {}).get("name", "") if isinstance(pop.get("country"), dict) else pop.get("country", "")

    # Award info
    award = opp.get("award", {}) or {}
    flat["award_number"] = award.get("number", "")
    flat["award_amount"] = award.get("amount", "")
    flat["award_date"] = award.get("date", "")
    awardee = award.get("awardee", {}) or {}
    flat["award_awardee_name"] = awardee.get("name", "")
    awardee_loc = awardee.get("location", {}) or {}
    if awardee_loc:
        loc_parts = [
            awardee_loc.get("city", {}).get("name", "") if isinstance(awardee_loc.get("city"), dict) else awardee_loc.get("city", ""),
            awardee_loc.get("state", {}).get("code", "") if isinstance(awardee_loc.get("state"), dict) else awardee_loc.get("state", ""),
        ]
        flat["award_awardee_location"] = ", ".join(p for p in loc_parts if p)
    else:
        flat["award_awardee_location"] = ""

    # Description URL
    flat["description_url"] = opp.get("description", {}).get("url", "") if isinstance(opp.get("description"), dict) else ""

    # Resource links (join multiple)
    links = opp.get("resourceLinks", []) or []
    flat["resourceLinks"] = "; ".join(links) if links else ""

    return flat


def export_to_csv(
    opportunities: list[dict],
    output_path: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> str:
    """
    Export opportunities to CSV file.

    Args:
        opportunities: List of opportunity dictionaries
        output_path: Custom output path (auto-generated if None)
        date_from: Start date for filename
        date_to: End date for filename

    Returns:
        Path to the created CSV file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if date_from and date_to:
            date_range = f"{date_from.strftime('%Y%m%d')}_to_{date_to.strftime('%Y%m%d')}"
            output_path = f"sam_opportunities_{date_range}_{timestamp}.csv"
        else:
            output_path = f"sam_opportunities_{timestamp}.csv"

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()

        for opp in opportunities:
            flat = flatten_opportunity(opp)
            writer.writerow(flat)

    return output_path


def export_to_csv_string(opportunities: list[dict]) -> str:
    """
    Export opportunities to CSV string (in-memory).

    Args:
        opportunities: List of opportunity dictionaries

    Returns:
        CSV content as a string
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS, extrasaction="ignore")
    writer.writeheader()

    for opp in opportunities:
        flat = flatten_opportunity(opp)
        writer.writerow(flat)

    return output.getvalue()
