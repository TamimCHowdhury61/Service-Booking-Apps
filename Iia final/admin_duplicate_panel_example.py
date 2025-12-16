#!/usr/bin/env python3
"""
Example: Integrating Duplicate Stats Widget into Admin Dashboard

This shows how to add duplicate statistics display to your existing
enhanced_distributed_app_primary.py admin interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from admin_duplicate_stats import DuplicateStatsWidget


class AdminDuplicatePanel:
    """Panel widget for displaying duplicate statistics in admin dashboard"""

    def __init__(self, parent_frame):
        """Initialize the duplicate stats panel"""
        self.widget = DuplicateStatsWidget()
        self.parent = parent_frame
        self.last_stats = None
        self.setup_ui()

    def setup_ui(self):
        """Create the UI elements"""
        # Main frame
        main_frame = ttk.LabelFrame(self.parent, text="📊 Duplicate Analysis", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Stats display frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)

        # Create stat boxes
        self.stat_labels = {}

        # Total providers
        self._create_stat_box(stats_frame, "Total Providers", "total_providers", 0, 0)

        # Total duplicates
        self._create_stat_box(stats_frame, "Total Duplicates", "total_duplicates", 0, 1)

        # Active duplicates
        self._create_stat_box(stats_frame, "Active Duplicates ⚠️", "active_duplicates", 1, 0)

        # Cancelled duplicates
        self._create_stat_box(stats_frame, "Cancelled Duplicates ✓", "cancelled_duplicates", 1, 1)

        # Quality score
        quality_frame = ttk.LabelFrame(stats_frame, text="Data Quality", padding=5)
        quality_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.quality_label = tk.Label(quality_frame, text="Score: --", font=("Arial", 14, "bold"))
        self.quality_label.pack(side=tk.LEFT, padx=10)

        self.quality_bar = ttk.Progressbar(
            quality_frame, length=200, mode="determinate", value=0
        )
        self.quality_bar.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        self.refresh_btn = ttk.Button(button_frame, text="🔄 Refresh Stats", command=self.refresh_stats)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.details_btn = ttk.Button(button_frame, text="📋 View Details", command=self.show_details)
        self.details_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = ttk.Button(button_frame, text="📁 Export Report", command=self.export_report)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Status message
        self.status_label = tk.Label(main_frame, text="Ready", fg="green", font=("Arial", 9))
        self.status_label.pack(anchor="w", padx=5, pady=5)

        # Load initial stats
        self.refresh_stats()

    def _create_stat_box(self, parent, label, key, row, col):
        """Helper to create individual stat box"""
        frame = ttk.LabelFrame(parent, text=label, padding=10)
        frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        parent.columnconfigure(col, weight=1)

        self.stat_labels[key] = tk.Label(frame, text="--", font=("Arial", 16, "bold"))
        self.stat_labels[key].pack()

    def refresh_stats(self):
        """Refresh statistics from database"""
        try:
            self.status_label.config(text="⏳ Loading...", fg="orange")
            self.parent.update()

            self.last_stats = self.widget.get_duplicate_stats(refresh=True)

            # Update stat displays
            for key, label_widget in self.stat_labels.items():
                value = self.last_stats.get(key, 0)
                label_widget.config(text=str(value))

            # Update quality score
            quality = 100 - self.last_stats["duplicate_ratio"]
            self.quality_label.config(text=f"Score: {quality:.1f}%")
            self.quality_bar.config(value=quality)

            # Color code quality
            if quality >= 95:
                color = "green"
                status = "✅ Excellent"
            elif quality >= 85:
                color = "blue"
                status = "✅ Good"
            elif quality >= 75:
                color = "orange"
                status = "⚠️ Fair"
            else:
                color = "red"
                status = "🔴 Poor"

            self.quality_label.config(fg=color)
            self.status_label.config(text=f"Status: {status}", fg=color)

        except Exception as e:
            self.status_label.config(
                text=f"❌ Error loading stats: {str(e)[:50]}", fg="red"
            )

    def show_details(self):
        """Show detailed duplicate information"""
        if not self.last_stats:
            messagebox.showinfo("No Data", "No statistics loaded. Click Refresh first.")
            return

        # Create details window
        details_window = tk.Toplevel(self.parent)
        details_window.title("Duplicate Analysis Details")
        details_window.geometry("600x400")

        # Scrollable text widget
        text_widget = tk.Text(details_window, wrap=tk.WORD, font=("Courier", 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Generate report text
        report_text = self._generate_report_text()
        text_widget.insert("1.0", report_text)
        text_widget.config(state="disabled")  # Read-only

        # Close button
        ttk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=5)

    def show_active_duplicates(self):
        """Show list of active duplicates that need attention"""
        active_dups = self.widget.get_active_duplicates_list()

        if not active_dups:
            messagebox.showinfo("Active Duplicates", "No active duplicates found! ✅")
            return

        window = tk.Toplevel(self.parent)
        window.title("Active Duplicates Requiring Attention")
        window.geometry("700x500")

        # Treeview for duplicates
        tree_frame = ttk.Frame(window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("Type", "Provider 1", "Provider 2", "Similarity")
        tree = ttk.Treeview(tree_frame, columns=columns, height=15)
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("Type", anchor=tk.W, width=120)
        tree.column("Provider 1", anchor=tk.W, width=200)
        tree.column("Provider 2", anchor=tk.W, width=200)
        tree.column("Similarity", anchor=tk.CENTER, width=80)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("Type", text="Type", anchor=tk.W)
        tree.heading("Provider 1", text="Provider 1", anchor=tk.W)
        tree.heading("Provider 2", text="Provider 2", anchor=tk.W)
        tree.heading("Similarity", text="Similarity", anchor=tk.CENTER)

        # Add data to tree
        for idx, dup in enumerate(active_dups, 1):
            if dup["type"] == "cross-database":
                prov1 = f"{dup['primary']['name']} (Co)"
                prov2 = f"{dup['secondary']['name']} (Emp)"
            else:
                prov1 = dup["provider1"]["name"]
                prov2 = dup["provider2"]["name"]

            similarity = f"{dup['similarity']:.1%}"
            tree.insert(parent="", index="end", iid=idx, text=str(idx),
                       values=(dup["type"].replace("-", " ").upper(), prov1, prov2, similarity))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.config(yscrollcommand=scrollbar.set)

        # Info label
        info_label = tk.Label(window, text=f"Showing {len(active_dups)} active duplicates",
                             fg="orange", font=("Arial", 9))
        info_label.pack(anchor="w", padx=5)

    def export_report(self):
        """Export full report to CSV"""
        try:
            self.status_label.config(text="⏳ Exporting...", fg="orange")
            self.parent.update()

            from duplicate_analysis_report import DuplicateAnalysisReport
            report = DuplicateAnalysisReport()
            analysis = report.analyze_duplicates()
            report.export_report_csv(analysis)

            messagebox.showinfo("Export Successful", "Report exported to CSV file!")
            self.status_label.config(text="✅ Export complete", fg="green")

        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting report:\n{str(e)}")
            self.status_label.config(text="❌ Export failed", fg="red")

    def _generate_report_text(self) -> str:
        """Generate formatted report text"""
        if not self.last_stats:
            return "No data available"

        report = """
═══════════════════════════════════════════════════════════════
                    DUPLICATE ANALYSIS REPORT
═══════════════════════════════════════════════════════════════

SUMMARY STATISTICS
───────────────────────────────────────────────────────────────
"""
        report += f"Last Updated:           {self.last_stats['last_updated']}\n"
        report += f"Total Providers:        {self.last_stats['total_providers']}\n"
        report += f"Total Duplicates:       {self.last_stats['total_duplicates']}\n"
        report += f"Duplicate Ratio:        {self.last_stats['duplicate_ratio']:.2f}%\n"

        report += """
DUPLICATE BREAKDOWN
───────────────────────────────────────────────────────────────
"""
        report += f"Active Duplicates:      {self.last_stats['active_duplicates']} ⚠️\n"
        report += f"Cancelled Duplicates:   {self.last_stats['cancelled_duplicates']} ✓\n"
        report += f"Cross-Database:         {self.last_stats['cross_database']}\n"
        report += f"Within-Database:        {self.last_stats['within_database']}\n"

        quality = 100 - self.last_stats["duplicate_ratio"]
        report += f"""
DATA QUALITY
───────────────────────────────────────────────────────────────
Quality Score:          {quality:.2f}%

Rating Scale:
  95-100%: Excellent ✅
  85-95%:  Good ✅
  75-85%:  Fair ⚠️
  <75%:    Poor 🔴

═══════════════════════════════════════════════════════════════
For detailed analysis, run: python duplicate_analysis_report.py
═══════════════════════════════════════════════════════════════
"""
        return report


# Example usage in your admin app:
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Admin Dashboard - Duplicate Analysis Example")
    root.geometry("800x500")

    # Create the panel
    panel = AdminDuplicatePanel(root)

    root.mainloop()
