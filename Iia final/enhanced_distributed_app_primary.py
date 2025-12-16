#!/usr/bin/env python3



import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database managers
from distributed_database_manager import DistributedDatabaseManager
from enhanced_database_manager import EnhancedDatabaseManager
from distributed_llm_service import DistributedLLMService
from distributed_sorting_service import DistributedSortingService

class EnhancedServiceBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Booking System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # Initialize services with distributed database manager for advanced features
        self.db_manager = DistributedDatabaseManager()
        self.llm_service = DistributedLLMService()
        self.sorting_service = DistributedSortingService(self.db_manager)

        # Current user state
        self.current_user_id = None
        self.current_user_type = None  # 'customer', 'employee', 'admin'

        # Search preferences
        self.search_mode = tk.StringVar(value="advanced")

        # Create GUI
        self.create_main_gui()

        # Show login screen
        self.show_login_screen()

    def create_main_gui(self):
        """Create the main GUI layout"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(self.main_frame, text="Service Booking System",
                                font=('Arial', 20, 'bold'))
        title_label.pack(pady=10)

        # Mode indicator (hidden for cleaner UI)
        # self.mode_label = ttk.Label(self.main_frame, text="Mode: Primary-Only",
        #                             font=('Arial', 12), foreground='blue')
        # self.mode_label.pack(pady=5)

        # Content area (will be replaced with different screens)
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Service Booking System")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def show_login_screen(self):
        """Show login/registration screen"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        login_frame = ttk.LabelFrame(self.content_frame, text="Login / Register", padding="20")
        login_frame.pack(expand=True)

        # User type selection
        ttk.Label(login_frame, text="I am a:", font=('Arial', 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_type_var = tk.StringVar(value="customer")
        user_types = ttk.Combobox(login_frame, textvariable=self.user_type_var,
                                  values=["customer", "employee", "admin"], state="readonly")
        user_types.grid(row=0, column=1, pady=5, padx=10)

        # Login fields
        ttk.Label(login_frame, text="User ID:", font=('Arial', 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_id_entry = ttk.Entry(login_frame, font=('Arial', 12))
        self.user_id_entry.grid(row=1, column=1, pady=5, padx=10)

        # Buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Register", command=self.register).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Demo Mode", command=self.demo_mode).pack(side=tk.LEFT, padx=5)

        # Instructions
        instructions = ttk.Label(login_frame, text=
            "Instructions:\n" +
            "• Customers: Enter any user ID (e.g., 101, 102) or use Demo Mode\n" +
            "• Employees: Enter 1-5 for test employees or use Demo Mode\n" +
            "• Admin: Use 'admin' or use Demo Mode\n\n" +
            "Service Booking System Ready!\n" +
            "All databases connected and operational.",
            font=('Arial', 10), foreground='blue')
        instructions.grid(row=3, column=0, columnspan=2, pady=10)

    def login(self):
        """Handle user login"""
        user_id = self.user_id_entry.get().strip()
        user_type = self.user_type_var.get()

        if not user_id:
            messagebox.showerror("Error", "Please enter a user ID")
            return

        try:
            # Simple login logic for demo
            if user_type == "admin" and (user_id == "admin" or user_id.lower() == "admin"):
                self.current_user_id = "admin"
                self.current_user_type = "admin"
                self.show_admin_dashboard()
            elif user_type == "customer":
                self.current_user_id = int(user_id) if user_id.isdigit() and int(user_id) <= 5 else 1  # Use valid customer ID (1-5) or default to 1
                self.current_user_type = "customer"
                self.show_customer_dashboard()
            elif user_type == "employee":
                emp_id = int(user_id) if user_id.isdigit() else 1
                if 1 <= emp_id <= 5:  # Our test employees
                    self.current_user_id = emp_id
                    self.current_user_type = "employee"
                    self.show_employee_dashboard()
                else:
                    messagebox.showerror("Error", "Employee ID must be 1-5 for demo")
                    return
            else:
                messagebox.showerror("Error", "Invalid login")
                return

            self.status_var.set(f"Logged in as {user_type}: {user_id}")

        except Exception as e:
            messagebox.showerror("Login Error", f"Login failed: {e}")

    def register(self):
        """Handle user registration"""
        messagebox.showinfo("Register", "Registration would open a form here.\nFor demo, use Demo Mode or enter an ID directly.")

    def demo_mode(self):
        """Start in demo mode"""
        self.current_user_id = 1  # Use existing customer ID from sample data
        self.current_user_type = "customer"
        self.show_customer_dashboard()
        self.status_var.set("Demo Mode - Customer ID: 1")

    def show_customer_dashboard(self):
        """Show customer dashboard"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create customer dashboard
        dashboard_frame = ttk.LabelFrame(self.content_frame, text="Customer Dashboard", padding="10")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        # AI Search Section with Advanced Features
        search_frame = ttk.LabelFrame(dashboard_frame, text="🔍 Advanced AI-Powered Service Search", padding="10")
        search_frame.pack(fill=tk.X, pady=10)

        # Search options
        options_frame = ttk.Frame(search_frame)
        options_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0,5))
        ttk.Radiobutton(options_frame, text="🚀 Advanced Search (Federated)", variable=self.search_mode, value="advanced").pack(side=tk.LEFT, padx=(0,15))
        ttk.Radiobutton(options_frame, text="📊 Standard Search", variable=self.search_mode, value="standard").pack(side=tk.LEFT, padx=(0,15))

        # Search instruction and examples
        instructions_frame = ttk.Frame(search_frame)
        instructions_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0,5))

        instructions_text = "💬 Describe what you need (e.g., 'My sink is leaking', 'Emergency plumbing needed', 'AC not working')"
        ttk.Label(instructions_frame, text=instructions_text, font=('Arial', 10), foreground='#666').pack()

        # Search entry with examples
        self.search_entry = ttk.Entry(search_frame, font=('Arial', 12), width=50)
        self.search_entry.grid(row=2, column=0, columnspan=2, padx=10, sticky=tk.EW)

        # Search buttons
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=2, column=2, padx=5)

        ttk.Button(button_frame, text="🔍 Search", command=self.ai_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="⚙️ Analysis", command=self.show_search_analysis).pack(side=tk.LEFT, padx=2)

        # Example queries
        examples_text = "Examples: 'I need a plumber' | 'Emergency electrical help' | 'Paint my living room' | 'Car won't start'"
        ttk.Label(search_frame, text=examples_text, font=('Arial', 9), foreground='#999').grid(row=3, column=0, columnspan=3, pady=5)

        # Sorting options
        sorting_frame = ttk.Frame(dashboard_frame)
        sorting_frame.pack(fill=tk.X, pady=5)

        ttk.Label(sorting_frame, text="🔽 Sort by:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0,10))

        self.sort_var = tk.StringVar(value="rating_desc")
        sort_options = [
            ("⭐ Rating (High to Low)", "rating_desc"),
            ("⭐ Rating (Low to High)", "rating_asc"),
            ("💰 Price (Low to High)", "price_asc"),
            ("💰 Price (High to Low)", "price_desc"),
            ("🟢 Available First", "available"),
            ("📝 Name (A-Z)", "name_asc"),
            ("📝 Name (Z-A)", "name_desc"),
            ("🏢 Companies First", "companies_first"),
            ("👤 Workers First", "workers_first")
        ]

        for text, value in sort_options:
            ttk.Radiobutton(sorting_frame, text=text, variable=self.sort_var,
                           value=value, command=self.sort_results).pack(side=tk.LEFT, padx=5)

        # Results area
        results_frame = ttk.LabelFrame(dashboard_frame, text="Search Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Treeview for results
        columns = ('Name', 'Type', 'Service', 'Rating', 'Cost', 'Source')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # Action buttons
        action_frame = ttk.Frame(dashboard_frame)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="Create Order", command=self.create_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="My Orders", command=self.view_my_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT, padx=5)
    def ai_search(self):
        """Perform AI-powered natural language search with advanced query federation"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Search", "Please describe what service you need")
            return

        search_mode = self.search_mode.get()
        if search_mode == "advanced":
            self.status_var.set(f"🚀 Advanced AI Search: {search_term}...")
        else:
            self.status_var.set(f"🤖 AI Analyzing: {search_term}...")
        self.root.update()

        try:
            analysis = None
            db_results = None
            display_results = []

            # ------------------ ADVANCED MODE ------------------
            if search_mode == "advanced":
                # Federated engine should already combine and normalize results
                fed = self.sorting_service.get_federated_search_results(
                    search_term, limit=50
                )

                # Prefer sorted_results / combined_results / results in that order
                display_results = (
                    fed.get("sorted_results")
                    or fed.get("combined_results")
                    or fed.get("results")
                    or []
                )

                # Also pull raw DB combined view; if it has richer info, use it
                db_results = self.db_manager.get_cross_laptop_results(search_term)
                if db_results and db_results.get("combined_results"):
                    display_results = db_results["combined_results"]

                # Keep for status / popup
                analysis = fed.get("analysis", None)
                self._show_advanced_search_summary(fed)

            # ------------------ STANDARD MODE ------------------
            else:
                analysis = self.llm_service.analyze_distributed_service_request(
                    search_term, "both"
                )
                search_term_for_db = analysis.get("service_type", search_term)
                db_results = self.db_manager.get_cross_laptop_results(
                    search_term_for_db
                )
                display_results = db_results.get("combined_results", [])

            # Clear previous rows
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            if not display_results:
                self.status_var.set("No providers found for your search")
                return

            # Ensure we have an analysis object for urgency
            if analysis is None:
                try:
                    analysis = self.llm_service.analyze_distributed_service_request(
                        search_term, "both"
                    )
                except Exception:
                    analysis = {"urgency": "medium"}

            urgency_value = (analysis or {}).get("urgency", "medium")

            # ------------------ RENDER ROWS ------------------
            for provider in display_results:
                # robust access: always use .get(...)
                provider_type = provider.get("type", "Unknown")

                # urgency indicator (query-level)
                urgency_indicator = ""
                if urgency_value == "emergency":
                    urgency_indicator = "🚨 "
                elif urgency_value == "high":
                    urgency_indicator = "⚡ "

                type_indicator = "🏢 " if provider_type == "Company" else "👤 "

                service_name = provider.get(
                    "service_name",
                    provider.get(
                        "business_type",
                        provider.get("job_type", "General"),
                    ),
                )

                # rating
                rating = provider.get("rating") or 0
                try:
                    rating_display = f"{float(rating):.1f} ⭐" if rating else "N/A"
                except (ValueError, TypeError):
                    rating_display = "N/A"

                # cost
                cost = provider.get(
                    "avg_cost",
                    provider.get("avg_hourly_rate", provider.get("avg_cost_per_hour", 0)),
                )
                try:
                    cost_val = float(cost) if cost is not None else 0.0
                    cost_display = (
                        f"${cost_val}/hr 💰" if cost_val else "Contact for price"
                    )
                except (ValueError, TypeError):
                    cost_display = "Contact for price"

                data_source = provider.get("data_source", "Unknown")

                self.results_tree.insert(
                    "",
                    tk.END,
                    values=(
                        f"{urgency_indicator}{provider.get('name', 'Unknown')}",
                        f"{type_indicator}{provider_type}",
                        service_name,
                        rating_display,
                        cost_display,
                        data_source,
                    ),
                )

            # ------------------ STATUS BAR ------------------
            if search_mode == "advanced":
                confidence = float(
                    (fed or {}).get("recommendation_confidence", 0.0)
                )
                self.status_var.set(
                    f"🚀 Advanced Search Complete: Found {len(display_results)} providers"
                    f" | Confidence: {confidence:.0%}"
                )
            else:
                self.status_var.set(
                    f"🤖 AI Analysis: {analysis.get('service_type', 'unknown')} service detected"
                    f" | Urgency: {analysis.get('urgency', 'medium')}"
                    f" | Found {len(display_results)} providers"
                )

            # ------------------ OPTIONAL AI RECOMMENDATION POPUP ------------------
            try:
                recommendation = self.llm_service.suggest_provider_type(search_term)
                rec_type = recommendation.get("recommended_type", "both")
                conf = recommendation.get("confidence", 0.7)

                if display_results and conf > 0.7:
                    if rec_type == "company":
                        advice = (
                            "💡 AI Recommendation: Consider professional companies "
                            "for better warranty and insurance coverage."
                        )
                    elif rec_type == "individual":
                        advice = (
                            "💡 AI Recommendation: Individual workers may offer "
                            "better pricing and faster response times."
                        )
                    else:
                        advice = (
                            "💡 AI Recommendation: Both companies and individual "
                            "workers have good options - compare specific providers."
                        )

                    top = display_results[0]
                    advice += (
                        f"\n\n🏆 Top Match: {top.get('name', 'Unknown')} "
                        f"({top.get('type', 'Unknown')})"
                    )
                    advice += f"\n   ⭐ Rating: {top.get('rating', 'N/A')}"
                    advice += f"\n   💰 Cost: {top.get('avg_cost', 'N/A')}/hr"
                    advice += "\n   📞 Contact: Available in search results"

                    messagebox.showinfo("🤖 AI Recommendations", advice)
            except Exception:
                # Don't let a popup failure break the main flow
                pass

        except Exception as e:
            messagebox.showerror("Search Error", f"AI search failed: {e}")
            self.status_var.set("AI search failed")

    # def ai_search(self):
    #     """Perform AI-powered natural language search with advanced query federation"""
    #     search_term = self.search_entry.get().strip()
    #     if not search_term:
    #         messagebox.showwarning("Search", "Please describe what service you need")
    #         return

    #     search_mode = self.search_mode.get()
    #     if search_mode == "advanced":
    #         self.status_var.set(f"🚀 Advanced AI Search: {search_term}...")
    #     else:
    #         self.status_var.set(f"🤖 AI Analyzing: {search_term}...")
    #     self.root.update()

    #     try:
    #         # Use advanced search if selected
    #         if search_mode == "advanced":
    #             # Use advanced federated search with query federation
    #             results = self.sorting_service.get_federated_search_results(search_term, limit=15)

    #             # Extract combined results (both companies and employees)
    #             display_results = results.get('employees', [])
                
    #             # Also get company results from the database for complete results
    #             db_results = self.db_manager.get_cross_laptop_results(search_term)
    #             companies = db_results.get('companies', [])
                
    #             # Combine both results
    #             display_results = companies + display_results

    #             # Show advanced search summary
    #             self._show_advanced_search_summary(results)

    #         else:
    #             # Use standard search
    #             analysis = self.llm_service.analyze_distributed_service_request(search_term, 'both')

    #             # Get search results using the existing database manager for better performance
    #             search_term_for_db = analysis.get('service_type', search_term)
    #             db_results = self.db_manager.get_cross_laptop_results(search_term_for_db)

    #             # Convert to expected format
    #             display_results = db_results.get('combined_results', [])

    #         # Clear previous results
    #         for item in self.results_tree.get_children():
    #             self.results_tree.delete(item)

    #         # Add results to tree with AI-enhanced information
    #         for provider in display_results:
    #             # Add urgency indicator if applicable
    #             urgency_indicator = ""
    #             if search_mode == "advanced":
    #                 analysis = self.sorting_service.llm_service.analyze_distributed_service_request(search_term, 'both')
    #             if analysis.get('urgency') == 'emergency':
    #                 urgency_indicator = "🚨 "
    #             elif analysis.get('urgency') == 'high':
    #                 urgency_indicator = "⚡ "

    #             # Add provider type indicator
    #             type_indicator = "🏢 " if provider['type'] == 'Company' else "👤 "

    #             # Handle different field names for different result types
    #             service_name = provider.get('service_name', provider.get('business_type', provider.get('job_type', 'General')))
    #             rating = provider.get('rating', 0)
    #             cost = provider.get('avg_cost', provider.get('avg_hourly_rate', provider.get('avg_cost_per_hour', 0)))
    #             data_source = provider.get('data_source', 'Unknown')

    #             self.results_tree.insert('', tk.END, values=(
    #                 f"{urgency_indicator}{provider['name']}",
    #                 f"{type_indicator}{provider['type']}",
    #                 service_name,
    #                 f"{rating:.1f} ⭐" if rating else "N/A",
    #                 f"${cost}/hr 💰" if cost else "Contact for price",
    #                 data_source
    #             ))

    #         # Generate intelligent summary based on search mode
    #         if search_mode == "advanced":
    #             # Use federated search results for summary
    #             coverage = results.get('search_coverage', {})
    #             status_text = f"🚀 Advanced Search Complete: Found {len(display_results)} providers"
    #             status_text += f" | Confidence: {results.get('recommendation_confidence', 0):.0%}"
    #         else:
    #             # Use standard search results for summary
    #             summary = self.llm_service.generate_intelligent_summary(search_term, db_results if 'db_results' in locals() else {'combined_results': display_results})
    #             status_text = f"🤖 AI Analysis: {analysis.get('service_type', 'unknown')} service detected"
    #             status_text += f" | Urgency: {analysis.get('urgency', 'medium')}"
    #             status_text += f" | Found {len(display_results)} providers"

    #         self.status_var.set(status_text)

    #         # Show AI recommendations in a message box if results found
    #         if display_results:
    #             recommendation = self.llm_service.suggest_provider_type(search_term)
    #             rec_type = recommendation.get('recommended_type', 'both')
    #             confidence = recommendation.get('confidence', 0.7)

    #             if confidence > 0.7:
    #                 if rec_type == 'company':
    #                     advice = "💡 AI Recommendation: Consider professional companies for better warranty and insurance coverage."
    #                 elif rec_type == 'individual':
    #                     advice = "💡 AI Recommendation: Individual workers may offer better pricing and faster response times."
    #                 else:
    #                     advice = "💡 AI Recommendation: Both companies and individual workers have good options - compare specific providers."

    #                 # Show top provider details
    #                 if display_results:
    #                     top_provider = display_results[0]
    #                     advice += f"\n\n🏆 Top Match: {top_provider['name']} ({top_provider['type']})"
    #                     advice += f"\n   ⭐ Rating: {top_provider.get('rating', 'N/A')}"
    #                     advice += f"\n   💰 Cost: ${top_provider.get('avg_cost', 'N/A')}/hr"
    #                     advice += f"\n   📞 Contact: Available in search results"

    #                 messagebox.showinfo("🤖 AI Recommendations", advice)

    #     except Exception as e:
    #         messagebox.showerror("Search Error", f"AI search failed: {e}")
    #         self.status_var.set("AI search failed")

    def show_employee_dashboard(self):
        """Show employee dashboard"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        dashboard_frame = ttk.LabelFrame(self.content_frame, text="Employee Dashboard", padding="10")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(dashboard_frame, text=f"Employee ID: {self.current_user_id}",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        # Orders section
        orders_frame = ttk.LabelFrame(dashboard_frame, text="Available Orders", padding="10")
        orders_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.orders_tree = ttk.Treeview(orders_frame, columns=('Order ID', 'Customer', 'Service', 'Urgency', 'Cost', 'Created'),
                                       show='headings', height=10)

        for col in ['Order ID', 'Customer', 'Service', 'Urgency', 'Cost', 'Created']:
            self.orders_tree.heading(col, text=col)
            self.orders_tree.column(col, width=120)

        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        # Action buttons
        action_frame = ttk.Frame(dashboard_frame)
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Button(action_frame, text="Refresh Orders", command=self.refresh_orders).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Accept Order", command=self.accept_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Complete Order", command=self.complete_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel Order", command=self.cancel_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT, padx=5)

        self.refresh_orders()

    def show_admin_dashboard(self):
        """Show admin dashboard"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        dashboard_frame = ttk.LabelFrame(self.content_frame, text="Admin Dashboard", padding="10")
        dashboard_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(dashboard_frame, text="Admin Panel",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Admin functions
        functions_frame = ttk.Frame(dashboard_frame)
        functions_frame.pack(expand=True)

        ttk.Button(functions_frame, text="View All Users", command=self.view_all_users,
                  width=20).pack(pady=5)
        ttk.Button(functions_frame, text="View System Status", command=self.view_system_status,
                  width=20).pack(pady=5)
        ttk.Button(functions_frame, text="Database Health", command=self.view_database_health,
                  width=20).pack(pady=5)
        ttk.Button(functions_frame, text="Logout", command=self.logout,
                  width=20).pack(pady=20)

    def refresh_orders(self):
        """Refresh orders for employee with permanent storage"""
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        try:
            # Get available orders from enhanced database manager
            orders = self.db_manager.get_employee_orders_permanent(self.current_user_id)

            for order in orders:
                # Add urgency indicator
                urgency = order.get('urgency', 'medium')
                urgency_text = urgency.upper()
                if urgency == 'emergency':
                    urgency_text = f"🚨 {urgency_text}"
                elif urgency == 'high':
                    urgency_text = f"⚡ {urgency_text}"

                # Format cost safely
                estimated_cost = order.get('estimated_cost')
                try:
                    if estimated_cost and isinstance(estimated_cost, (int, float, str)):
                        cost = float(estimated_cost)
                        cost_text = f"${cost:.2f}" if cost else "Not estimated"
                    else:
                        cost_text = "Not estimated"
                except (ValueError, TypeError):
                    cost_text = "Not estimated"

                # Format created date safely
                created_at = order.get('created_at')
                if created_at:
                    try:
                        created_text = created_at.strftime('%Y-%m-%d %H:%M')
                    except (AttributeError, TypeError):
                        created_text = str(created_at)
                else:
                    created_text = "Unknown"

                self.orders_tree.insert('', tk.END, values=(
                    order.get('order_number', order.get('order_id', 'N/A')),  # Order Number/ID
                    order.get('customer_name', f"Customer {order.get('customer_id', 'Unknown')}"),  # Customer Name
                    order.get('service_type', 'N/A'),  # Service Type
                    urgency_text,  # Urgency
                    cost_text,  # Cost
                    created_text   # Created
                ))

            if not orders:
                self.orders_tree.insert('', tk.END, values=('No pending orders', '', '', '', '', ''))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {e}")

    def accept_order(self):
        """Accept selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order to accept")
            return

        try:
            selected_item = self.orders_tree.item(selection[0])
            order_data = selected_item['values']
            order_number = order_data[0]  # First column is order number

            if order_number == 'No pending orders' or order_number == 'N/A':
                messagebox.showwarning("Invalid Selection", "Please select a valid order")
                return

            # Get actual order_id from database
            try:
                # Find the order_id from the order number
                result = self.db_manager.execute_query("SELECT order_id FROM ORDER_TABLE WHERE order_number = %s", (order_number,), 'primary')
                if result:
                    order_id = result[0]['order_id']
                else:
                    messagebox.showwarning("Error", "Order not found")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to find order: {e}")
                return

            # Confirm acceptance
            result = messagebox.askyesno("Accept Order",
                f"Are you sure you want to accept Order #{order_number}?\n\n"
                f"This will mark the order as 'Accepted' and assign it to you.")

            if result:
                # Update order status with permanent storage
                affected_rows = self.db_manager.update_order_status_permanent(
                    order_id, 'accepted', self.current_user_id
                )




                if affected_rows > 0:
                    messagebox.showinfo("Order Accepted",
                        f"Order #{order_id} accepted successfully!\n"
                        f"The order has been assigned to you and saved permanently.")
                    self.refresh_orders()
                    self.status_var.set(f"Order #{order_id} accepted and saved")
                else:
                    messagebox.showwarning("Update Failed",
                        "Order may have been accepted by another worker. Please refresh.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to accept order: {e}")

    def complete_order(self):
        """Complete selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order to complete")
            return

        try:
            selected_item = self.orders_tree.item(selection[0])
            order_data = selected_item['values']
            order_number = order_data[0]  # First column is order number

            if order_number == 'No pending orders' or order_number == 'N/A':
                messagebox.showwarning("Invalid Selection", "Please select a valid order")
                return

            # Get actual order_id from database
            try:
                # Find the order_id from the order number
                result = self.db_manager.execute_query("SELECT order_id FROM ORDER_TABLE WHERE order_number = %s", (order_number,), 'primary')
                if result:
                    order_id = result[0]['order_id']
                else:
                    messagebox.showwarning("Error", "Order not found")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to find order: {e}")
                return

            # Create completion dialog for rating and notes
            self.create_completion_dialog(order_id)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete order: {e}")

    def create_completion_dialog(self, order_id):
        """Create order completion dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Complete Order")
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')

        ttk.Label(dialog, text=f"Complete Order #{order_id}",
                 font=('Arial', 14, 'bold')).pack(pady=10)

        # Actual Cost
        ttk.Label(dialog, text="Actual Cost ($):", font=('Arial', 11)).pack(anchor=tk.W, padx=20)
        cost_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=cost_var, width=20).pack(padx=20, pady=5)

        # Provider Notes
        ttk.Label(dialog, text="Work Completed:", font=('Arial', 11)).pack(anchor=tk.W, padx=20, pady=(10, 0))
        notes_text = tk.Text(dialog, height=6, width=50)
        notes_text.pack(padx=20, pady=5)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        def submit_completion():
            try:
                actual_cost = float(cost_var.get()) if cost_var.get() else None
                provider_notes = notes_text.get("1.0", tk.END).strip()

                # Update order status with permanent storage
                affected_rows = self.db_manager.update_order_status_permanent(
                    order_id, 'completed', self.current_user_id, provider_notes, actual_cost
                )

                if affected_rows > 0:
                    messagebox.showinfo("Order Completed",
                        f"Order #{order_id} marked as completed and saved permanently!")
                    dialog.destroy()
                    self.refresh_orders()
                    self.status_var.set(f"Order #{order_id} completed and saved")
                else:
                    messagebox.showwarning("Update Failed",
                        "Unable to complete order. Please check order status.")

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for cost")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to complete order: {e}")

        ttk.Button(button_frame, text="Complete Order", command=submit_completion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def cancel_order(self):
        """Cancel selected order (employee)"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an order to cancel")
            return

        try:
            selected_item = self.orders_tree.item(selection[0])
            order_data = selected_item['values']
            order_number = order_data[0]  # First column is order number

            if order_number == 'No pending orders' or order_number == 'N/A':
                messagebox.showwarning("Invalid Selection", "Please select a valid order")
                return

            # Get actual order_id from database
            try:
                # Find the order_id from the order number
                result = self.db_manager.execute_query("SELECT order_id FROM ORDER_TABLE WHERE order_number = %s", (order_number,), 'primary')
                if result:
                    order_id = result[0]['order_id']
                else:
                    messagebox.showwarning("Error", "Order not found")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to find order: {e}")
                return

            # Confirm cancellation
            result = messagebox.askyesno("Cancel Order",
                f"Are you sure you want to cancel Order #{order_number}?\n\n"
                f"This will make the order available to other workers.")

            if result:
                # Cancel order with permanent storage
                affected_rows = self.db_manager.cancel_order_permanent(order_id, self.current_user_id)

                if affected_rows > 0:
                    messagebox.showinfo("Order Cancelled",
                        f"Order #{order_number} cancelled successfully and saved permanently!")
                    self.refresh_orders()
                    self.status_var.set(f"Order #{order_number} cancelled and saved")
                else:
                    messagebox.showwarning("Update Failed",
                        "Unable to cancel order. Please check order status.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {e}")

    def create_order(self):
        """Create new order"""
        # Get selected provider from search results
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a service provider from the search results first")
            return

        # Get selected provider details
        selected_item = self.results_tree.item(selection[0])
        provider_name = selected_item['values'][0].replace('🚨 ', '').replace('⚡ ', '').replace('🏢 ', '').replace('👤 ', '')
        provider_type = selected_item['values'][1].replace('🏢 ', '').replace('👤 ', '')
        service_name = selected_item['values'][2]
        cost_text = selected_item['values'][4]
        try:
            # Extract numeric value from cost text
            if isinstance(cost_text, str):
                cost_per_hour = float(cost_text.replace('$', '').replace('/hr 💰', '').replace('/hr', '').strip())
            else:
                cost_per_hour = float(cost_text) if cost_text else 0.0
        except (ValueError, TypeError):
            cost_per_hour = 0.0

        # Create order creation dialog
        self.create_order_dialog(provider_name, provider_type, service_name, cost_per_hour)

    def create_order_dialog(self, provider_name, provider_type, service_name, cost_per_hour):
        """Create order creation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create New Order")
        dialog.geometry("600x500")
        dialog.configure(bg='#f0f0f0')

        # Provider Information
        info_frame = ttk.LabelFrame(dialog, text="Service Provider", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text=f"Provider: {provider_name} ({provider_type})", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Service: {service_name}", font=('Arial', 11)).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Rate: ${cost_per_hour}/hour", font=('Arial', 11)).pack(anchor=tk.W)

        # Order Details
        details_frame = ttk.LabelFrame(dialog, text="Order Details", padding="10")
        details_frame.pack(fill=tk.X, padx=10, pady=5)

        # Service Description
        ttk.Label(details_frame, text="Service Description:", font=('Arial', 11)).pack(anchor=tk.W)
        description_text = tk.Text(details_frame, height=4, width=60)
        description_text.pack(fill=tk.X, pady=5)
        description_text.insert(tk.END, f"I need help with {service_name.lower()}")

        # Urgency
        ttk.Label(details_frame, text="Urgency:", font=('Arial', 11)).pack(anchor=tk.W, pady=(10, 0))
        urgency_var = tk.StringVar(value="medium")
        urgency_frame = ttk.Frame(details_frame)
        urgency_frame.pack(fill=tk.X)
        ttk.Radiobutton(urgency_frame, text="Low", variable=urgency_var, value="low").pack(side=tk.LEFT)
        ttk.Radiobutton(urgency_frame, text="Medium", variable=urgency_var, value="medium").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(urgency_frame, text="High", variable=urgency_var, value="high").pack(side=tk.LEFT)
        ttk.Radiobutton(urgency_frame, text="Emergency", variable=urgency_var, value="emergency").pack(side=tk.LEFT, padx=10)

        # Estimated Hours
        ttk.Label(details_frame, text="Estimated Hours:", font=('Arial', 11)).pack(anchor=tk.W, pady=(10, 0))
        hours_frame = ttk.Frame(details_frame)
        hours_frame.pack(fill=tk.X)
        hours_var = tk.StringVar(value="2")
        ttk.Entry(hours_frame, textvariable=hours_var, width=10).pack(side=tk.LEFT)
        ttk.Label(hours_frame, text="hours", font=('Arial', 11)).pack(side=tk.LEFT, padx=5)

        # Customer Notes
        ttk.Label(details_frame, text="Additional Notes:", font=('Arial', 11)).pack(anchor=tk.W, pady=(10, 0))
        notes_text = tk.Text(details_frame, height=3, width=60)
        notes_text.pack(fill=tk.X, pady=5)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def submit_order():
            try:
                # Get order details
                service_description = description_text.get("1.0", tk.END).strip()
                urgency = urgency_var.get()
                estimated_hours = float(hours_var.get())
                customer_notes = notes_text.get("1.0", tk.END).strip()
                try:
                    cost_per_hour_num = float(cost_per_hour) if isinstance(cost_per_hour, (int, float, str)) else 0.0
                    estimated_cost = cost_per_hour_num * estimated_hours
                except (ValueError, TypeError):
                    estimated_cost = 0.0

                if not service_description:
                    messagebox.showwarning("Missing Information", "Please provide a service description")
                    return

                # Create order in database
                self.create_order_in_db(
                    provider_name, provider_type, service_name,
                    service_description, urgency, estimated_cost, customer_notes
                )

                # Safe cost formatting for messagebox
                try:
                    cost_display = f"${estimated_cost:.2f}" if isinstance(estimated_cost, (int, float)) else "Not estimated"
                except (ValueError, TypeError):
                    cost_display = "Not estimated"

                messagebox.showinfo("Order Created", f"Order created successfully!\n\nProvider: {provider_name}\nService: {service_name}\nEstimated Cost: {cost_display}\nUrgency: {urgency.capitalize()}")
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number for estimated hours")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create order: {e}")

        ttk.Button(button_frame, text="Create Order", command=submit_order).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def create_order_in_db(self, provider_name, provider_type, service_name, description, urgency, estimated_cost, customer_notes):
        """Create order in database with permanent storage"""
        try:
            # Get provider_id using enhanced database manager
            provider_details = self.db_manager.get_provider_details(provider_name, provider_type)
            if provider_details:
                provider_id = provider_details.get('id', 1)
            else:
                # Fallback: get employee_id for individual workers
                provider_id = self.db_manager.get_employee_id_from_provider(provider_name, provider_type)

            # Create order with permanent storage
            order_id = self.db_manager.create_order_permanent(
                self.current_user_id, provider_id, provider_type.lower(), service_name,
                description, urgency, estimated_cost, customer_notes
            )

            self.status_var.set(f"Order #{order_id} created permanently with {provider_name}")
            return order_id

        except Exception as e:
            raise Exception(f"Failed to create order: {e}")

    def view_my_orders(self):
        """View customer's orders"""
        dialog = tk.Toplevel(self.root)
        dialog.title("My Orders")
        dialog.geometry("900x600")
        dialog.configure(bg='#f0f0f0')

        # Title
        ttk.Label(dialog, text=f"Orders for Customer ID: {self.current_user_id}",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Orders Treeview
        columns = ('Order ID', 'Provider', 'Service', 'Status', 'Urgency', 'Cost', 'Created', 'Updated')
        orders_tree = ttk.Treeview(dialog, columns=columns, show='headings', height=15)

        for col in columns:
            orders_tree.heading(col, text=col)
            orders_tree.column(col, width=120)

        orders_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=orders_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        orders_tree.configure(yscrollcommand=scrollbar.set)

        # Load orders
        self.load_customer_orders(orders_tree)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Refresh", command=lambda: self.load_customer_orders(orders_tree)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)

    def load_customer_orders(self, orders_tree):
        """Load customer orders into treeview with permanent storage"""
        # Clear existing items
        for item in orders_tree.get_children():
            orders_tree.delete(item)

        try:
            # Get orders from enhanced database manager
            orders = self.db_manager.get_customer_orders_permanent(self.current_user_id)

            for order in orders:
                # Add urgency indicator
                urgency = order.get('urgency', 'medium')
                urgency_text = urgency.upper()
                if urgency == 'emergency':
                    urgency_text = f"🚨 {urgency_text}"
                elif urgency == 'high':
                    urgency_text = f"⚡ {urgency_text}"

                # Add status indicator
                status = order.get('status', 'pending')
                status_text = status.upper().replace('_', ' ')
                if status == 'pending':
                    status_text = f"⏳ {status_text}"
                elif status == 'accepted':
                    status_text = f"✅ {status_text}"
                elif status == 'in_progress':
                    status_text = f"🔧 {status_text}"
                elif status == 'completed':
                    status_text = f"🎉 {status_text}"
                elif status == 'cancelled':
                    status_text = f"❌ {status_text}"

                # Format cost safely
                estimated_cost = order.get('estimated_cost')
                try:
                    cost_text = f"${float(estimated_cost):.2f}" if estimated_cost and isinstance(estimated_cost, (int, float, str)) else "Not estimated"
                except (ValueError, TypeError):
                    cost_text = "Not estimated"

                # Format dates safely
                created_at = order.get('created_at')
                updated_at = order.get('updated_at')

                created_text = created_at.strftime('%Y-%m-%d %H:%M') if created_at else "Unknown"
                updated_text = updated_at.strftime('%Y-%m-%d %H:%M') if updated_at else "Unknown"

                orders_tree.insert('', tk.END, values=(
                    order.get('order_number', order.get('order_id', 'N/A')),  # Order Number/ID
                    order.get('order_id', 'Not assigned'),  # Provider Name (will be updated when assigned)
                    order.get('service_type', 'N/A'),  # Service Type
                    status_text,  # Status
                    urgency_text,  # Urgency
                    cost_text,  # Cost
                    created_text,  # Created
                    updated_text   # Updated
                ))

            if not orders:
                orders_tree.insert('', tk.END, values=('No orders found', '', '', '', '', '', '', ''))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {e}")

    def view_all_users(self):
        """View all users (admin)"""
        dialog = tk.Toplevel(self.root)
        dialog.title("All Users - Admin Dashboard")
        dialog.geometry("1200x700")
        dialog.configure(bg='#f0f0f0')

        # Title
        ttk.Label(dialog, text="All Users - Admin Dashboard",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Create notebook for tabs
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Customers Tab
        customers_frame = ttk.Frame(notebook)
        notebook.add(customers_frame, text="Customers")

        customers_columns = ('ID', 'Name', 'Email', 'Phone', 'Membership', 'Orders', 'Spent', 'Status', 'Verified', 'Joined')
        customers_tree = ttk.Treeview(customers_frame, columns=customers_columns, show='headings', height=15)

        for col in customers_columns:
            customers_tree.heading(col, text=col)
            if col in ['ID', 'Orders']:
                customers_tree.column(col, width=50)
            elif col == 'Spent':
                customers_tree.column(col, width=80)
            elif col == 'Status':
                customers_tree.column(col, width=70)
            else:
                customers_tree.column(col, width=120)

        customers_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Employees Tab
        employees_frame = ttk.Frame(notebook)
        notebook.add(employees_frame, text="Employees")

        employees_columns = ('ID', 'Name', 'Email', 'Phone', 'Job Type', 'Experience', 'Orders', 'Earnings', 'Rating', 'Available', 'Status')
        employees_tree = ttk.Treeview(employees_frame, columns=employees_columns, show='headings', height=15)

        for col in employees_columns:
            employees_tree.heading(col, text=col)
            if col in ['ID', 'Experience', 'Orders']:
                employees_tree.column(col, width=60)
            elif col == 'Rating':
                employees_tree.column(col, width=50)
            elif col == 'Available':
                employees_tree.column(col, width=80)
            else:
                employees_tree.column(col, width=120)

        employees_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Companies Tab
        companies_frame = ttk.Frame(notebook)
        notebook.add(companies_frame, text="Companies")

        companies_columns = ('ID', 'Company Name', 'Email', 'Phone', 'Business Type', 'Rating', 'Reviews', 'Specialization')
        companies_tree = ttk.Treeview(companies_frame, columns=companies_columns, show='headings', height=15)

        for col in companies_columns:
            companies_tree.heading(col, text=col)
            if col in ['ID', 'Rating', 'Reviews']:
                companies_tree.column(col, width=50)
            else:
                companies_tree.column(col, width=150)

        companies_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Load users data
        self.load_admin_users_data(customers_tree, employees_tree, companies_tree)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Refresh",
                  command=lambda: self.load_admin_users_data(customers_tree, employees_tree, companies_tree)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)

    def load_admin_users_data(self, customers_tree, employees_tree, companies_tree):
        """Load all users data into admin dashboard"""
        try:
            # Clear existing items
            for tree in [customers_tree, employees_tree, companies_tree]:
                for item in tree.get_children():
                    tree.delete(item)

            # Get all users from database
            users_data = self.db_manager.get_all_users_admin()

            # Load customers
            for customer in users_data.get('customers', []):
                status = "Active" if customer['is_active'] else "Inactive"
                verified = "Yes" if customer['is_verified'] else "No"

                # Safe date formatting
                try:
                    joined = customer['registration_date'].strftime('%Y-%m-%d') if customer['registration_date'] else "Unknown"
                except (AttributeError, TypeError):
                    joined = str(customer.get('registration_date', 'Unknown'))

                customers_tree.insert('', tk.END, values=(
                    customer['id'],
                    customer['name'],
                    customer['email'],
                    customer['phone'],
                    customer['membership_level'],
                    customer['total_orders'],
                    f"${customer['total_spent']:.2f}" if customer['total_spent'] else "$0.00",
                    status,
                    verified,
                    joined
                ))

            # Load employees
            for employee in users_data.get('employees', []):
                status = "Active" if employee['is_active'] else "Inactive"
                available = employee.get('availability_status', 'Unknown')

                # Safe date formatting
                try:
                    joined = employee['registration_date'].strftime('%Y-%m-%d') if employee['registration_date'] else "Unknown"
                except (AttributeError, TypeError):
                    joined = str(employee.get('registration_date', 'Unknown'))

                employees_tree.insert('', tk.END, values=(
                    employee['id'],
                    employee['name'],
                    employee['email'],
                    employee['phone'],
                    employee['job_type'],
                    f"{employee['experience_years']} years",
                    employee['total_orders'],
                    f"${employee['total_earnings']:.2f}" if employee['total_earnings'] else "$0.00",
                    f"{employee['rating']:.1f}" if employee['rating'] else "0.0",
                    available,
                    status
                ))

            # Load companies
            for company in users_data.get('companies', []):
                # Truncate long descriptions for display
                spec = company.get('specialization_areas', '')
                if len(spec) > 50:
                    spec = spec[:47] + "..."

                companies_tree.insert('', tk.END, values=(
                    company['id'],
                    company['name'],
                    company['email'],
                    company['phone'],
                    company['business_type'],
                    f"{company['rating']:.1f}" if company['rating'] else "0.0",
                    company['total_reviews'],
                    spec
                ))

            # Add no data messages if needed
            if not users_data.get('customers'):
                customers_tree.insert('', tk.END, values=('No customers found', '', '', '', '', '', '', '', '', ''))
            if not users_data.get('employees'):
                employees_tree.insert('', tk.END, values=('No employees found', '', '', '', '', '', '', '', '', '', ''))
            if not users_data.get('companies'):
                companies_tree.insert('', tk.END, values=('No companies found', '', '', '', '', '', '', ''))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users data: {e}")

    def view_system_status(self):
        """View system status"""
        dialog = tk.Toplevel(self.root)
        dialog.title("System Status - Admin Dashboard")
        dialog.geometry("800x600")
        dialog.configure(bg='#f0f0f0')

        # Title
        ttk.Label(dialog, text="System Status - Admin Dashboard",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Main frame with scroll
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create canvas with scrollbar
        canvas = tk.Canvas(main_frame, bg='white')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Load system status data
        try:
            status_data = self.db_manager.get_system_status()

            # Database Health Section
            db_frame = ttk.LabelFrame(scrollable_frame, text="Database Health", padding=15)
            db_frame.pack(fill=tk.X, padx=10, pady=10)

            db_health = status_data.get('database_health', {})
            ttk.Label(db_frame, text=f"Primary Database: {'✅ Connected' if db_health.get('primary') else '❌ Disconnected'}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(db_frame, text=f"Secondary Database: {'✅ Connected' if db_health.get('secondary') else '❌ Disconnected'}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(db_frame, text=f"Mode: {db_health.get('mode', 'Unknown')}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Order Statistics Section
            orders_frame = ttk.LabelFrame(scrollable_frame, text="Order Statistics", padding=15)
            orders_frame.pack(fill=tk.X, padx=10, pady=10)

            total_orders = status_data.get('total_orders', 0)
            orders_by_status = status_data.get('orders_by_status', {})

            ttk.Label(orders_frame, text=f"Total Orders: {total_orders}",
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)

            order_status_labels = [
                ("⏳ Pending", orders_by_status.get('pending', 0)),
                ("✅ Accepted", orders_by_status.get('accepted', 0)),
                ("🔧 In Progress", orders_by_status.get('in_progress', 0)),
                ("🎉 Completed", orders_by_status.get('completed', 0)),
                ("❌ Cancelled", orders_by_status.get('cancelled', 0))
            ]

            for label, count in order_status_labels:
                ttk.Label(orders_frame, text=f"{label}: {count}",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # User Statistics Section
            users_frame = ttk.LabelFrame(scrollable_frame, text="User Statistics", padding=15)
            users_frame.pack(fill=tk.X, padx=10, pady=10)

            total_users = status_data.get('total_users', 0)
            active_users = status_data.get('active_users', 0)

            ttk.Label(users_frame, text=f"Total Users: {total_users}",
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)
            ttk.Label(users_frame, text=f"Active Users: {active_users}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Calculate percentage
            if total_users > 0:
                active_percentage = (active_users / total_users) * 100
                ttk.Label(users_frame, text=f"User Activity Rate: {active_percentage:.1f}%",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Service Statistics Section
            services_frame = ttk.LabelFrame(scrollable_frame, text="Service Statistics", padding=15)
            services_frame.pack(fill=tk.X, padx=10, pady=10)

            services_offered = status_data.get('services_offered', 0)
            ttk.Label(services_frame, text=f"Services Offered: {services_offered}",
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)

            if services_offered > 0:
                ttk.Label(services_frame, text="🟢 Service catalog is active",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            else:
                ttk.Label(services_frame, text="🔴 No services available",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # System Status Summary
            summary_frame = ttk.LabelFrame(scrollable_frame, text="System Health Summary", padding=15)
            summary_frame.pack(fill=tk.X, padx=10, pady=10)

            # Calculate overall health score
            health_score = 0
            max_score = 3

            if db_health.get('primary'):
                health_score += 1
            if db_health.get('secondary'):
                health_score += 1
            if total_orders > 0:
                health_score += 1

            if health_score == max_score:
                status_emoji = "🟢"
                status_text = "Excellent"
                status_color = "green"
            elif health_score >= max_score - 1:
                status_emoji = "🟡"
                status_text = "Good"
                status_color = "orange"
            else:
                status_emoji = "🔴"
                status_text = "Critical"
                status_color = "red"

            ttk.Label(summary_frame, text=f"{status_emoji} Overall System Status: {status_text}",
                     font=('Arial', 14, 'bold'), foreground=status_color).pack(anchor=tk.W, pady=5)
            ttk.Label(summary_frame, text=f"Health Score: {health_score}/{max_score}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Last Updated
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ttk.Label(summary_frame, text=f"Last Updated: {current_time}",
                     font=('Arial', 10, 'italic')).pack(anchor=tk.W, pady=5)

        except Exception as e:
            ttk.Label(scrollable_frame, text=f"Error loading system status: {e}",
                     font=('Arial', 12), foreground="red").pack(pady=20)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Refresh",
                  command=lambda: self.refresh_system_status(dialog, scrollable_frame)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_system_status(self, dialog, scrollable_frame):
        """Refresh system status display"""
        # Clear existing widgets
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Recreate status display
        try:
            status_data = self.db_manager.get_system_status()

            # Database Health Section
            db_frame = ttk.LabelFrame(scrollable_frame, text="Database Health", padding=15)
            db_frame.pack(fill=tk.X, padx=10, pady=10)

            db_health = status_data.get('database_health', {})
            ttk.Label(db_frame, text=f"Primary Database: {'✅ Connected' if db_health.get('primary') else '❌ Disconnected'}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(db_frame, text=f"Secondary Database: {'✅ Connected' if db_health.get('secondary') else '❌ Disconnected'}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(db_frame, text=f"Mode: {db_health.get('mode', 'Unknown')}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Order Statistics Section
            orders_frame = ttk.LabelFrame(scrollable_frame, text="Order Statistics", padding=15)
            orders_frame.pack(fill=tk.X, padx=10, pady=10)

            total_orders = status_data.get('total_orders', 0)
            orders_by_status = status_data.get('orders_by_status', {})

            ttk.Label(orders_frame, text=f"Total Orders: {total_orders}",
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)

            order_status_labels = [
                ("⏳ Pending", orders_by_status.get('pending', 0)),
                ("✅ Accepted", orders_by_status.get('accepted', 0)),
                ("🔧 In Progress", orders_by_status.get('in_progress', 0)),
                ("🎉 Completed", orders_by_status.get('completed', 0)),
                ("❌ Cancelled", orders_by_status.get('cancelled', 0))
            ]

            for label, count in order_status_labels:
                ttk.Label(orders_frame, text=f"{label}: {count}",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # User Statistics Section
            users_frame = ttk.LabelFrame(scrollable_frame, text="User Statistics", padding=15)
            users_frame.pack(fill=tk.X, padx=10, pady=10)

            total_users = status_data.get('total_users', 0)
            active_users = status_data.get('active_users', 0)

            ttk.Label(users_frame, text=f"Total Users: {total_users}",
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)
            ttk.Label(users_frame, text=f"Active Users: {active_users}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Calculate percentage
            if total_users > 0:
                active_percentage = (active_users / total_users) * 100
                ttk.Label(users_frame, text=f"User Activity Rate: {active_percentage:.1f}%",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Service Statistics Section
            services_frame = ttk.LabelFrame(scrollable_frame, text="Service Statistics", padding=15)
            services_frame.pack(fill=tk.X, padx=10, pady=10)

            services_offered = status_data.get('services_offered', 0)
            ttk.Label(services_frame, text=f"Services Offered: {services_offered}",
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=5)

            if services_offered > 0:
                ttk.Label(services_frame, text="🟢 Service catalog is active",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            else:
                ttk.Label(services_frame, text="🔴 No services available",
                         font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # System Status Summary
            summary_frame = ttk.LabelFrame(scrollable_frame, text="System Health Summary", padding=15)
            summary_frame.pack(fill=tk.X, padx=10, pady=10)

            # Calculate overall health score
            health_score = 0
            max_score = 3

            if db_health.get('primary'):
                health_score += 1
            if db_health.get('secondary'):
                health_score += 1
            if total_orders > 0:
                health_score += 1

            if health_score == max_score:
                status_emoji = "🟢"
                status_text = "Excellent"
                status_color = "green"
            elif health_score >= max_score - 1:
                status_emoji = "🟡"
                status_text = "Good"
                status_color = "orange"
            else:
                status_emoji = "🔴"
                status_text = "Critical"
                status_color = "red"

            ttk.Label(summary_frame, text=f"{status_emoji} Overall System Status: {status_text}",
                     font=('Arial', 14, 'bold'), foreground=status_color).pack(anchor=tk.W, pady=5)
            ttk.Label(summary_frame, text=f"Health Score: {health_score}/{max_score}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Last Updated
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ttk.Label(summary_frame, text=f"Last Updated: {current_time}",
                     font=('Arial', 10, 'italic')).pack(anchor=tk.W, pady=5)

        except Exception as e:
            ttk.Label(scrollable_frame, text=f"Error refreshing system status: {e}",
                     font=('Arial', 12), foreground="red").pack(pady=20)

    def view_database_health(self):
        """View database health"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Database Health - Admin Dashboard")
        dialog.geometry("600x400")
        dialog.configure(bg='#f0f0f0')

        # Title
        ttk.Label(dialog, text="Database Health - Admin Dashboard",
                 font=('Arial', 16, 'bold')).pack(pady=10)

        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        try:
            health = self.db_manager.get_database_health()

            # Database Connections Section
            conn_frame = ttk.LabelFrame(main_frame, text="Database Connections", padding=15)
            conn_frame.pack(fill=tk.X, pady=10)

            # Primary Database Status
            primary_status = "✅ Connected" if health.get('primary') else "❌ Disconnected"
            primary_color = "green" if health.get('primary') else "red"
            ttk.Label(conn_frame, text=f"Primary Database:",
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 2))
            ttk.Label(conn_frame, text=primary_status,
                     font=('Arial', 14, 'bold'), foreground=primary_color).pack(anchor=tk.W, pady=(0, 10))

            # Secondary Database Status
            secondary_status = "✅ Connected" if health.get('secondary') else "❌ Disconnected"
            secondary_color = "green" if health.get('secondary') else "red"
            ttk.Label(conn_frame, text=f"Secondary Database:",
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 2))
            ttk.Label(conn_frame, text=secondary_status,
                     font=('Arial', 14, 'bold'), foreground=secondary_color).pack(anchor=tk.W, pady=(0, 10))

            # System Information Section
            info_frame = ttk.LabelFrame(main_frame, text="System Information", padding=15)
            info_frame.pack(fill=tk.X, pady=10)

            ttk.Label(info_frame, text=f"Operating Mode: {health.get('mode', 'Unknown')}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Cache Size: {health.get('cache_size', 0)} records",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Connection Summary
            summary_frame = ttk.LabelFrame(main_frame, text="Connection Summary", padding=15)
            summary_frame.pack(fill=tk.X, pady=10)

            total_connections = sum([health.get('primary', False), health.get('secondary', False)])
            connection_text = f"{total_connections}/2 databases connected"

            if total_connections == 2:
                summary_color = "green"
                summary_status = "✅ All databases operational"
            elif total_connections == 1:
                summary_color = "orange"
                summary_status = "⚠️ Partial connectivity"
            else:
                summary_color = "red"
                summary_status = "❌ No database connections"

            ttk.Label(summary_frame, text=connection_text,
                     font=('Arial', 14, 'bold'), foreground=summary_color).pack(anchor=tk.W)
            ttk.Label(summary_frame, text=summary_status,
                     font=('Arial', 12), foreground=summary_color).pack(anchor=tk.W, pady=(5, 0))

            # Status Note
            note_frame = ttk.Frame(main_frame)
            note_frame.pack(fill=tk.X, pady=10)

            note_text = "Note: Secondary database will connect automatically when the secondary laptop comes online!"
            ttk.Label(note_frame, text=note_text,
                     font=('Arial', 10, 'italic'), foreground="blue").pack(anchor=tk.W)

            # Last Updated
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ttk.Label(main_frame, text=f"Last Updated: {current_time}",
                     font=('Arial', 9, 'italic')).pack(anchor=tk.W, pady=5)

        except Exception as e:
            error_frame = ttk.Frame(main_frame)
            error_frame.pack(fill=tk.BOTH, expand=True)
            ttk.Label(error_frame, text=f"Error loading database health: {e}",
                     font=('Arial', 12), foreground="red").pack(pady=20)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(button_frame, text="Refresh",
                  command=lambda: self.refresh_database_health(dialog, main_frame)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT)

    def refresh_database_health(self, dialog, main_frame):
        """Refresh database health display"""
        # Clear existing widgets
        for widget in main_frame.winfo_children():
            widget.destroy()

        # Recreate health display
        try:
            health = self.db_manager.get_database_health()

            # Database Connections Section
            conn_frame = ttk.LabelFrame(main_frame, text="Database Connections", padding=15)
            conn_frame.pack(fill=tk.X, pady=10)

            # Primary Database Status
            primary_status = "✅ Connected" if health.get('primary') else "❌ Disconnected"
            primary_color = "green" if health.get('primary') else "red"
            ttk.Label(conn_frame, text=f"Primary Database:",
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 2))
            ttk.Label(conn_frame, text=primary_status,
                     font=('Arial', 14, 'bold'), foreground=primary_color).pack(anchor=tk.W, pady=(0, 10))

            # Secondary Database Status
            secondary_status = "✅ Connected" if health.get('secondary') else "❌ Disconnected"
            secondary_color = "green" if health.get('secondary') else "red"
            ttk.Label(conn_frame, text=f"Secondary Database:",
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 2))
            ttk.Label(conn_frame, text=secondary_status,
                     font=('Arial', 14, 'bold'), foreground=secondary_color).pack(anchor=tk.W, pady=(0, 10))

            # System Information Section
            info_frame = ttk.LabelFrame(main_frame, text="System Information", padding=15)
            info_frame.pack(fill=tk.X, pady=10)

            ttk.Label(info_frame, text=f"Operating Mode: {health.get('mode', 'Unknown')}",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)
            ttk.Label(info_frame, text=f"Cache Size: {health.get('cache_size', 0)} records",
                     font=('Arial', 12)).pack(anchor=tk.W, pady=2)

            # Connection Summary
            summary_frame = ttk.LabelFrame(main_frame, text="Connection Summary", padding=15)
            summary_frame.pack(fill=tk.X, pady=10)

            total_connections = sum([health.get('primary', False), health.get('secondary', False)])
            connection_text = f"{total_connections}/2 databases connected"

            if total_connections == 2:
                summary_color = "green"
                summary_status = "✅ All databases operational"
            elif total_connections == 1:
                summary_color = "orange"
                summary_status = "⚠️ Partial connectivity"
            else:
                summary_color = "red"
                summary_status = "❌ No database connections"

            ttk.Label(summary_frame, text=connection_text,
                     font=('Arial', 14, 'bold'), foreground=summary_color).pack(anchor=tk.W)
            ttk.Label(summary_frame, text=summary_status,
                     font=('Arial', 12), foreground=summary_color).pack(anchor=tk.W, pady=(5, 0))

            # Status Note
            note_frame = ttk.Frame(main_frame)
            note_frame.pack(fill=tk.X, pady=10)

            note_text = "Note: Secondary database will connect automatically when the secondary laptop comes online!"
            ttk.Label(note_frame, text=note_text,
                     font=('Arial', 10, 'italic'), foreground="blue").pack(anchor=tk.W)

            # Last Updated
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ttk.Label(main_frame, text=f"Last Updated: {current_time}",
                     font=('Arial', 9, 'italic')).pack(anchor=tk.W, pady=5)

        except Exception as e:
            error_frame = ttk.Frame(main_frame)
            error_frame.pack(fill=tk.BOTH, expand=True)
            ttk.Label(error_frame, text=f"Error refreshing database health: {e}",
                     font=('Arial', 12), foreground="red").pack(pady=20)

    def logout(self):
        """Logout current user"""
        self.current_user_id = None
        self.current_user_type = None
        self.show_login_screen()
        self.status_var.set("Logged out - Ready")

    def sort_results(self):
        """Sort the search results based on selected criteria"""
        try:
            # Get current results from treeview
            current_results = []
            for item in self.results_tree.get_children():
                values = self.results_tree.item(item)['values']
                # Parse the values back into a dict for sorting
                current_results.append({
                    'name': values[0].replace('🚨 ', '').replace('⚡ ', ''),  # Remove urgency indicators
                    'type': values[1].replace('🏢 ', '').replace('👤 ', ''),
                    'service': values[2],
                    'rating_str': values[3].replace(' ⭐', '').replace('N/A', '0'),
                    'cost_str': values[4].replace('$', '').replace('/hr 💰', '').replace('Contact for price', '999999'),
                    'source': values[5],
                    'tree_item': item
                })

            if not current_results:
                return

            # Sort based on selected option
            sort_option = self.sort_var.get()

            if sort_option == "rating_desc":
                current_results.sort(key=lambda x: float(x['rating_str']), reverse=True)
            elif sort_option == "rating_asc":
                current_results.sort(key=lambda x: float(x['rating_str']))
            elif sort_option == "price_asc":
                current_results.sort(key=lambda x: float(x['cost_str']))
            elif sort_option == "price_desc":
                current_results.sort(key=lambda x: float(x['cost_str']), reverse=True)
            elif sort_option == "available":
                # Priority to available providers
                current_results.sort(key=lambda x: 0 if 'Available' in str(x.get('availability', '')) else 1)
            elif sort_option == "name_asc":
                current_results.sort(key=lambda x: x['name'].lower())
            elif sort_option == "name_desc":
                current_results.sort(key=lambda x: x['name'].lower(), reverse=True)
            elif sort_option == "companies_first":
                current_results.sort(key=lambda x: 0 if 'Company' in x['type'] else 1)
            elif sort_option == "workers_first":
                current_results.sort(key=lambda x: 0 if 'Individual Worker' in x['type'] else 1)

            # Rebuild the treeview with sorted results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)

            for result in current_results:
                # Re-add urgency indicators if needed
                name = result['name']
                if 'emergency' in result['service'].lower() or 'urgent' in result['name'].lower():
                    name = "🚨 " + name
                elif 'high' in result['service'].lower():
                    name = "⚡ " + name

                # Re-add provider type indicators
                type_indicator = "🏢 " if 'Company' in result['type'] else "👤 "
                provider_type = type_indicator + result['type']

                # Re-add rating indicator
                rating = result['rating_str']
                if rating != '0':
                    rating_display = f"{float(rating):.1f} ⭐"
                else:
                    rating_display = "N/A"

                # Re-add cost indicator
                cost = result['cost_str']
                if cost != '999999':
                    cost_display = f"${float(cost):.0f}/hr 💰"
                else:
                    cost_display = "Contact for price"

                # Insert the sorted result
                self.results_tree.insert('', tk.END, values=(
                    name,
                    provider_type,
                    result['service'],
                    rating_display,
                    cost_display,
                    result['source']
                ))

            # Update status
            sort_names = {
                "rating_desc": "Rating (High to Low)",
                "rating_asc": "Rating (Low to High)",
                "price_asc": "Price (Low to High)",
                "price_desc": "Price (High to Low)",
                "available": "Available First",
                "name_asc": "Name (A-Z)",
                "name_desc": "Name (Z-A)",
                "companies_first": "Companies First",
                "workers_first": "Workers First"
            }

            sort_name = sort_names.get(sort_option, "Default")
            self.status_var.set(f"🔽 Results sorted by: {sort_name}")

        except Exception as e:
            messagebox.showerror("Sort Error", f"Error sorting results: {str(e)}")

    def show_search_analysis(self):
        """Show detailed search analysis with query federation insights"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Analysis", "Please enter a search term first")
            return

        self.status_var.set(f"⚙️ Analyzing Search: {search_term}...")
        self.root.update()

        try:
            # Get prompt rewrite analysis
            prompt_analysis = self.sorting_service.get_prompt_rewrite_analysis(search_term)

            # Get results integration analysis
            integration_analysis = self.sorting_service.get_results_integration_analysis(search_term)

            # Create analysis window
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("🔍 Advanced Search Analysis")
            analysis_window.geometry("800x600")
            analysis_window.configure(bg='#f0f0f0')

            # Create notebook for tabs
            notebook = ttk.Notebook(analysis_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Tab 1: Prompt Analysis
            prompt_frame = ttk.Frame(notebook)
            notebook.add(prompt_frame, text="📝 Prompt Analysis")

            prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, font=('Arial', 10))
            prompt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            prompt_content = f"""
🎯 QUERY ANALYSIS
═══════════════════════════════════════

Original Query: "{prompt_analysis.get('original_query', 'N/A')}"

🔧 REWRITTEN QUERY: "{prompt_analysis.get('rewritten_query', 'N/A')}"

📊 ANALYSIS DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Extracted Keywords: {', '.join(prompt_analysis.get('extracted_keywords', ['None']))}
• Detected Region: {prompt_analysis.get('detected_region', 'None')}
• Primary Intent: {prompt_analysis.get('primary_intent', 'general')}
• Provider Bias: {prompt_analysis.get('provider_bias', 'both')}
• Analysis Confidence: {prompt_analysis.get('analysis_confidence', 0):.1%}

🚀 IMPROVEMENTS MADE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for improvement in prompt_analysis.get('improvements', []):
                prompt_content += f"✓ {improvement}\n"

            prompt_text.insert(tk.END, prompt_content)
            prompt_text.config(state=tk.DISABLED)

            # Tab 2: Results Integration
            integration_frame = ttk.Frame(notebook)
            notebook.add(integration_frame, text="🔗 Results Integration")

            integration_text = tk.Text(integration_frame, wrap=tk.WORD, font=('Arial', 10))
            integration_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            integration_content = f"""
🎯 SEARCH INTEGRATION ANALYSIS
═══════════════════════════════════════

Query: "{integration_analysis.get('query', 'N/A')}"

📊 RESULTS SUMMARY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Results Found: {integration_analysis.get('total_results', 0)}
• Primary Database Results: {integration_analysis.get('primary_database_results', 0)}
• Secondary Database Results: {integration_analysis.get('secondary_database_results', 0)}

🎯 INTEGRATION QUALITY: {integration_analysis.get('integration_quality', 'Unknown')}

📈 DATA SOURCE BALANCE: {integration_analysis.get('data_source_balance', 'Unknown')}

🏆 TOP PROVIDERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Primary Database:
"""
            for provider in integration_analysis.get('top_providers', {}).get('primary', []):
                integration_content += f"  • {provider.get('name', 'N/A')} - Rating: {provider.get('rating', 'N/A')}\n"

            integration_content += "\nSecondary Database:\n"
            for provider in integration_analysis.get('top_providers', {}).get('secondary', []):
                integration_content += f"  • {provider.get('name', 'N/A')} - Rating: {provider.get('rating', 'N/A')}\n"

            integration_content += f"""
💡 INTEGRATION NOTES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for note in integration_analysis.get('integration_notes', []):
                integration_content += f"• {note}\n"

            integration_content += f"""
🎯 RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for rec in integration_analysis.get('recommendations', []):
                integration_content += f"• {rec}\n"

            integration_text.insert(tk.END, integration_content)
            integration_text.config(state=tk.DISABLED)

            # Status update
            self.status_var.set("✅ Analysis Complete - Advanced features ready")

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error analyzing search: {str(e)}")
            self.status_var.set("❌ Analysis failed")

    def _show_advanced_search_summary(self, results):
        """Show summary of advanced search in a small popup"""
        try:
            summary = results.get('integration_summary', {}).get('coverage', {})
            confidence = results.get('recommendation_confidence', 0)
            complexity = results.get('query_complexity', {})

            popup = tk.Toplevel(self.root)
            popup.title("🚀 Advanced Search Results")
            popup.geometry("400x250")
            popup.configure(bg='#f0f0f0')

            ttk.Label(popup, text="🔍 Advanced Search Complete",
                     font=('Arial', 14, 'bold')).pack(pady=10)

            info_frame = ttk.Frame(popup)
            info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            info_text = f"""
📊 Results Found: {summary.get('combined', 0)} total
   • Companies: {summary.get('primary_matches', 0)}
   • Individual Workers: {summary.get('secondary_matches', 0)}

🎯 Recommendation Confidence: {confidence:.1%}

📝 Query Complexity: {complexity.get('complexity_level', 'Unknown')}
   • Words: {complexity.get('word_count', 0)}
   • Location detected: {'Yes' if complexity.get('has_location_hint') else 'No'}
   • Urgency detected: {'Yes' if complexity.get('has_urgency_hint') else 'No'}

⚡ Features Used:
   ✓ Query Federation
   ✓ Prompt Rewriting
   ✓ Results Integration
   ✓ Intelligent Sorting
"""

            ttk.Label(info_frame, text=info_text, font=('Arial', 10)).pack()

            ttk.Button(popup, text="Close",
                      command=popup.destroy).pack(pady=10)

            # Auto-close after 5 seconds
            popup.after(5000, popup.destroy)

        except Exception as e:
            print(f"Error showing search summary: {e}")

def main():
    root = tk.Tk()
    app = EnhancedServiceBookingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()