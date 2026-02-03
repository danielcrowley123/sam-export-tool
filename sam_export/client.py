"""SAM.gov API client for searching contract opportunities."""

import os
import time
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv


class SamGovClient:
    """Client for interacting with SAM.gov Opportunities API."""

    BASE_URL = "https://api.sam.gov/opportunities/v2/search"
    MAX_RECORDS_PER_REQUEST = 1000
    MAX_DATE_RANGE_DAYS = 365

    def __init__(self, api_key: Optional[str] = None):
        """Initialize client with API key from parameter or environment."""
        load_dotenv()
        self.api_key = api_key or os.getenv("SAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SAM_API_KEY not found. Set it in .env file or pass to constructor."
            )

    def search_opportunities(
        self,
        naics_code: Optional[str] = None,
        posted_from: Optional[datetime] = None,
        posted_to: Optional[datetime] = None,
        limit: Optional[int] = 100,
    ) -> list[dict]:
        """
        Search for opportunities, optionally filtered by NAICS code prefix.

        Args:
            naics_code: NAICS code or prefix to filter (e.g., "212" for mining,
                       "541330" for engineering). If None, returns all opportunities.
            posted_from: Start date for posted date filter
            posted_to: End date for posted date filter
            limit: Maximum number of records to fetch (None for all)

        Returns:
            List of opportunity dictionaries
        """
        if posted_to is None:
            posted_to = datetime.now()
        if posted_from is None:
            posted_from = posted_to - timedelta(days=30)

        # Validate date range
        if (posted_to - posted_from).days > self.MAX_DATE_RANGE_DAYS:
            raise ValueError(
                f"Date range cannot exceed {self.MAX_DATE_RANGE_DAYS} days"
            )

        all_opportunities = []
        offset = 0

        # API ncode only works with full 6-digit codes
        # For prefixes, we fetch all and filter client-side
        use_api_filter = naics_code and len(naics_code) == 6

        while True: to:                                                                                                  
          max_pages = 5  # Limit to 5 API calls to prevent timeout                                                        
          page = 0                                                                                                        
          while page < max_pages:                                                                                         
              page += 1                                                                                                   
              params = {
                "api_key": self.api_key,
                "postedFrom": posted_from.strftime("%m/%d/%Y"),
                "postedTo": posted_to.strftime("%m/%d/%Y"),
                "limit": self.MAX_RECORDS_PER_REQUEST,
                "offset": offset,
            }

            # Only use ncode param for full 6-digit codes
            if use_api_filter:
                params["ncode"] = naics_code

            response = self._make_request(params)
            if response is None:
                break

            opportunities = response.get("opportunitiesData", [])
            if not opportunities:
                break

            # Filter by NAICS prefix if using client-side filtering
            if naics_code and not use_api_filter:
                opportunities = [
                    opp for opp in opportunities
                    if str(opp.get("naicsCode", "")).startswith(naics_code)
                ]

            all_opportunities.extend(opportunities)
            print(f"  Fetched {len(all_opportunities)} matching opportunities...")

            # Check if we've reached the user-specified limit
            if limit and len(all_opportunities) >= limit:
                all_opportunities = all_opportunities[:limit]
                break

            # Check if there are more records
            total_records = response.get("totalRecords", 0)
            fetched_total = offset + self.MAX_RECORDS_PER_REQUEST
            if fetched_total >= total_records:
                break

            offset += self.MAX_RECORDS_PER_REQUEST
            time.sleep(0.5)  # Rate limiting

        return all_opportunities

    def _make_request(
        self, params: dict, max_retries: int = 3, retry_delay: float = 2.0
    ) -> Optional[dict]:
        """Make API request with retry logic."""
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self.BASE_URL, params=params, timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Rate limited
                    print(f"  Rate limited, waiting {retry_delay * 2}s...")
                    time.sleep(retry_delay * 2)
                elif response.status_code == 403:
                    raise ValueError("Invalid API key or access denied") from e
                else:
                    print(f"  HTTP error {response.status_code}, retrying...")
                    time.sleep(retry_delay)
            except requests.exceptions.RequestException as e:
                print(f"  Request failed: {e}, retrying...")
                time.sleep(retry_delay)

            if attempt == max_retries - 1:
                print(f"  Failed after {max_retries} attempts")
                return None

        return None
