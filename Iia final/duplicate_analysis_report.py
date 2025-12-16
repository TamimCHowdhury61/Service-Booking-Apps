#!/usr/bin/env python3
"""
Duplicate Detection and Analysis Report

Analyzes both Primary (Companies) and Secondary (Employees) databases
to find and report duplicate providers, their status, and cancellation info.
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from distributed_database_manager import DistributedDatabaseManager
from string_similarity_matcher import StringSimplicityMatcher


class DuplicateAnalysisReport:
    """Generate comprehensive duplicate analysis and cancellation report"""

    def __init__(self):
        self.db_manager = DistributedDatabaseManager()
        self.duplicates = []
        self.cancelled_duplicates = []
        self.active_duplicates = []
        self.total_providers = 0

    def analyze_duplicates(self) -> Dict[str, Any]:
        """
        Analyze database for duplicates and generate comprehensive report
        """
        print("\n" + "=" * 80)
        print("DUPLICATE DETECTION AND ANALYSIS REPORT")
        print("=" * 80)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        # Get data from both databases
        print("\n📊 Scanning databases...")

        # Get all companies from primary database
        companies = self._get_all_companies()
        employees = self._get_all_employees()

        self.total_providers = len(companies) + len(employees)
        print(f"   - Primary DB (Companies): {len(companies)} records")
        print(f"   - Secondary DB (Employees): {len(employees)} records")
        print(f"   - Total providers: {self.total_providers}")

        # Find duplicates across databases
        print("\n🔍 Searching for duplicates across databases...")
        self._find_cross_database_duplicates(companies, employees)

        # Find duplicates within each database
        print("\n🔍 Searching for duplicates within each database...")
        self._find_within_database_duplicates(companies, "Primary")
        self._find_within_database_duplicates(employees, "Secondary")

        # Separate cancelled and active duplicates
        print("\n📋 Analyzing duplicate status...")
        self._categorize_duplicates()

        # Generate report
        report = self._generate_report()

        return report

    def _get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies from primary database"""
        try:
            query = """
            SELECT company_id, company_name, business_type, rating, 
                   total_reviews, phone, email
            FROM COMPANIES
            ORDER BY company_name ASC
            """
            results = self.db_manager.execute_query(query, None, 'primary')
            return results if results else []
        except Exception as e:
            print(f"   ⚠️ Error getting companies: {e}")
            return []

    def _get_all_employees(self) -> List[Dict[str, Any]]:
        """Get all employees from secondary database"""
        try:
            query = """
            SELECT e.employee_id, u.name, e.job_type, e.rating, 
                   e.total_completed_orders, u.phone, u.email, 
                   e.availability_status
            FROM EMPLOYEE e
            JOIN USER u ON e.user_id = u.user_id
            ORDER BY u.name ASC
            """
            results = self.db_manager.execute_query(query, None, 'secondary')
            return results if results else []
        except Exception as e:
            print(f"   ⚠️ Error getting employees: {e}")
            return []

    def _find_cross_database_duplicates(
        self, companies: List[Dict], employees: List[Dict]
    ):
        """Find duplicates between Primary and Secondary databases"""
        threshold = 0.80

        for comp_idx, company in enumerate(companies):
            comp_name = company.get("company_name", "")

            for emp_idx, employee in enumerate(employees):
                emp_name = employee.get("name", "")

                similarity = StringSimplicityMatcher.calculate_similarity(
                    comp_name, emp_name
                )

                if similarity >= threshold:
                    self.duplicates.append(
                        {
                            "type": "cross-database",
                            "primary": {
                                "id": company.get("company_id"),
                                "name": comp_name,
                                "source": "Primary (Company)",
                                "rating": company.get("rating", 0),
                            },
                            "secondary": {
                                "id": employee.get("employee_id"),
                                "name": emp_name,
                                "source": "Secondary (Employee)",
                                "rating": employee.get("rating", 0),
                                "availability_status": employee.get("availability_status", "Unknown"),
                            },
                            "similarity": similarity,
                        }
                    )

    def _find_within_database_duplicates(
        self, providers: List[Dict], source: str
    ):
        """Find duplicates within the same database"""
        threshold = 0.90  # Higher threshold for within-database duplicates

        for i in range(len(providers)):
            for j in range(i + 1, len(providers)):
                name_i = providers[i].get("company_name") or providers[i].get("name", "")
                name_j = providers[j].get("company_name") or providers[j].get("name", "")

                similarity = StringSimplicityMatcher.calculate_similarity(name_i, name_j)

                if similarity >= threshold:
                    self.duplicates.append(
                        {
                            "type": f"within-{source.lower()}",
                            "provider1": {
                                "id": providers[i].get("company_id") or providers[i].get("employee_id"),
                                "name": name_i,
                                "source": source,
                                "rating": providers[i].get("rating", 0),
                                "availability_status": providers[i].get("availability_status", "Unknown"),
                            },
                            "provider2": {
                                "id": providers[j].get("company_id") or providers[j].get("employee_id"),
                                "name": name_j,
                                "source": source,
                                "rating": providers[j].get("rating", 0),
                                "availability_status": providers[j].get("availability_status", "Unknown"),
                            },
                            "similarity": similarity,
                        }
                    )

    def _categorize_duplicates(self):
        """Separate duplicates into cancelled and active"""
        # For this analysis, we'll treat unavailable employees as "cancelled" status
        
        for duplicate in self.duplicates:
            is_cancelled = False

            # Check cancellation status
            if duplicate["type"] == "cross-database":
                secondary_available = duplicate["secondary"].get("availability_status", "").lower() == "available"
                
                # Consider it "cancelled" if employee is unavailable
                if not secondary_available:
                    is_cancelled = True

            else:
                # For within-database duplicates, check employee availability
                prov1_available = True
                prov2_available = True
                
                if "availability_status" in duplicate["provider1"]:
                    prov1_available = duplicate["provider1"].get("availability_status", "").lower() == "available"
                if "availability_status" in duplicate["provider2"]:
                    prov2_available = duplicate["provider2"].get("availability_status", "").lower() == "available"

                if not prov1_available or not prov2_available:
                    is_cancelled = True

            if is_cancelled:
                self.cancelled_duplicates.append(duplicate)
            else:
                self.active_duplicates.append(duplicate)

    def _generate_report(self) -> Dict[str, Any]:
        """Generate final report with all statistics"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_providers": self.total_providers,
            "total_duplicates_found": len(self.duplicates),
            "cancelled_duplicates": len(self.cancelled_duplicates),
            "active_duplicates": len(self.active_duplicates),
            "cross_database_duplicates": len(
                [d for d in self.duplicates if d["type"] == "cross-database"]
            ),
            "within_database_duplicates": len(
                [d for d in self.duplicates if d["type"].startswith("within-")]
            ),
            "duplicates": self.duplicates,
            "cancelled_details": self.cancelled_duplicates,
            "active_details": self.active_duplicates,
        }

        return report

    def print_report(self, report: Dict[str, Any]):
        """Print formatted report to console"""
        print("\n" + "=" * 80)
        print("📈 SUMMARY")
        print("=" * 80)
        print(f"Total providers scanned: {report['total_providers']}")
        print(f"Total duplicates found: {report['total_duplicates_found']}")
        print(f"  ├─ Active duplicates: {report['active_duplicates']} ⚠️")
        print(f"  └─ Cancelled duplicates: {report['cancelled_duplicates']} ✓")
        print(f"\nDuplicate breakdown:")
        print(f"  ├─ Cross-database duplicates: {report['cross_database_duplicates']}")
        print(f"  └─ Within-database duplicates: {report['within_database_duplicates']}")

        # Print active duplicates (need action)
        if report["active_duplicates"] > 0:
            print("\n" + "=" * 80)
            print(f"⚠️  ACTIVE DUPLICATES ({report['active_duplicates']} found)")
            print("=" * 80)
            print("These duplicates are ACTIVE and may need attention:\n")

            for idx, dup in enumerate(report["active_details"], 1):
                print(f"{idx}. {dup['type'].replace('-', ' ').upper()}")

                if dup["type"] == "cross-database":
                    print(
                        f"   Primary:   {dup['primary']['name']} (ID: {dup['primary']['id']}, Rating: {dup['primary']['rating']})"
                    )
                    print(
                        f"   Secondary: {dup['secondary']['name']} (ID: {dup['secondary']['id']}, Rating: {dup['secondary']['rating']})"
                    )
                else:
                    print(
                        f"   Provider 1: {dup['provider1']['name']} (ID: {dup['provider1']['id']}, Rating: {dup['provider1']['rating']})"
                    )
                    print(
                        f"   Provider 2: {dup['provider2']['name']} (ID: {dup['provider2']['id']}, Rating: {dup['provider2']['rating']})"
                    )

                print(f"   Similarity: {dup['similarity']:.1%}\n")

        # Print cancelled duplicates (for reference)
        if report["cancelled_duplicates"] > 0:
            print("\n" + "=" * 80)
            print(f"✓ CANCELLED DUPLICATES ({report['cancelled_duplicates']} found)")
            print("=" * 80)
            print("These duplicates are CANCELLED (no action needed):\n")

            for idx, dup in enumerate(report["cancelled_details"], 1):
                print(f"{idx}. {dup['type'].replace('-', ' ').upper()}")

                if dup["type"] == "cross-database":
                    prim_status = dup["primary"].get("status", "unknown")
                    sec_status = dup["secondary"].get("status", "unknown")
                    print(f"   Primary:   {dup['primary']['name']} [Status: {prim_status}]")
                    print(f"   Secondary: {dup['secondary']['name']} [Status: {sec_status}]")
                else:
                    p1_status = dup["provider1"].get("status", "unknown")
                    p2_status = dup["provider2"].get("status", "unknown")
                    print(f"   Provider 1: {dup['provider1']['name']} [Status: {p1_status}]")
                    print(f"   Provider 2: {dup['provider2']['name']} [Status: {p2_status}]")

                print(f"   Similarity: {dup['similarity']:.1%}\n")

        # Print summary statistics
        print("\n" + "=" * 80)
        print("📊 DETAILED STATISTICS")
        print("=" * 80)
        duplicate_ratio = (
            (report["total_duplicates_found"] / report["total_providers"] * 100)
            if report["total_providers"] > 0
            else 0
        )
        print(f"Duplicate ratio: {duplicate_ratio:.2f}%")
        print(f"Data quality score: {max(0, 100 - duplicate_ratio):.2f}%")

        if report["total_duplicates_found"] == 0:
            print("\n✅ No duplicates found! Database is clean.")
        else:
            print(
                f"\n⚠️ Found {report['total_duplicates_found']} potential duplicates."
            )
            print("Review active duplicates and consider deduplication.")

        print("\n" + "=" * 80)

    def export_report_csv(self, report: Dict[str, Any], filename: str = "duplicate_report.csv"):
        """Export report to CSV file"""
        import csv

        try:
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(
                    [
                        "Duplicate Type",
                        "Item 1 ID",
                        "Item 1 Name",
                        "Item 1 Source",
                        "Item 1 Status",
                        "Item 2 ID",
                        "Item 2 Name",
                        "Item 2 Source",
                        "Item 2 Status",
                        "Similarity %",
                        "Is Cancelled",
                    ]
                )

                # Data rows
                for dup in report["duplicates"]:
                    is_cancelled = (
                        "Yes"
                        if dup in report["cancelled_details"]
                        else "No"
                    )

                    if dup["type"] == "cross-database":
                        writer.writerow(
                            [
                                dup["type"],
                                dup["primary"]["id"],
                                dup["primary"]["name"],
                                dup["primary"]["source"],
                                dup["primary"]["status"],
                                dup["secondary"]["id"],
                                dup["secondary"]["name"],
                                dup["secondary"]["source"],
                                dup["secondary"]["status"],
                                f"{dup['similarity']:.1%}",
                                is_cancelled,
                            ]
                        )
                    else:
                        writer.writerow(
                            [
                                dup["type"],
                                dup["provider1"]["id"],
                                dup["provider1"]["name"],
                                dup["provider1"]["source"],
                                dup["provider1"]["status"],
                                dup["provider2"]["id"],
                                dup["provider2"]["name"],
                                dup["provider2"]["source"],
                                dup["provider2"]["status"],
                                f"{dup['similarity']:.1%}",
                                is_cancelled,
                            ]
                        )

            print(f"✅ Report exported to: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error exporting report: {e}")
            return False


def main():
    """Main entry point"""
    print("\n🔍 Starting Duplicate Analysis...\n")

    analyzer = DuplicateAnalysisReport()

    try:
        report = analyzer.analyze_duplicates()

        # Print to console
        analyzer.print_report(report)

        # Export to CSV
        csv_filename = f"duplicate_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        analyzer.export_report_csv(report, csv_filename)

        print(
            f"\n💡 Tip: Open the CSV file with Excel or Google Sheets for easier viewing."
        )
        print(
            f"📁 Location: {os.path.abspath(csv_filename)}"
        )

        return report

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
