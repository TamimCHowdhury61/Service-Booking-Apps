#!/usr/bin/env python3
"""
Admin Dashboard Widget - Duplicate Statistics Display

Shows duplicate counts and cancellation status in the admin dashboard.
Can be embedded into the main app or used as standalone monitoring tool.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from duplicate_analysis_report import DuplicateAnalysisReport


class DuplicateStatsWidget:
    """Widget for displaying duplicate statistics in admin dashboard"""

    def __init__(self):
        self.analyzer = DuplicateAnalysisReport()
        self.last_report = None
        self.last_update = None

    def get_duplicate_stats(self, refresh: bool = False) -> Dict[str, Any]:
        """
        Get current duplicate statistics
        
        Args:
            refresh: If True, re-analyze database. If False, use cached results.
        
        Returns:
            Dictionary with duplicate statistics
        """
        if refresh or self.last_report is None:
            self.last_report = self.analyzer.analyze_duplicates()
            self.last_update = datetime.now()

        return {
            "total_duplicates": self.last_report["total_duplicates_found"],
            "active_duplicates": self.last_report["active_duplicates"],
            "cancelled_duplicates": self.last_report["cancelled_duplicates"],
            "cross_database": self.last_report["cross_database_duplicates"],
            "within_database": self.last_report["within_database_duplicates"],
            "total_providers": self.last_report["total_providers"],
            "duplicate_ratio": (
                self.last_report["total_duplicates_found"] / self.last_report["total_providers"] * 100
                if self.last_report["total_providers"] > 0
                else 0
            ),
            "last_updated": self.last_update.isoformat() if self.last_update else None,
        }

    def get_active_duplicates_list(self) -> list:
        """Get list of active duplicates that need attention"""
        if self.last_report is None:
            self.get_duplicate_stats(refresh=True)
        
        if self.last_report is None:
            return []
        return self.last_report.get("active_details", [])

    def get_cancelled_duplicates_list(self) -> list:
        """Get list of cancelled duplicates"""
        if self.last_report is None:
            self.get_duplicate_stats(refresh=True)
        
        if self.last_report is None:
            return []
        return self.last_report.get("cancelled_details", [])

    def print_dashboard_summary(self):
        """Print a simple dashboard summary"""
        stats = self.get_duplicate_stats()

        print("\n" + "=" * 60)
        print("ADMIN DASHBOARD - DUPLICATE STATISTICS")
        print("=" * 60)
        print(f"Last Updated: {stats['last_updated']}")
        print("-" * 60)

        # Color-coded status boxes
        print(f"\n📊 OVERVIEW")
        print(f"  Total Providers:        {stats['total_providers']}")
        print(f"  Total Duplicates:       {stats['total_duplicates']}")
        print(f"  Duplicate Ratio:        {stats['duplicate_ratio']:.2f}%")

        print(f"\n⚠️  ACTIVE (NEED ATTENTION)")
        print(f"  Active Duplicates:      {stats['active_duplicates']}")
        print(f"  Cross-Database:         {stats['cross_database']}")
        print(f"  Within-Database:        {stats['within_database']}")

        print(f"\n✓ RESOLVED")
        print(f"  Cancelled Duplicates:   {stats['cancelled_duplicates']}")

        # Status indicator
        if stats["active_duplicates"] == 0:
            status = "🟢 HEALTHY"
        elif stats["active_duplicates"] < 5:
            status = "🟡 WARNING"
        else:
            status = "🔴 CRITICAL"

        print(f"\n{status} - Database Quality")

        print("\n" + "=" * 60)

        # Show sample active duplicates
        if stats["active_duplicates"] > 0:
            print("\n📋 SAMPLE ACTIVE DUPLICATES (Top 5):")
            active_dups = self.get_active_duplicates_list()[:5]
            for idx, dup in enumerate(active_dups, 1):
                if dup["type"] == "cross-database":
                    print(
                        f"\n{idx}. {dup['primary']['name']} ↔ {dup['secondary']['name']}"
                    )
                    print(f"   Similarity: {dup['similarity']:.1%}")
                else:
                    print(
                        f"\n{idx}. {dup['provider1']['name']} ↔ {dup['provider2']['name']}"
                    )
                    print(f"   Similarity: {dup['similarity']:.1%}")

        print("\n" + "=" * 60)


def print_quick_stats():
    """Print quick statistics without full analysis"""
    print("\n" + "=" * 60)
    print("QUICK DUPLICATE CHECK")
    print("=" * 60)

    widget = DuplicateStatsWidget()
    stats = widget.get_duplicate_stats(refresh=True)

    print(f"\n📈 Results:")
    print(f"   Total Providers: {stats['total_providers']}")
    print(f"   Total Duplicates: {stats['total_duplicates']}")
    print(f"   Active: {stats['active_duplicates']} ⚠️")
    print(f"   Cancelled: {stats['cancelled_duplicates']} ✓")
    print(f"\n   Quality Score: {100 - stats['duplicate_ratio']:.2f}%")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    widget = DuplicateStatsWidget()
    widget.print_dashboard_summary()
