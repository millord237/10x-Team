#!/usr/bin/env python3
"""
LinkedIn Sales Navigator API Integration for 100X Outreach System

Provides REST API access to LinkedIn Sales Navigator for lead and account search.
Falls back gracefully when no API token is configured.

Requires: LINKEDIN_SALES_NAV_TOKEN in .env
API Docs: https://learn.microsoft.com/en-us/linkedin/sales/

Developed by 10x.in
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import local modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rate_limiter import RateLimiter
except ImportError:
    RateLimiter = None

# LinkedIn Sales Navigator API base URL
API_BASE = "https://api.linkedin.com/sales-api"
API_VERSION = "2024-01"


@dataclass
class SalesNavLead:
    """A lead from Sales Navigator search"""
    lead_id: str
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    title: str = ""
    company_name: str = ""
    company_id: str = ""
    location: str = ""
    industry: str = ""
    linkedin_url: str = ""
    profile_picture_url: str = ""
    connection_degree: int = 0
    shared_connections: int = 0
    last_activity: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.full_name and (self.first_name or self.last_name):
            self.full_name = f"{self.first_name} {self.last_name}".strip()


@dataclass
class SalesNavAccount:
    """A company/account from Sales Navigator search"""
    account_id: str
    name: str = ""
    industry: str = ""
    company_size: str = ""
    headquarters: str = ""
    website: str = ""
    description: str = ""
    employee_count: int = 0
    linkedin_url: str = ""


class LinkedInSalesNavigator:
    """
    LinkedIn Sales Navigator REST API client.

    Provides search and lookup capabilities for leads and accounts.
    Requires a valid Sales Navigator API token (LINKEDIN_SALES_NAV_TOKEN).
    """

    def __init__(self, token: str = None):
        self.token = token or os.getenv("LINKEDIN_SALES_NAV_TOKEN", "")
        self.rate_limiter = RateLimiter() if RateLimiter else None
        self._session = None

    @property
    def is_configured(self) -> bool:
        """Check if API token is available and not a placeholder"""
        return bool(self.token) and self.token != "your_linkedin_sales_nav_token_here"

    def _get_session(self):
        """Lazy-init requests session"""
        if self._session is None:
            try:
                import requests
            except ImportError:
                raise ImportError(
                    "The 'requests' package is required. Install with: pip install requests"
                )
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "LinkedIn-Version": API_VERSION,
            })
        return self._session

    def _check_rate_limit(self, action: str) -> bool:
        """Check rate limits before making API call"""
        if self.rate_limiter:
            can_proceed, reason, wait_seconds = self.rate_limiter.can_proceed(
                "api", "linkedin_api", action
            )
            if not can_proceed:
                return False
        return True

    def _record_action(self, action: str, target: str, success: bool):
        """Record action for rate limiting"""
        if self.rate_limiter:
            self.rate_limiter.record_action(
                "api", "linkedin_api", action, target, success
            )

    def _request(self, method: str, endpoint: str, params: Dict = None,
                 data: Dict = None) -> Dict:
        """Make an authenticated API request"""
        if not self.is_configured:
            return {
                "success": False,
                "error": "LinkedIn Sales Navigator token not configured. "
                         "Set LINKEDIN_SALES_NAV_TOKEN in .env"
            }

        session = self._get_session()
        url = f"{API_BASE}/{endpoint}"

        try:
            response = session.request(
                method, url, params=params, json=data, timeout=30
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                return {
                    "success": False,
                    "error": f"Rate limited. Retry after {retry_after}s",
                    "retry_after": retry_after,
                }

            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid or expired Sales Navigator token. "
                             "Update LINKEDIN_SALES_NAV_TOKEN in .env",
                }

            response.raise_for_status()
            return {"success": True, "data": response.json()}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_leads(self, query: str, filters: Dict = None,
                     start: int = 0, count: int = 25) -> Dict:
        """
        Search for leads (people) in Sales Navigator.

        Args:
            query: Keyword search string
            filters: Optional filters dict with keys:
                - title: Job title filter
                - company: Company name filter
                - location: Geographic location
                - industry: Industry filter
                - seniority: Seniority level (e.g., "VP", "Director", "CXO")
                - company_size: Company headcount range
            start: Pagination offset
            count: Results per page (max 25)

        Returns:
            Dict with success status and list of SalesNavLead results
        """
        if not self._check_rate_limit("search_leads"):
            return {"success": False, "error": "Rate limit reached for API searches"}

        params = {
            "q": "search",
            "query": query,
            "start": start,
            "count": min(count, 25),
        }

        if filters:
            if filters.get("title"):
                params["titleFilter"] = filters["title"]
            if filters.get("company"):
                params["companyFilter"] = filters["company"]
            if filters.get("location"):
                params["geoFilter"] = filters["location"]
            if filters.get("industry"):
                params["industryFilter"] = filters["industry"]
            if filters.get("seniority"):
                params["seniorityFilter"] = filters["seniority"]
            if filters.get("company_size"):
                params["companySizeFilter"] = filters["company_size"]

        result = self._request("GET", "salesLeadSearches", params=params)
        self._record_action("search_leads", query, result.get("success", False))

        if result.get("success") and "data" in result:
            leads = self._parse_lead_results(result["data"])
            result["leads"] = leads
            result["total"] = result["data"].get("paging", {}).get("total", len(leads))

        return result

    def get_lead_profile(self, lead_id: str) -> Dict:
        """
        Get detailed lead profile by Sales Navigator lead ID.

        Args:
            lead_id: Sales Navigator lead identifier

        Returns:
            Dict with success status and SalesNavLead data
        """
        if not self._check_rate_limit("get_lead"):
            return {"success": False, "error": "Rate limit reached for lead lookups"}

        result = self._request("GET", f"salesLeads/{lead_id}")
        self._record_action("get_lead", lead_id, result.get("success", False))

        if result.get("success") and "data" in result:
            lead = self._parse_single_lead(result["data"])
            result["lead"] = lead

        return result

    def search_accounts(self, query: str, filters: Dict = None,
                        start: int = 0, count: int = 25) -> Dict:
        """
        Search for accounts (companies) in Sales Navigator.

        Args:
            query: Company name or keyword
            filters: Optional filters dict with keys:
                - industry: Industry filter
                - company_size: Employee count range
                - location: Headquarters location
                - revenue: Revenue range
            start: Pagination offset
            count: Results per page (max 25)

        Returns:
            Dict with success status and list of SalesNavAccount results
        """
        if not self._check_rate_limit("search_accounts"):
            return {"success": False, "error": "Rate limit reached for account searches"}

        params = {
            "q": "search",
            "query": query,
            "start": start,
            "count": min(count, 25),
        }

        if filters:
            if filters.get("industry"):
                params["industryFilter"] = filters["industry"]
            if filters.get("company_size"):
                params["companySizeFilter"] = filters["company_size"]
            if filters.get("location"):
                params["geoFilter"] = filters["location"]

        result = self._request("GET", "salesAccountSearches", params=params)
        self._record_action("search_accounts", query, result.get("success", False))

        if result.get("success") and "data" in result:
            accounts = self._parse_account_results(result["data"])
            result["accounts"] = accounts
            result["total"] = result["data"].get("paging", {}).get("total", len(accounts))

        return result

    def get_account(self, account_id: str) -> Dict:
        """
        Get detailed account info by Sales Navigator account ID.

        Args:
            account_id: Sales Navigator account identifier

        Returns:
            Dict with success status and SalesNavAccount data
        """
        if not self._check_rate_limit("get_account"):
            return {"success": False, "error": "Rate limit reached for account lookups"}

        result = self._request("GET", f"salesAccounts/{account_id}")
        self._record_action("get_account", account_id, result.get("success", False))

        if result.get("success") and "data" in result:
            account = self._parse_single_account(result["data"])
            result["account"] = account

        return result

    def get_saved_leads(self, start: int = 0, count: int = 25) -> Dict:
        """
        Get list of saved leads from Sales Navigator.

        Args:
            start: Pagination offset
            count: Results per page

        Returns:
            Dict with success status and list of saved leads
        """
        if not self._check_rate_limit("get_saved_leads"):
            return {"success": False, "error": "Rate limit reached"}

        params = {"start": start, "count": min(count, 25)}
        result = self._request("GET", "savedLeads", params=params)
        self._record_action("get_saved_leads", "saved", result.get("success", False))

        if result.get("success") and "data" in result:
            leads = self._parse_lead_results(result["data"])
            result["leads"] = leads

        return result

    def save_lead(self, lead_id: str) -> Dict:
        """
        Save a lead in Sales Navigator.

        Args:
            lead_id: Sales Navigator lead identifier

        Returns:
            Dict with success status
        """
        if not self._check_rate_limit("save_lead"):
            return {"success": False, "error": "Rate limit reached"}

        result = self._request("POST", "savedLeads", data={"leadId": lead_id})
        self._record_action("save_lead", lead_id, result.get("success", False))
        return result

    # --- Result Parsing ---

    def _parse_lead_results(self, data: Dict) -> List[SalesNavLead]:
        """Parse API response into SalesNavLead objects"""
        leads = []
        for element in data.get("elements", []):
            leads.append(self._parse_single_lead(element))
        return leads

    def _parse_single_lead(self, element: Dict) -> SalesNavLead:
        """Parse a single lead element"""
        return SalesNavLead(
            lead_id=str(element.get("id", "")),
            first_name=element.get("firstName", ""),
            last_name=element.get("lastName", ""),
            full_name=element.get("fullName", ""),
            title=element.get("currentPositions", [{}])[0].get("title", "")
                if element.get("currentPositions") else element.get("title", ""),
            company_name=element.get("currentPositions", [{}])[0].get("companyName", "")
                if element.get("currentPositions") else element.get("company", ""),
            company_id=str(element.get("currentPositions", [{}])[0].get("companyId", ""))
                if element.get("currentPositions") else "",
            location=element.get("geoRegion", ""),
            industry=element.get("industry", ""),
            linkedin_url=element.get("linkedInUrl", ""),
            profile_picture_url=element.get("profilePictureDisplayImage", ""),
            connection_degree=element.get("connectionDegree", 0),
            shared_connections=element.get("sharedConnectionsCount", 0),
        )

    def _parse_account_results(self, data: Dict) -> List[SalesNavAccount]:
        """Parse API response into SalesNavAccount objects"""
        accounts = []
        for element in data.get("elements", []):
            accounts.append(self._parse_single_account(element))
        return accounts

    def _parse_single_account(self, element: Dict) -> SalesNavAccount:
        """Parse a single account element"""
        return SalesNavAccount(
            account_id=str(element.get("id", "")),
            name=element.get("name", ""),
            industry=element.get("industry", ""),
            company_size=element.get("companySize", ""),
            headquarters=element.get("headquarters", ""),
            website=element.get("website", ""),
            description=element.get("description", ""),
            employee_count=element.get("employeeCount", 0),
            linkedin_url=element.get("linkedInUrl", ""),
        )

    def leads_to_discovered_persons(self, leads: List[SalesNavLead]) -> List[Dict]:
        """
        Convert SalesNavLead list to DiscoveredPerson-compatible dicts.
        Used to feed results into the discovery engine.
        """
        persons = []
        for lead in leads:
            persons.append({
                "name": lead.full_name,
                "title": lead.title,
                "company": lead.company_name,
                "location": lead.location,
                "linkedin_url": lead.linkedin_url,
                "bio": "",
                "tags": ["sales_navigator"] + lead.tags,
            })
        return persons


def main():
    """CLI interface for LinkedIn Sales Navigator"""
    import argparse

    parser = argparse.ArgumentParser(
        description="LinkedIn Sales Navigator API CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Search leads
    search_parser = subparsers.add_parser("search", help="Search for leads")
    search_parser.add_argument("--query", required=True, help="Search keywords")
    search_parser.add_argument("--title", help="Job title filter")
    search_parser.add_argument("--company", help="Company filter")
    search_parser.add_argument("--location", help="Location filter")
    search_parser.add_argument("--industry", help="Industry filter")
    search_parser.add_argument("--seniority", help="Seniority level")
    search_parser.add_argument("--count", type=int, default=10, help="Max results")

    # Get lead
    lead_parser = subparsers.add_parser("lead", help="Get lead profile")
    lead_parser.add_argument("--id", required=True, help="Lead ID")

    # Search accounts
    acct_parser = subparsers.add_parser("accounts", help="Search accounts")
    acct_parser.add_argument("--query", required=True, help="Company search")
    acct_parser.add_argument("--industry", help="Industry filter")
    acct_parser.add_argument("--location", help="Location filter")
    acct_parser.add_argument("--count", type=int, default=10, help="Max results")

    # Get account
    acct_get = subparsers.add_parser("account", help="Get account details")
    acct_get.add_argument("--id", required=True, help="Account ID")

    # Saved leads
    subparsers.add_parser("saved", help="List saved leads")

    # Save lead
    save_parser = subparsers.add_parser("save", help="Save a lead")
    save_parser.add_argument("--id", required=True, help="Lead ID to save")

    # Status
    subparsers.add_parser("status", help="Check API configuration status")

    args = parser.parse_args()
    client = LinkedInSalesNavigator()

    if args.command == "status":
        if client.is_configured:
            print("LinkedIn Sales Navigator API: CONFIGURED")
            print(f"Token: {client.token[:8]}...{client.token[-4:]}")
        else:
            print("LinkedIn Sales Navigator API: NOT CONFIGURED")
            print("Set LINKEDIN_SALES_NAV_TOKEN in .env")
        return

    if not client.is_configured:
        print("Error: LINKEDIN_SALES_NAV_TOKEN not set in .env")
        print("Get your token from https://developer.linkedin.com/")
        sys.exit(1)

    if args.command == "search":
        filters = {}
        if args.title:
            filters["title"] = args.title
        if args.company:
            filters["company"] = args.company
        if args.location:
            filters["location"] = args.location
        if args.industry:
            filters["industry"] = args.industry
        if args.seniority:
            filters["seniority"] = args.seniority

        result = client.search_leads(args.query, filters=filters, count=args.count)
        if result.get("success"):
            leads = result.get("leads", [])
            print(f"Found {result.get('total', len(leads))} leads:")
            for lead in leads:
                print(f"  [{lead.lead_id}] {lead.full_name} - {lead.title} at {lead.company_name}")
                if lead.location:
                    print(f"       Location: {lead.location}")
        else:
            print(f"Error: {result.get('error')}")

    elif args.command == "lead":
        result = client.get_lead_profile(args.id)
        if result.get("success"):
            lead = result["lead"]
            print(json.dumps(asdict(lead), indent=2))
        else:
            print(f"Error: {result.get('error')}")

    elif args.command == "accounts":
        filters = {}
        if args.industry:
            filters["industry"] = args.industry
        if args.location:
            filters["location"] = args.location

        result = client.search_accounts(args.query, filters=filters, count=args.count)
        if result.get("success"):
            accounts = result.get("accounts", [])
            print(f"Found {result.get('total', len(accounts))} accounts:")
            for acct in accounts:
                print(f"  [{acct.account_id}] {acct.name} - {acct.industry}")
                if acct.headquarters:
                    print(f"       HQ: {acct.headquarters}")
        else:
            print(f"Error: {result.get('error')}")

    elif args.command == "account":
        result = client.get_account(args.id)
        if result.get("success"):
            print(json.dumps(asdict(result["account"]), indent=2))
        else:
            print(f"Error: {result.get('error')}")

    elif args.command == "saved":
        result = client.get_saved_leads()
        if result.get("success"):
            leads = result.get("leads", [])
            print(f"Saved leads ({len(leads)}):")
            for lead in leads:
                print(f"  [{lead.lead_id}] {lead.full_name} - {lead.title}")
        else:
            print(f"Error: {result.get('error')}")

    elif args.command == "save":
        result = client.save_lead(args.id)
        if result.get("success"):
            print(f"Lead {args.id} saved successfully")
        else:
            print(f"Error: {result.get('error')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
