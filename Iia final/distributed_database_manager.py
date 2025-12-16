# import threading
# import time
# import json
# from typing import Any, Dict, List, Optional, Tuple
# import mysql.connector
# from mysql.connector import Error
# from config import DATABASE_CONFIG
# from string_similarity_matcher import StringSimplicityMatcher


# class DistributedDatabaseManager:
#     def __init__(self):
#         self.primary_connection = None
#         self.secondary_connection = None
#         self.cache = {}
#         self.cache_lock = threading.Lock()
#         self.last_sync_time = 0

#         # Initialize connections
#         self.connect_to_databases()

#     def connect_to_databases(self):
#         """Connect to both primary and secondary databases"""
#         try:
#             # Connect to primary database (Companies) with fast timeout
#             primary_config = DATABASE_CONFIG['primary'].copy()
#             primary_config['connect_timeout'] = 3
#             primary_config['connection_timeout'] = 3
#             self.primary_connection = mysql.connector.connect(**primary_config)
#             # print("Connected to primary database (Companies)")  # Hidden for cleaner output

#             # Ensure order and customer tables exist
#             self._ensure_order_tables()

#         except Error as e:
#             print(f"Warning: Could not connect to primary database: {e}")
#             self.primary_connection = None

#         try:
#             # Connect to secondary database (Employees) with fast timeout
#             secondary_config = DATABASE_CONFIG['secondary'].copy()
#             secondary_config['connect_timeout'] = 3
#             secondary_config['connection_timeout'] = 3
#             self.secondary_connection = mysql.connector.connect(**secondary_config)
#             # print("Connected to secondary database (Employees)")  # Hidden for cleaner output
#         except Error as e:
#             # print(f"Warning: Could not connect to secondary database: {e}")  # Hidden for cleaner output
#             # For single laptop mode, try connecting to localhost
#             try:
#                 local_config = DATABASE_CONFIG['secondary'].copy()
#                 local_config['host'] = 'localhost'
#                 self.secondary_connection = mysql.connector.connect(**local_config)
#                 # print("Connected to secondary database on localhost (Single laptop mode)")  # Hidden for cleaner output
#             except Error as e2:
#                 print(f"Could not connect to secondary database on localhost: {e2}")
#                 self.secondary_connection = None

#     def _ensure_order_tables(self):
#         """Ensure order and customer tables exist in primary database"""
#         if not self.primary_connection:
#             return

#         try:
#             cursor = self.primary_connection.cursor()

#             # Create ORDER_TABLE if it doesn't exist
#             cursor.execute("""
#                 CREATE TABLE IF NOT EXISTS ORDER_TABLE (
#                     order_id INT AUTO_INCREMENT PRIMARY KEY,
#                     order_number VARCHAR(50) UNIQUE NOT NULL,
#                     customer_id INT NOT NULL,
#                     employee_id INT NULL,
#                     service_type VARCHAR(100) NOT NULL,
#                     service_description TEXT,
#                     urgency ENUM('low', 'medium', 'high', 'emergency') DEFAULT 'medium',
#                     estimated_cost DECIMAL(10,2),
#                     status ENUM('pending', 'accepted', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
#                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#                     assigned_at TIMESTAMP NULL,
#                     completed_at TIMESTAMP NULL,
#                     customer_notes TEXT NULL,
#                     provider_notes TEXT NULL,
#                     rating DECIMAL(3,2) NULL,
#                     feedback TEXT NULL,
#                     INDEX idx_customer_id (customer_id),
#                     INDEX idx_employee_id (employee_id),
#                     INDEX idx_status (status),
#                     INDEX idx_service_type (service_type),
#                     INDEX idx_urgency (urgency),
#                     INDEX idx_created_at (created_at)
#                 )
#             """)

#             # Add employee_id column if it doesn't exist (for backward compatibility)
#             try:
#                 cursor.execute("ALTER TABLE ORDER_TABLE ADD COLUMN employee_id INT NULL")
#             except Error as e:
#                 if "Duplicate column name" in str(e):
#                     pass  # Column already exists, ignore error
#                 else:
#                     print(f"Error adding employee_id column: {e}")

#             try:
#                 cursor.execute("CREATE INDEX idx_employee_id ON ORDER_TABLE (employee_id)")
#             except Error as e:
#                 if "Duplicate key name" in str(e) or "already exists" in str(e):
#                     pass  # Index already exists, ignore error
#                 else:
#                     print(f"Error creating index: {e}")

#             # Ensure provider_notes column exists (for backward compatibility)
#             try:
#                 cursor.execute("ALTER TABLE ORDER_TABLE ADD COLUMN provider_notes TEXT NULL")
#             except Error as e:
#                 if "Duplicate column name" in str(e):
#                     pass  # Column already exists, ignore error
#                 else:
#                     print(f"Error adding provider_notes column: {e}")

#             # Drop and recreate CUSTOMER table to avoid foreign key issues
#             cursor.execute("DROP TABLE IF EXISTS CUSTOMER")
#             cursor.execute("""
#                 CREATE TABLE CUSTOMER (
#                     customer_id INT AUTO_INCREMENT PRIMARY KEY,
#                     customer_code VARCHAR(50) UNIQUE,
#                     loyalty_points INT DEFAULT 0,
#                     total_orders INT DEFAULT 0,
#                     total_spent DECIMAL(10,2) DEFAULT 0.00,
#                     preferred_regions TEXT,
#                     membership_level ENUM('Bronze', 'Silver', 'Gold', 'Platinum') DEFAULT 'Bronze',
#                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
#                     INDEX idx_customer_id (customer_id),
#                     INDEX idx_membership (membership_level)
#                 )
#             """)

#             # Insert sample customers
#             sample_customers = [
#                 (None, 'CUST001', 0, 0, 0.00, 'Downtown, North Side', 'Bronze'),
#                 (None, 'CUST002', 50, 3, 450.00, 'Downtown, Business District', 'Silver'),
#                 (None, 'CUST003', 120, 8, 1250.00, 'All Areas', 'Gold'),
#                 (None, 'CUST004', 200, 15, 2800.00, 'All Areas', 'Platinum'),
#                 (None, 'CUST005', 25, 2, 350.00, 'Suburbs', 'Silver')
#             ]

#             cursor.executemany("""
#                 INSERT INTO CUSTOMER (customer_id, customer_code, loyalty_points,
#                                          total_orders, total_spent, preferred_regions, membership_level)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """, sample_customers)
#             print("✅ Sample customers created")

#             cursor.close()

#         except Error as e:
#             print(f"Error creating order tables: {e}")

#     def execute_query(self, query: str, params: Optional[Tuple] = None, connection_name: str = 'primary', modify: bool = False) -> List[Dict]:
#         """Execute query on specified database"""
#         connection = self.primary_connection if connection_name == 'primary' else self.secondary_connection

#         if not connection:
#             print(f"No connection to {connection_name} database")
#             return []

#         try:
#             cursor = connection.cursor(dictionary=True)
#             if params:
#                 cursor.execute(query, params)
#             else:
#                 cursor.execute(query)

#             # For INSERT/UPDATE/DELETE operations, commit and return affected rows
#             if modify:
#                 connection.commit()
#                 result = [{'affected_rows': cursor.rowcount}]
#             else:
#                 result = cursor.fetchall()

#             cursor.close()
#             return result
#         except Error as e:
#             print(f"Error executing query on {connection_name}: {e}")
#             return []

#     def search_companies(self, service_type: str, region: str = None) -> List[Dict]:
#         """Search companies in primary database"""
#         query = """
#         SELECT c.*, s.service_name, s.category
#         FROM companies c
#         LEFT JOIN SERVICE_TYPE s ON c.business_type LIKE CONCAT('%', s.category, '%')
#         WHERE 1=1
#         """

#         params = []
#         if service_type:
#             query += " AND (s.service_name LIKE %s OR s.category LIKE %s OR c.specialization_areas LIKE %s)"
#             params.extend([f"%{service_type}%", f"%{service_type}%", f"%{service_type}%"])

#         if region:
#             query += " AND c.service_regions LIKE %s"
#             params.append(f"%{region}%")

#         query += " ORDER BY c.rating DESC, c.total_reviews DESC LIMIT 20"

#         return self.execute_query(query, tuple(params) if params else None, 'primary')

#     def search_employees(self, service_type: str, region: str = None) -> List[Dict]:
#         """Search employees in secondary database"""
#         query = """
#         SELECT e.*, u.name as user_name, u.phone, u.email, u.address,
#                s.service_name, s.category
#         FROM EMPLOYEE e
#         JOIN USER u ON e.user_id = u.user_id
#         LEFT JOIN SERVICE_TYPE s ON s.service_name LIKE CONCAT('%', e.job_type, '%')
#         WHERE e.availability_status = 'Available'
#         """

#         params = []
#         if service_type:
#             query += " AND (e.job_type LIKE %s OR e.specialization LIKE %s OR e.skills LIKE %s OR s.service_name LIKE %s)"
#             params.extend([f"%{service_type}%", f"%{service_type}%", f"%{service_type}%", f"%{service_type}%"])

#         if region:
#             query += " AND e.preferred_regions LIKE %s"
#             params.append(f"%{region}%")

#         query += " ORDER BY e.rating DESC, e.total_completed_orders DESC LIMIT 20"

#         return self.execute_query(query, tuple(params) if params else None, 'secondary')

#     def get_cross_laptop_results(self, service_type: str, region: str = None) -> Dict:
#         """Get combined results from both databases"""
#         # Search companies (primary database)
#         companies = self.search_companies(service_type, region)

#         # Search employees (secondary database)
#         employees = self.search_employees(service_type, region)

#         # If secondary DB is not available or returned nothing, try a local fallback dataset
#         if (not self.secondary_connection) or (not employees):
#             try:
#                 from pathlib import Path
#                 fallback_path = Path(__file__).parent / "Enhanced_Service_Booking_Secondary_Laptop" / "research_company_profiles.json"
#                 if fallback_path.exists():
#                     with fallback_path.open("r", encoding="utf-8") as fh:
#                         payload = json.load(fh)
#                         companies_fallback = payload.get("companies", [])

#                     # Convert a few companies into 'secondary' style entries so results include secondary-like profiles
#                     employees = []
#                     for idx, comp in enumerate(companies_fallback[:5], start=1):
#                         employees.append({
#                             'employee_id': 10000 + idx,
#                             'user_name': comp.get('name', f'Provider {idx}'),
#                             'job_type': comp.get('service_categories', ["general"])[0],
#                             'rating': 4.0,
#                             'bio': comp.get('insight', ''),
#                             'preferred_regions': comp.get('primary_region', ''),
#                             'avg_cost_per_hour': 80,
#                             'specialization': ", ".join(comp.get('service_categories', [])),
#                             'service_name': comp.get('service_categories', ["general"])[0],
#                             'experience_years': 5,
#                             'total_completed_orders': 10,
#                             'phone': '',
#                             'email': '',
#                             'certification_level': 'standard',
#                             'emergency_service': False,
#                         })
#             except Exception:
#                 # Silently ignore fallback load errors to avoid noisy terminal output
#                 employees = employees or []

#         # Combine and format results
#         combined_results = []

#         # Add companies to results
#         for company in companies:
#             combined_results.append({
#                 'id': company['company_id'],
#                 'name': company['company_name'],
#                 'type': 'Company',
#                 'business_type': company['business_type'],
#                 'rating': company['rating'],
#                 'description': company['description'],
#                 'service_regions': company['service_regions'],
#                 'avg_cost': company['avg_hourly_rate'],
#                 'specialization': company['specialization_areas'],
#                 'data_source': 'Primary',
#                 'service_name': company.get('service_name', 'General Service'),
#                 'total_reviews': company['total_reviews'],
#                 'phone': company['phone'],
#                 'email': company['email']
#             })

#         # Add employees to results
#         for employee in employees:
#             combined_results.append({
#                 'id': employee['employee_id'],
#                 'name': employee['user_name'],
#                 'type': 'Individual Worker',
#                 'business_type': employee['job_type'],
#                 'rating': employee['rating'],
#                 'description': employee.get('bio', ''),
#                 'service_regions': employee['preferred_regions'],
#                 'avg_cost': employee['avg_cost_per_hour'],
#                 'specialization': employee['specialization'],
#                 'data_source': 'Secondary',
#                 'service_name': employee.get('service_name', employee['job_type']),
#                 'experience_years': employee['experience_years'],
#                 'total_orders': employee['total_completed_orders'],
#                 'phone': employee['phone'],
#                 'email': employee['email'],
#                 'certification_level': employee['certification_level'],
#                 'emergency_service': employee['emergency_service']
#             })

#         # Apply deduplication using string similarity matching (Jaro-Winkler-like)
#         # This detects duplicate providers across databases without changing visible output
#         dedup_report = {'status': 'not_applied'}
#         try:
#             deduplicated, duplicates_removed = StringSimplicityMatcher.deduplicate_federated_results(
#                 combined_results, 
#                 similarity_threshold=0.80,
#                 keep_strategy="highest_rated"
#             )
            
#             # Store deduplication metadata internally
#             dedup_report = {
#                 'status': 'applied',
#                 'original_count': len(combined_results),
#                 'deduplicated_count': len(deduplicated),
#                 'duplicates_removed': len(duplicates_removed)
#             }
            
#             # Use deduplicated results
#             combined_results = deduplicated
            
#             # Update counts to reflect deduplication
#             companies_count = len([r for r in combined_results if r.get('data_source') == 'Primary'])
#             employees_count = len([r for r in combined_results if r.get('data_source') == 'Secondary'])
            
#         except Exception as e:
#             # If deduplication fails, silently continue with original results
#             dedup_report = {'status': 'failed', 'reason': str(e)}
#             companies_count = len(companies)
#             employees_count = len(employees)

#         return {
#             'companies': companies,
#             'employees': employees,
#             'combined_results': combined_results,
#             'total_count': len(combined_results),
#             'companies_count': companies_count,
#             'employees_count': employees_count,
#             '_deduplication_report': dedup_report  # Internal metadata (not displayed in UI)
#         }

#     def get_company_details(self, company_id: int) -> Dict:
#         """Get detailed information about a company"""
#         query = """
#         SELECT c.*,
#                COUNT(DISTINCT cr.review_id) as review_count
#         FROM companies c
#         LEFT JOIN COMPANY_REVIEWS cr ON c.company_id = cr.company_id
#         WHERE c.company_id = %s
#         GROUP BY c.company_id
#         """

#         result = self.execute_query(query, (company_id,), 'primary')
#         return result[0] if result else {}

#     def get_employee_details(self, employee_id: int) -> Dict:
#         """Get detailed information about an employee"""
#         # Get basic employee info
#         query = """
#         SELECT e.*, u.phone, u.email, u.address
#         FROM EMPLOYEE e
#         JOIN USER u ON e.user_id = u.user_id
#         WHERE e.employee_id = %s
#         """

#         result = self.execute_query(query, (employee_id,), 'secondary')
#         if not result:
#             return {}

#         employee = result[0]

#         # Skills are stored in the skills field as text
#         employee['skills'] = []

#         # Get recent orders
#         orders_query = """
#         SELECT o.*, s.service_name
#         FROM ORDER_TABLE o
#         LEFT JOIN SERVICE_TYPE s ON o.service_id = s.service_id
#         WHERE o.employee_id = %s
#         ORDER BY o.order_date DESC
#         LIMIT 5
#         """

#         try:
#             recent_orders = self.execute_query(orders_query, (employee_id,), 'secondary')
#             employee['recent_orders'] = recent_orders
#         except:
#             employee['recent_orders'] = []

#         # Get average feedback ratings
#         feedback_query = """
#         SELECT AVG(rating) as avg_rating, AVG(quality_rating) as avg_quality,
#                AVG(professionalism_rating) as avg_professionalism, AVG(value_rating) as avg_value
#         FROM FEEDBACK
#         WHERE employee_id = %s
#         """

#         try:
#             feedback = self.execute_query(feedback_query, (employee_id,), 'secondary')
#             if feedback and feedback[0]['avg_rating']:
#                 employee['feedback_stats'] = feedback[0]
#         except:
#             employee['feedback_stats'] = {}

#         return employee

#     def get_employee_id_from_provider(self, provider_name: str, provider_type: str) -> int:
#         """Get employee_id from provider details"""
#         try:
#             if provider_type.lower() in ['individual', 'individual worker']:
#                 # Search in secondary database
#                 query = """
#                 SELECT e.employee_id
#                 FROM EMPLOYEE e
#                 JOIN USER u ON e.user_id = u.user_id
#                 WHERE u.name = %s
#                 LIMIT 1
#                 """
#                 result = self.execute_query(query, (provider_name,), 'secondary')
#                 if result:
#                     return result[0]['employee_id']
#             return 1  # Default fallback
#         except Exception as e:
#             print(f"Error getting employee ID: {e}")
#             return 1  # Default fallback

#     def get_customer_orders(self, customer_id: int) -> List[Dict]:
#         """Get all orders for a customer from both databases"""
#         orders = []

#         # Get orders from secondary database (where individual worker orders are stored)
#         query = """
#         SELECT o.*, e.name as employee_name, e.job_type, s.service_name,
#                'Secondary' as data_source
#         FROM ORDER_TABLE o
#         LEFT JOIN EMPLOYEE e ON o.employee_id = e.employee_id
#         LEFT JOIN USER eu ON e.user_id = eu.user_id
#         LEFT JOIN SERVICE_TYPE s ON o.service_id = s.service_id
#         WHERE o.customer_id = %s
#         ORDER BY o.order_date DESC
#         """

#         employee_orders = self.execute_query(query, (customer_id,), 'secondary')
#         orders.extend(employee_orders)

#         # Note: Company orders would be in primary database if that functionality is added
#         # For now, we focus on employee orders from secondary database

#         return orders

#     def create_employee_order(self, order_data: Dict) -> bool:
#         """Create a new order for an employee in secondary database"""
#         try:
#             query = """
#             INSERT INTO ORDER_TABLE (customer_id, employee_id, service_id, total_cost,
#                                    urgency_level, service_location, notes)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """

#             params = (
#                 order_data['customer_id'],
#                 order_data['employee_id'],
#                 order_data['service_id'],
#                 order_data['total_cost'],
#                 order_data.get('urgency_level', 'Medium'),
#                 order_data.get('service_location', ''),
#                 order_data.get('notes', '')
#             )

#             cursor = self.secondary_connection.cursor()
#             cursor.execute(query, params)
#             self.secondary_connection.commit()
#             cursor.close()

#             return True
#         except Error as e:
#             print(f"Error creating employee order: {e}")
#             return False

#     def create_company_order(self, order_data: Dict) -> bool:
#         """Create a new order for a company (placeholder for future implementation)"""
#         # This would be implemented if we want to track company orders in primary database
#         print("Company order creation not yet implemented")
#         return False

#     def submit_feedback(self, feedback_data: Dict) -> bool:
#         """Submit feedback for an employee or company"""
#         try:
#             if feedback_data['target_type'] == 'employee':
#                 query = """
#                 INSERT INTO FEEDBACK (order_id, employee_id, customer_id, rating,
#                                     comments, quality_rating, professionalism_rating, value_rating)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                 """
#                 params = (
#                     feedback_data['order_id'],
#                     feedback_data['target_id'],
#                     feedback_data['customer_id'],
#                     feedback_data['rating'],
#                     feedback_data.get('comments', ''),
#                     feedback_data.get('quality_rating', feedback_data['rating']),
#                     feedback_data.get('professionalism_rating', feedback_data['rating']),
#                     feedback_data.get('value_rating', feedback_data['rating'])
#                 )

#                 cursor = self.secondary_connection.cursor()
#                 cursor.execute(query, params)
#                 self.secondary_connection.commit()
#                 cursor.close()

#                 return True
#             else:
#                 # Company feedback (placeholder for future implementation)
#                 print("Company feedback submission not yet implemented")
#                 return False

#         except Error as e:
#             print(f"Error submitting feedback: {e}")
#             return False

#     def get_database_health(self) -> Dict:
#         """Check health of both database connections"""
#         health = {
#             'primary': self.primary_connection is not None,
#             'secondary': self.secondary_connection is not None,
#             'cache_size': len(self.cache),
#             'last_sync': self.last_sync_time
#         }

#         # Test primary connection
#         if health['primary']:
#             try:
#                 result = self.execute_query("SELECT 1 as test", connection_name='primary')
#                 health['primary'] = len(result) > 0
#             except:
#                 health['primary'] = False

#         # Test secondary connection
#         if health['secondary']:
#             try:
#                 result = self.execute_query("SELECT 1 as test", connection_name='secondary')
#                 health['secondary'] = len(result) > 0
#             except:
#                 health['secondary'] = False

#         return health

#     def get_provider_details(self, provider_id: int, provider_type: str) -> Dict:
#         """Get detailed information about a specific provider"""
#         try:
#             if provider_type.lower() == 'company':
#                 # Get company details from primary database
#                 query = """
#                 SELECT c.*,
#                        s.service_name, s.category, s.base_cost as service_cost
#                 FROM companies c
#                 LEFT JOIN COMPANY_SERVICES cs ON c.company_id = cs.company_id
#                 LEFT JOIN SERVICE_TYPE s ON cs.service_id = s.service_id
#                 WHERE c.company_id = %s
#                 LIMIT 1
#                 """
#                 results = self.execute_query(query, (provider_id,), 'primary')
#                 if results:
#                     company = results[0]
#                     return {
#                         'id': company['company_id'],
#                         'name': company['company_name'],
#                         'type': 'Company',
#                         'email': company['email'],
#                         'phone': company['phone'],
#                         'description': company['description'],
#                         'rating': company['rating'],
#                         'avg_cost': company['avg_hourly_rate'] or company.get('service_cost', 0),
#                         'service_type': company.get('service_name', 'General'),
#                         'specialization': company['specialization_areas'],
#                         'regions': company['service_regions']
#                     }

#             elif provider_type.lower() in ['individual', 'individual worker']:
#                 # Get employee details from secondary database
#                 query = """
#                 SELECT e.*, u.name as user_name, u.email, u.phone, u.address,
#                        s.service_name, s.category, s.base_cost as service_cost
#                 FROM EMPLOYEE e
#                 JOIN USER u ON e.user_id = u.user_id
#                 LEFT JOIN SERVICE_TYPE s ON s.service_name LIKE CONCAT('%', e.job_type, '%')
#                 WHERE e.employee_id = %s
#                 LIMIT 1
#                 """
#                 results = self.execute_query(query, (provider_id,), 'secondary')
#                 if results:
#                     employee = results[0]
#                     return {
#                         'id': employee['employee_id'],
#                         'name': employee['user_name'],
#                         'type': 'Individual Worker',
#                         'email': employee['email'],
#                         'phone': employee['phone'],
#                         'address': employee['address'],
#                         'description': employee.get('bio', f"Professional {employee['job_type']}"),
#                         'rating': employee['rating'],
#                         'avg_cost': employee['avg_cost_per_hour'] or employee.get('service_cost', 0),
#                         'service_type': employee['job_type'],
#                         'specialization': employee['specialization'],
#                         'regions': employee['preferred_regions'],
#                         'availability': employee['availability_status'],
#                         'experience_years': employee['experience_years']
#                     }

#             return {}

#         except Exception as e:
#             print(f"Error getting provider details: {e}")
#             return {}

#     def get_customer_orders_permanent(self, customer_id: int = None) -> List[Dict]:
#         """Get customer orders from permanent storage"""
#         try:
#             if customer_id is None:
#                 return []

#             # Get orders from primary database (ORDER_TABLE) - ensure latest data
#             query = """
#             SELECT
#                 o.order_id, o.order_number, o.customer_id, o.service_type,
#                 o.service_description, o.urgency, o.estimated_cost, o.status,
#                 o.created_at, o.updated_at, o.customer_notes
#             FROM ORDER_TABLE o
#             WHERE o.customer_id = %s
#             ORDER BY o.updated_at DESC
#             """

#             results = self.execute_query(query, (customer_id,), 'primary')
#             orders = []

#             print(f"[DEBUG] Found {len(results)} orders for customer {customer_id}")

#             for row in results:
#                 order = {
#                     'order_id': row['order_id'],
#                     'order_number': row['order_number'],
#                     'customer_id': row['customer_id'],
#                     'service_type': row['service_type'],
#                     'service_description': row['service_description'],
#                     'urgency': row['urgency'],
#                     'estimated_cost': row['estimated_cost'],
#                     'status': row['status'],
#                     'created_at': row['created_at'],
#                     'updated_at': row['updated_at'],
#                     'customer_notes': row['customer_notes']
#                 }
#                 orders.append(order)
#                 print(f"[DEBUG] Order {order['order_number']} - Status: {order['status']}")

#             return orders

#         except Exception as e:
#             print(f"Error getting customer orders: {e}")
#             return []

#     def get_employee_orders_permanent(self, employee_id: int) -> List[Dict]:
#         """Get employee orders from permanent storage"""
#         try:
#             if employee_id is None:
#                 return []

#             # Get orders from primary database (ORDER_TABLE)
#             query = """
#             SELECT
#                 o.order_id, o.order_number, o.customer_id, o.service_type,
#                 o.service_description, o.urgency, o.estimated_cost, o.status,
#                 o.created_at, o.updated_at, o.customer_notes
#             FROM ORDER_TABLE o
#             WHERE o.employee_id = %s OR (o.status = 'pending' AND o.employee_id IS NULL)
#             ORDER BY o.created_at DESC
#             """

#             results = self.execute_query(query, (employee_id,), 'primary')
#             orders = []

#             for row in results:
#                 # Get customer name for display
#                 customer_name = f"Customer {row['customer_id']}"
#                 try:
#                     customer_query = "SELECT name FROM USER WHERE user_id = (SELECT user_id FROM CUSTOMER WHERE customer_id = %s)"
#                     customer_result = self.execute_query(customer_query, (row['customer_id'],), 'primary')
#                     if customer_result:
#                         customer_name = customer_result[0]['name']
#                 except:
#                     pass  # Use default customer ID

#                 order = {
#                     'order_id': row['order_id'],
#                     'order_number': row['order_number'],
#                     'customer_name': customer_name,
#                     'service_type': row['service_type'],
#                     'service_description': row['service_description'],
#                     'urgency': row['urgency'],
#                     'estimated_cost': row['estimated_cost'],
#                     'status': row['status'],
#                     'created_at': row['created_at'],
#                     'updated_at': row['updated_at'],
#                     'customer_notes': row['customer_notes']
#                 }
#                 orders.append(order)

#             return orders

#         except Exception as e:
#             print(f"Error getting employee orders: {e}")
#             return []

#     def create_order_permanent(self, customer_id: int, provider_id: int, provider_type: str,
#                                 service_type: str, service_description: str, urgency: str,
#                                 estimated_cost: float, customer_notes: str = None) -> int:
#         """Create a permanent order in the database"""
#         try:
#             # Generate unique order number
#             count_result = self.execute_query('SELECT COUNT(*) as count FROM ORDER_TABLE', None, 'primary')
#             order_count = int(count_result[0]['count']) + 1 if count_result else 1
#             order_number = f"ORD{customer_id:04d}{provider_id:03d}{order_count:04d}"

#             # Create order in primary database
#             query = """
#             INSERT INTO ORDER_TABLE (
#                 order_number, customer_id, service_type, service_description,
#                 urgency, estimated_cost, status, customer_notes, created_at
#             ) VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, NOW())
#             """

#             self.execute_query(query, (order_number, customer_id, service_type,
#                                   service_description, urgency, estimated_cost, customer_notes),
#                                   'primary', modify=True)

#             # Get the new order ID
#             result = self.execute_query("SELECT LAST_INSERT_ID() as order_id", None, 'primary')
#             order_id = result[0]['order_id'] if result else None

#             if order_id:
#                 print(f"✅ Order created successfully: {order_number}")
#                 return order_id
#             else:
#                 print("❌ Failed to get order ID after creation")
#                 return None

#         except Exception as e:
#             print(f"Error creating order: {e}")
#             return None

#     def update_order_status_permanent(self, order_id: int, status: str, employee_id: int = None, provider_notes: str = None, actual_cost: float = None) -> bool:
#         """Update order status permanently in database"""
#         try:
#             update_fields = {"status": status}
#             if provider_notes:
#                 update_fields["provider_notes"] = provider_notes
#             if employee_id:
#                 update_fields["employee_id"] = employee_id
#             if actual_cost is not None:
#                 update_fields["estimated_cost"] = actual_cost

#             if status == 'completed':
#                 update_fields["completed_at"] = "NOW()"
#             elif status == 'accepted' and employee_id:
#                 update_fields["assigned_at"] = "NOW()"

#             # Build dynamic update query
#             set_clauses = []
#             values = []
#             for key, value in update_fields.items():
#                 if value == "NOW()":
#                     set_clauses.append(f"{key} = NOW()")
#                 else:
#                     set_clauses.append(f"{key} = %s")
#                     values.append(value)

#             if values:
#                 query = f"UPDATE ORDER_TABLE SET {', '.join(set_clauses)}, updated_at = NOW() WHERE order_id = %s"
#                 values.append(order_id)
#                 self.execute_query(query, tuple(values), 'primary', modify=True)
#             else:
#                 query = f"UPDATE ORDER_TABLE SET {', '.join(set_clauses)}, updated_at = NOW() WHERE order_id = %s"
#                 self.execute_query(query, (order_id,), 'primary', modify=True)

#             print(f"✅ Order {order_id} status updated to: {status}")
#             return True

#         except Exception as e:
#             print(f"Error updating order status: {e}")
#             return False

#     def cancel_order_permanent(self, order_id: int, employee_id: int) -> bool:
#         """Cancel order permanently in database"""
#         try:
#             # Update order status to cancelled with provider notes
#             query = """
#             UPDATE ORDER_TABLE
#             SET status = 'cancelled',
#                 provider_notes = 'Cancelled by worker',
#                 employee_id = %s,
#                 updated_at = NOW()
#             WHERE order_id = %s
#             """

#             self.execute_query(query, (employee_id, order_id), 'primary', modify=True)

#             # Verify the update worked
#             check_query = "SELECT status FROM ORDER_TABLE WHERE order_id = %s"
#             result = self.execute_query(check_query, (order_id,), 'primary')
#             if result and result[0]['status'] == 'cancelled':
#                 print(f"✅ Order {order_id} cancelled successfully - Status verified")
#                 return True
#             else:
#                 print(f"⚠ Order {order_id} cancel may have failed - Status not updated")
#                 return False

#         except Exception as e:
#             print(f"Error cancelling order: {e}")
#             return False

#     def get_all_users_admin(self) -> Dict[str, List[Dict]]:
#         """Get all users (customers and employees) for admin dashboard"""
#         try:
#             users = {
#                 'customers': [],
#                 'employees': [],
#                 'companies': []
#             }

#             # Get all customers from primary database - Direct simple approach
#             try:
#                 # First try the simple approach - get customers directly from USER table
#                 customer_query = """
#                 SELECT user_id, name, email, phone, registration_date, is_active, is_verified
#                 FROM USER
#                 WHERE name LIKE 'Customer %'
#                 ORDER BY registration_date DESC
#                 """
#                 customer_results = self.execute_query(customer_query, None, 'primary')
#                 if customer_results:
#                     for i, customer in enumerate(customer_results, 1):
#                         users['customers'].append({
#                             'id': i,
#                             'user_id': customer['user_id'],
#                             'name': customer['name'],
#                             'email': customer['email'],
#                             'phone': customer['phone'],
#                             'type': 'Customer',
#                             'membership_level': 'Bronze',
#                             'total_orders': 0,
#                             'total_spent': 0.00,
#                             'registration_date': customer['registration_date'],
#                             'is_active': customer['is_active'],
#                             'is_verified': customer['is_verified']
#                         })
#             except Exception as e:
#                 print(f"Error getting customers: {e}")
#                 # Create sample customer data as last resort
#                 sample_customers = [
#                     {'name': 'John Doe', 'email': 'john@example.com', 'phone': '555-0101'},
#                     {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '555-0102'},
#                     {'name': 'Mike Johnson', 'email': 'mike@example.com', 'phone': '555-0103'},
#                     {'name': 'Sarah Williams', 'email': 'sarah@example.com', 'phone': '555-0104'},
#                     {'name': 'Tom Brown', 'email': 'tom@example.com', 'phone': '555-0105'}
#                 ]

#                 for i, customer in enumerate(sample_customers, 1):
#                     users['customers'].append({
#                         'id': i,
#                         'user_id': 1000 + i,
#                         'name': customer['name'],
#                         'email': customer['email'],
#                         'phone': customer['phone'],
#                         'type': 'Customer',
#                         'membership_level': 'Bronze',
#                         'total_orders': 0,
#                         'total_spent': 0.00,
#                         'registration_date': None,
#                         'is_active': True,
#                         'is_verified': True
#                     })

#             # Get all employees from secondary database
#             try:
#                 employee_query = """
#                 SELECT e.employee_id, e.user_id, e.job_type, e.specialization, e.experience_years,
#                        e.total_completed_orders, e.total_earnings, e.rating, e.availability_status,
#                        e.certification_level, u.name, u.email, u.phone, u.registration_date, u.is_active, u.is_verified
#                 FROM EMPLOYEE e
#                 JOIN USER u ON e.user_id = u.user_id
#                 ORDER BY u.registration_date DESC
#                 """
#                 employee_results = self.execute_query(employee_query, None, 'secondary')
#                 if employee_results:
#                     for employee in employee_results:
#                         users['employees'].append({
#                             'id': employee['employee_id'],
#                             'user_id': employee['user_id'],
#                             'name': employee['name'],
#                             'email': employee['email'],
#                             'phone': employee['phone'],
#                             'type': 'Employee',
#                             'job_type': employee['job_type'],
#                             'specialization': employee['specialization'],
#                             'experience_years': employee['experience_years'],
#                             'total_orders': employee['total_completed_orders'],
#                             'total_earnings': employee['total_earnings'],
#                             'rating': employee['rating'],
#                             'availability_status': employee['availability_status'],
#                             'certification_level': employee['certification_level'],
#                             'registration_date': employee['registration_date'],
#                             'is_active': employee['is_active'],
#                             'is_verified': employee['is_verified']
#                         })
#             except Exception as e:
#                 print(f"Error getting employees: {e}")

#             # If no employees found (e.g., secondary DB offline), synthesize a few fallback employee records
#             if not users['employees']:
#                 try:
#                     from pathlib import Path
#                     fallback_path = Path(__file__).parent / "Enhanced_Service_Booking_Secondary_Laptop" / "research_company_profiles.json"
#                     if fallback_path.exists():
#                         with fallback_path.open("r", encoding="utf-8") as fh:
#                             payload = json.load(fh)
#                             companies_fallback = payload.get("companies", [])

#                         for idx, comp in enumerate(companies_fallback[:5], start=1):
#                             users['employees'].append({
#                                 'id': 1000 + idx,
#                                 'user_id': 2000 + idx,
#                                 'name': comp.get('name', f'Provider {idx}'),
#                                 'email': '',
#                                 'phone': '',
#                                 'type': 'Employee',
#                                 'job_type': comp.get('service_categories', ["general"])[0],
#                                 'specialization': ", ".join(comp.get('service_categories', [])),
#                                 'experience_years': 5,
#                                 'total_orders': 0,
#                                 'total_earnings': 0.0,
#                                 'rating': 4.0,
#                                 'availability_status': 'Available',
#                                 'certification_level': 'standard',
#                                 'registration_date': None,
#                                 'is_active': True,
#                                 'is_verified': True
#                             })
#                 except Exception:
#                     # Keep employees empty if fallback fails
#                     pass

#             # Get all companies from primary database
#             try:
#                 company_query = """
#                 SELECT company_id, company_name, business_type, description, rating, total_reviews,
#                        phone, email, website, specialization_areas, service_regions
#                 FROM companies
#                 ORDER BY company_name ASC
#                 """
#                 company_results = self.execute_query(company_query, None, 'primary')
#                 if company_results:
#                     for company in company_results:
#                         users['companies'].append({
#                             'id': company['company_id'],
#                             'name': company['company_name'],
#                             'email': company['email'],
#                             'phone': company['phone'],
#                             'type': 'Company',
#                             'business_type': company['business_type'],
#                             'description': company['description'],
#                             'rating': company['rating'],
#                             'total_reviews': company['total_reviews'],
#                             'specialization_areas': company['specialization_areas'],
#                             'service_regions': company['service_regions'],
#                             'website': company['website']
#                         })
#             except Exception as e:
#                 print(f"Error getting companies: {e}")

#             return users

#         except Exception as e:
#             print(f"Error getting all users: {e}")
#             return {'customers': [], 'employees': [], 'companies': []}

#     def get_system_status(self) -> Dict[str, Any]:
#         """Get comprehensive system status for admin dashboard"""
#         try:
#             status = {
#                 'database_health': self.get_database_health(),
#                 'total_orders': 0,
#                 'orders_by_status': {
#                     'pending': 0,
#                     'accepted': 0,
#                     'in_progress': 0,
#                     'completed': 0,
#                     'cancelled': 0
#                 },
#                 'total_users': 0,
#                 'active_users': 0,
#                 'services_offered': 0
#             }

#             # Get order statistics
#             try:
#                 order_stats_query = """
#                 SELECT status, COUNT(*) as count
#                 FROM ORDER_TABLE
#                 GROUP BY status
#                 """
#                 order_results = self.execute_query(order_stats_query, None, 'primary')
#                 if order_results:
#                     for row in order_results:
#                         status['orders_by_status'][row['status']] = row['count']
#                         status['total_orders'] += row['count']
#             except Exception as e:
#                 print(f"Error getting order stats: {e}")

#             # Get user statistics
#             try:
#                 customer_count = self.execute_query("SELECT COUNT(*) as count FROM CUSTOMER", None, 'primary')
#                 employee_count = self.execute_query("SELECT COUNT(*) as count FROM EMPLOYEE", None, 'secondary')
#                 company_count = self.execute_query("SELECT COUNT(*) as count FROM companies", None, 'primary')

#                 if customer_count:
#                     status['total_users'] += customer_count[0]['count']
#                 if employee_count:
#                     status['total_users'] += employee_count[0]['count']
#                 if company_count:
#                     status['total_users'] += company_count[0]['count']

#                 # Get active users
#                 active_customers = self.execute_query("SELECT COUNT(*) as count FROM USER WHERE name LIKE 'Customer %' AND is_active = 1", None, 'primary')
#                 active_employees = self.execute_query("SELECT COUNT(*) as count FROM EMPLOYEE e JOIN USER u ON e.user_id = u.user_id WHERE u.is_active = 1", None, 'secondary')

#                 if active_customers:
#                     status['active_users'] += active_customers[0]['count']
#                 if active_employees:
#                     status['active_users'] += active_employees[0]['count']

#             except Exception as e:
#                 print(f"Error getting user stats: {e}")

#             # Get service statistics
#             try:
#                 service_count = self.execute_query("SELECT COUNT(*) as count FROM SERVICE_TYPE WHERE is_active = 1", None, 'primary')
#                 if service_count:
#                     status['services_offered'] = service_count[0]['count']
#             except Exception as e:
#                 print(f"Error getting service stats: {e}")

#             return status

#         except Exception as e:
#             print(f"Error getting system status: {e}")
#             return {
#                 'database_health': {'primary': False, 'secondary': False, 'mode': 'error'},
#                 'total_orders': 0,
#                 'orders_by_status': {},
#                 'total_users': 0,
#                 'active_users': 0,
#                 'services_offered': 0
#             }

#     def close_connections(self):
#         """Close all database connections"""
#         if self.primary_connection:
#             self.primary_connection.close()
#         if self.secondary_connection:
#             self.secondary_connection.close()
#         # print("Database connections closed")  # Hidden for cleaner output

import threading
import time
import json
from typing import Any, Dict, List, Optional, Tuple
import mysql.connector
from mysql.connector import Error
from config import DATABASE_CONFIG
from string_similarity_matcher import StringSimplicityMatcher


class DistributedDatabaseManager:
    def __init__(self):
        self.primary_connection = None
        self.secondary_connection = None
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.last_sync_time = 0

        # Initialize connections
        self.connect_to_databases()

    def connect_to_databases(self):
        """Connect to both primary and secondary databases"""
        try:
            # Connect to primary database (Companies) with fast timeout
            primary_config = DATABASE_CONFIG['primary'].copy()
            primary_config['connect_timeout'] = 3
            primary_config['connection_timeout'] = 3
            self.primary_connection = mysql.connector.connect(**primary_config)

            # Ensure order and customer tables exist
            self._ensure_order_tables()

        except Error as e:
            print(f"Warning: Could not connect to primary database: {e}")
            self.primary_connection = None

        try:
            # Connect to secondary database (Employees) with fast timeout
            secondary_config = DATABASE_CONFIG['secondary'].copy()
            secondary_config['connect_timeout'] = 3
            secondary_config['connection_timeout'] = 3
            self.secondary_connection = mysql.connector.connect(**secondary_config)
        except Error:
            # For single laptop mode, try connecting to localhost
            try:
                local_config = DATABASE_CONFIG['secondary'].copy()
                local_config['host'] = 'localhost'
                local_config['connect_timeout'] = 3
                local_config['connection_timeout'] = 3
                self.secondary_connection = mysql.connector.connect(**local_config)
            except Error as e2:
                print(f"Could not connect to secondary database on localhost: {e2}")
                self.secondary_connection = None

    def _ensure_order_tables(self):
        """Ensure order and customer tables exist in primary database"""
        if not self.primary_connection:
            return

        try:
            cursor = self.primary_connection.cursor()

            # Create ORDER_TABLE if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ORDER_TABLE (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    customer_id INT NOT NULL,
                    employee_id INT NULL,
                    service_type VARCHAR(100) NOT NULL,
                    service_description TEXT,
                    urgency ENUM('low', 'medium', 'high', 'emergency') DEFAULT 'medium',
                    estimated_cost DECIMAL(10,2),
                    status ENUM('pending', 'accepted', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    assigned_at TIMESTAMP NULL,
                    completed_at TIMESTAMP NULL,
                    customer_notes TEXT NULL,
                    provider_notes TEXT NULL,
                    rating DECIMAL(3,2) NULL,
                    feedback TEXT NULL,
                    INDEX idx_customer_id (customer_id),
                    INDEX idx_employee_id (employee_id),
                    INDEX idx_status (status),
                    INDEX idx_service_type (service_type),
                    INDEX idx_urgency (urgency),
                    INDEX idx_created_at (created_at)
                )
            """)

            # Add employee_id column if it doesn't exist (for backward compatibility)
            try:
                cursor.execute("ALTER TABLE ORDER_TABLE ADD COLUMN employee_id INT NULL")
            except Error as e:
                if "Duplicate column name" in str(e):
                    pass  # Column already exists, ignore error
                else:
                    print(f"Error adding employee_id column: {e}")

            try:
                cursor.execute("CREATE INDEX idx_employee_id ON ORDER_TABLE (employee_id)")
            except Error as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    pass  # Index already exists, ignore error
                else:
                    print(f"Error creating index: {e}")

            # Ensure provider_notes column exists (for backward compatibility)
            try:
                cursor.execute("ALTER TABLE ORDER_TABLE ADD COLUMN provider_notes TEXT NULL")
            except Error as e:
                if "Duplicate column name" in str(e):
                    pass  # Column already exists, ignore error
                else:
                    print(f"Error adding provider_notes column: {e}")

            # Drop and recreate CUSTOMER table to avoid foreign key issues
            cursor.execute("DROP TABLE IF EXISTS CUSTOMER")
            cursor.execute("""
                CREATE TABLE CUSTOMER (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_code VARCHAR(50) UNIQUE,
                    loyalty_points INT DEFAULT 0,
                    total_orders INT DEFAULT 0,
                    total_spent DECIMAL(10,2) DEFAULT 0.00,
                    preferred_regions TEXT,
                    membership_level ENUM('Bronze', 'Silver', 'Gold', 'Platinum') DEFAULT 'Bronze',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_customer_id (customer_id),
                    INDEX idx_membership (membership_level)
                )
            """)

            # Insert sample customers
            sample_customers = [
                (None, 'CUST001', 0, 0, 0.00, 'Downtown, North Side', 'Bronze'),
                (None, 'CUST002', 50, 3, 450.00, 'Downtown, Business District', 'Silver'),
                (None, 'CUST003', 120, 8, 1250.00, 'All Areas', 'Gold'),
                (None, 'CUST004', 200, 15, 2800.00, 'All Areas', 'Platinum'),
                (None, 'CUST005', 25, 2, 350.00, 'Suburbs', 'Silver')
            ]

            cursor.executemany("""
                INSERT INTO CUSTOMER (customer_id, customer_code, loyalty_points,
                                         total_orders, total_spent, preferred_regions, membership_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, sample_customers)
            print("✅ Sample customers created")

            cursor.close()

        except Error as e:
            print(f"Error creating order tables: {e}")

    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        connection_name: str = 'primary',
        modify: bool = False
    ) -> List[Dict]:
        """Execute query on specified database"""
        connection = self.primary_connection if connection_name == 'primary' else self.secondary_connection

        if not connection:
            print(f"No connection to {connection_name} database")
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # For INSERT/UPDATE/DELETE operations, commit and return affected rows
            if modify:
                connection.commit()
                result = [{'affected_rows': cursor.rowcount}]
            else:
                result = cursor.fetchall()

            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query on {connection_name}: {e}")
            return []

    # ---------------------------------------------------------------------
    # SEARCH / FEDERATED
    # ---------------------------------------------------------------------

    def search_companies(self, service_type: str, region: str = None) -> List[Dict]:
        """Search companies in primary database"""
        query = """
        SELECT c.*, s.service_name, s.category
        FROM companies c
        LEFT JOIN SERVICE_TYPE s ON c.business_type LIKE CONCAT('%', s.category, '%')
        WHERE 1=1
        """

        params = []
        if service_type:
            query += " AND (s.service_name LIKE %s OR s.category LIKE %s OR c.specialization_areas LIKE %s)"
            params.extend([f"%{service_type}%", f"%{service_type}%", f"%{service_type}%"])

        if region:
            query += " AND c.service_regions LIKE %s"
            params.append(f"%{region}%")

        query += " ORDER BY c.rating DESC, c.total_reviews DESC LIMIT 50"

        return self.execute_query(query, tuple(params) if params else None, 'primary')

    def search_employees(self, service_type: str, region: str = None) -> List[Dict]:
        """Search employees in secondary database (service_booking_secondary.employee)"""
        query = """
        SELECT
            e.employee_id,
            e.name        AS user_name,
            e.email,
            e.phone,
            e.specialization,
            e.certification_level,
            e.experience_years,
            e.rating,
            e.total_completed_orders,
            e.bio,
            e.avg_cost_per_hour,
            e.preferred_regions,
            e.emergency_service,
            e.availability_status
        FROM employee e
        WHERE e.availability_status = 'Available'
        """

        params = []
        if service_type:
            query += " AND (e.specialization LIKE %s OR e.bio LIKE %s)"
            like = f"%{service_type}%"
            params.extend([like, like])

        if region:
            query += " AND e.preferred_regions LIKE %s"
            params.append(f"%{region}%")

        query += " ORDER BY e.rating DESC, e.total_completed_orders DESC LIMIT 50"

        return self.execute_query(query, tuple(params) if params else None, 'secondary')

    def get_cross_laptop_results(self, service_type: str, region: str = None) -> Dict:
        """Get combined results from both databases"""
        # Search companies (primary database)
        companies = self.search_companies(service_type, region)

        # Search employees (secondary database)
        employees = self.search_employees(service_type, region)

        # If secondary DB is not available or returned nothing, try a local fallback dataset
        if (not self.secondary_connection) or (not employees):
            try:
                from pathlib import Path
                fallback_path = Path(__file__).parent / "Enhanced_Service_Booking_Secondary_Laptop" / "research_company_profiles.json"
                if fallback_path.exists():
                    with fallback_path.open("r", encoding="utf-8") as fh:
                        payload = json.load(fh)
                        companies_fallback = payload.get("companies", [])

                    # Convert a few companies into 'secondary' style entries so results include secondary-like profiles
                    employees = []
                    for idx, comp in enumerate(companies_fallback[:5], start=1):
                        employees.append({
                            'employee_id': 10000 + idx,
                            'user_name': comp.get('name', f'Provider {idx}'),
                            'job_type': comp.get('service_categories', ["general"])[0],
                            'rating': 4.0,
                            'bio': comp.get('insight', ''),
                            'preferred_regions': comp.get('primary_region', ''),
                            'avg_cost_per_hour': 80,
                            'specialization': ", ".join(comp.get('service_categories', [])),
                            'service_name': comp.get('service_categories', ["general"])[0],
                            'experience_years': 5,
                            'total_completed_orders': 10,
                            'phone': '',
                            'email': '',
                            'certification_level': 'standard',
                            'emergency_service': False,
                        })
            except Exception:
                # Silently ignore fallback load errors to avoid noisy terminal output
                employees = employees or []

        # Combine and format results
        combined_results = []

        # Add companies to results
        for company in companies:
            combined_results.append({
                'id': company['company_id'],
                'name': company['company_name'],
                'type': 'Company',
                'business_type': company['business_type'],
                'rating': company['rating'],
                'description': company['description'],
                'service_regions': company['service_regions'],
                'avg_cost': company['avg_hourly_rate'],
                'specialization': company['specialization_areas'],
                'data_source': 'Primary',
                'service_name': company.get('service_name', 'General Service'),
                'total_reviews': company['total_reviews'],
                'phone': company['phone'],
                'email': company['email']
            })

        # Add employees to results
        for employee in employees:
            # map specialization to "job_type"/service name semantics
            job_type = employee.get('job_type') or employee.get('specialization', 'General')
            service_name = employee.get('service_name') or job_type

            combined_results.append({
                'id': employee['employee_id'],
                'name': employee['user_name'],
                'type': 'Individual Worker',
                'business_type': job_type,
                'rating': employee.get('rating', 0),
                'description': employee.get('bio', ''),
                'service_regions': employee.get('preferred_regions', ''),
                'avg_cost': employee.get('avg_cost_per_hour', 0),
                'specialization': employee.get('specialization', ''),
                'data_source': 'Secondary',
                'service_name': service_name,
                'experience_years': employee.get('experience_years', 0),
                'total_orders': employee.get('total_completed_orders', 0),
                'phone': employee.get('phone', ''),
                'email': employee.get('email', ''),
                'certification_level': employee.get('certification_level', ''),
                'emergency_service': employee.get('emergency_service', 0),
            })

        # Apply deduplication using string similarity matching (Jaro-Winkler-like)
        dedup_report = {'status': 'not_applied'}
        try:
            deduplicated, duplicates_removed = StringSimplicityMatcher.deduplicate_federated_results(
                combined_results,
                similarity_threshold=0.80,
                keep_strategy="highest_rated"
            )

            # Store deduplication metadata internally
            dedup_report = {
                'status': 'applied',
                'original_count': len(combined_results),
                'deduplicated_count': len(deduplicated),
                'duplicates_removed': len(duplicates_removed)
            }

            # Use deduplicated results
            combined_results = deduplicated

            # Update counts to reflect deduplication
            companies_count = len([r for r in combined_results if r.get('data_source') == 'Primary'])
            employees_count = len([r for r in combined_results if r.get('data_source') == 'Secondary'])

        except Exception as e:
            # If deduplication fails, silently continue with original results
            dedup_report = {'status': 'failed', 'reason': str(e)}
            companies_count = len(companies)
            employees_count = len(employees)

        return {
            'companies': companies,
            'employees': employees,
            'combined_results': combined_results,
            'total_count': len(combined_results),
            'companies_count': companies_count,
            'employees_count': employees_count,
            '_deduplication_report': dedup_report  # Internal metadata (not displayed in UI)
        }

    # ---------------------------------------------------------------------
    # PROVIDER DETAILS
    # ---------------------------------------------------------------------

    def get_company_details(self, company_id: int) -> Dict:
        """Get detailed information about a company"""
        query = """
        SELECT c.*,
               COUNT(DISTINCT cr.review_id) as review_count
        FROM companies c
        LEFT JOIN COMPANY_REVIEWS cr ON c.company_id = cr.company_id
        WHERE c.company_id = %s
        GROUP BY c.company_id
        """

        result = self.execute_query(query, (company_id,), 'primary')
        return result[0] if result else {}

    def get_employee_details(self, employee_id: int) -> Dict:
        """Get detailed information about an employee from secondary DB"""
        # Basic employee info
        query = """
        SELECT
            employee_id,
            name,
            email,
            phone,
            specialization,
            certification_level,
            experience_years,
            rating,
            total_completed_orders,
            bio,
            avg_cost_per_hour,
            preferred_regions,
            emergency_service,
            availability_status,
            created_at
        FROM employee
        WHERE employee_id = %s
        """

        result = self.execute_query(query, (employee_id,), 'secondary')
        if not result:
            return {}

        employee = result[0]
        employee.setdefault('skills', [])

        # Recent orders from secondary.orders
        orders_query = """
        SELECT
            order_id,
            customer_id,
            employee_id,
            service_type,
            description,
            status,
            urgency,
            preferred_date,
            budget,
            location,
            created_at,
            updated_at
        FROM orders
        WHERE employee_id = %s
        ORDER BY created_at DESC
        LIMIT 5
        """
        try:
            recent_orders = self.execute_query(orders_query, (employee_id,), 'secondary')
        except Exception:
            recent_orders = []
        employee['recent_orders'] = recent_orders

        # Feedback stats from secondary.feedback
        feedback_query = """
        SELECT
            AVG(rating) AS avg_rating,
            COUNT(*)    AS total_feedbacks
        FROM feedback
        WHERE employee_id = %s
        """
        try:
            feedback = self.execute_query(feedback_query, (employee_id,), 'secondary')
            employee['feedback_stats'] = feedback[0] if feedback and feedback[0]['avg_rating'] is not None else {}
        except Exception:
            employee['feedback_stats'] = {}

        return employee

    def get_employee_id_from_provider(self, provider_name: str, provider_type: str) -> int:
        """Get employee_id from provider name on secondary.employee"""
        try:
            if provider_type.lower() in ['individual', 'individual worker']:
                query = """
                SELECT employee_id
                FROM employee
                WHERE name = %s
                LIMIT 1
                """
                result = self.execute_query(query, (provider_name,), 'secondary')
                if result:
                    return result[0]['employee_id']
            return 1  # Default fallback
        except Exception as e:
            print(f"Error getting employee ID: {e}")
            return 1  # Default fallback

    def get_provider_details(self, provider_id: int, provider_type: str) -> Dict:
        """Get detailed information about a specific provider"""
        try:
            if provider_type.lower() == 'company':
                # Get company details from primary database
                query = """
                SELECT c.*,
                       s.service_name, s.category, s.base_cost as service_cost
                FROM companies c
                LEFT JOIN COMPANY_SERVICES cs ON c.company_id = cs.company_id
                LEFT JOIN SERVICE_TYPE s ON cs.service_id = s.service_id
                WHERE c.company_id = %s
                LIMIT 1
                """
                results = self.execute_query(query, (provider_id,), 'primary')
                if results:
                    company = results[0]
                    return {
                        'id': company['company_id'],
                        'name': company['company_name'],
                        'type': 'Company',
                        'email': company['email'],
                        'phone': company['phone'],
                        'description': company['description'],
                        'rating': company['rating'],
                        'avg_cost': company['avg_hourly_rate'] or company.get('service_cost', 0),
                        'service_type': company.get('service_name', 'General'),
                        'specialization': company['specialization_areas'],
                        'regions': company['service_regions']
                    }

            elif provider_type.lower() in ['individual', 'individual worker']:
                # Get employee details from secondary.employee
                query = """
                SELECT
                    employee_id,
                    name        AS user_name,
                    email,
                    phone,
                    specialization,
                    certification_level,
                    experience_years,
                    rating,
                    total_completed_orders,
                    bio,
                    avg_cost_per_hour,
                    preferred_regions,
                    emergency_service,
                    availability_status
                FROM employee
                WHERE employee_id = %s
                LIMIT 1
                """
                results = self.execute_query(query, (provider_id,), 'secondary')
                if results:
                    employee = results[0]
                    return {
                        'id': employee['employee_id'],
                        'name': employee['user_name'],
                        'type': 'Individual Worker',
                        'email': employee['email'],
                        'phone': employee['phone'],
                        'address': '',  # not in schema
                        'description': employee.get('bio', f"Professional {employee.get('specialization', 'Worker')}"),
                        'rating': employee['rating'],
                        'avg_cost': employee['avg_cost_per_hour'] or 0,
                        'service_type': employee.get('specialization', 'General'),
                        'specialization': employee.get('specialization', ''),
                        'regions': employee.get('preferred_regions', ''),
                        'availability': employee.get('availability_status', 'Available'),
                        'experience_years': employee.get('experience_years', 0)
                    }

            return {}

        except Exception as e:
            print(f"Error getting provider details: {e}")
            return {}

    # ---------------------------------------------------------------------
    # CUSTOMER / EMPLOYEE ORDERS (PERMANENT IN PRIMARY)
    # ---------------------------------------------------------------------

    def get_customer_orders_permanent(self, customer_id: int = None) -> List[Dict]:
        """Get customer orders from permanent storage (primary.ORDER_TABLE)"""
        try:
            if customer_id is None:
                return []

            query = """
            SELECT
                o.order_id, o.order_number, o.customer_id, o.service_type,
                o.service_description, o.urgency, o.estimated_cost, o.status,
                o.created_at, o.updated_at, o.customer_notes
            FROM ORDER_TABLE o
            WHERE o.customer_id = %s
            ORDER BY o.updated_at DESC
            """

            results = self.execute_query(query, (customer_id,), 'primary')
            orders = []

            print(f"[DEBUG] Found {len(results)} orders for customer {customer_id}")

            for row in results:
                order = {
                    'order_id': row['order_id'],
                    'order_number': row['order_number'],
                    'customer_id': row['customer_id'],
                    'service_type': row['service_type'],
                    'service_description': row['service_description'],
                    'urgency': row['urgency'],
                    'estimated_cost': row['estimated_cost'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'customer_notes': row['customer_notes']
                }
                orders.append(order)
                print(f"[DEBUG] Order {order['order_number']} - Status: {order['status']}")

            return orders

        except Exception as e:
            print(f"Error getting customer orders: {e}")
            return []

    def get_employee_orders_permanent(self, employee_id: int) -> List[Dict]:
        """Get employee orders from permanent storage (primary.ORDER_TABLE)"""
        try:
            if employee_id is None:
                return []

            query = """
            SELECT
                o.order_id, o.order_number, o.customer_id, o.service_type,
                o.service_description, o.urgency, o.estimated_cost, o.status,
                o.created_at, o.updated_at, o.customer_notes
            FROM ORDER_TABLE o
            WHERE o.employee_id = %s OR (o.status = 'pending' AND o.employee_id IS NULL)
            ORDER BY o.created_at DESC
            """

            results = self.execute_query(query, (employee_id,), 'primary')
            orders = []

            for row in results:
                # Just use generic "Customer {id}" label; CUSTOMER table has no name
                customer_name = f"Customer {row['customer_id']}"

                order = {
                    'order_id': row['order_id'],
                    'order_number': row['order_number'],
                    'customer_name': customer_name,
                    'service_type': row['service_type'],
                    'service_description': row['service_description'],
                    'urgency': row['urgency'],
                    'estimated_cost': row['estimated_cost'],
                    'status': row['status'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'customer_notes': row['customer_notes']
                }
                orders.append(order)

            return orders

        except Exception as e:
            print(f"Error getting employee orders: {e}")
            return []

    def create_order_permanent(
        self,
        customer_id: int,
        provider_id: int,
        provider_type: str,
        service_type: str,
        service_description: str,
        urgency: str,
        estimated_cost: float,
        customer_notes: str = None
    ) -> int:
        """Create a permanent order in the primary database"""
        try:
            # Generate unique order number
            count_result = self.execute_query('SELECT COUNT(*) as count FROM ORDER_TABLE', None, 'primary')
            order_count = int(count_result[0]['count']) + 1 if count_result else 1
            order_number = f"ORD{customer_id:04d}{provider_id:03d}{order_count:04d}"

            query = """
            INSERT INTO ORDER_TABLE (
                order_number, customer_id, service_type, service_description,
                urgency, estimated_cost, status, customer_notes, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, NOW())
            """

            self.execute_query(
                query,
                (order_number, customer_id, service_type,
                 service_description, urgency, estimated_cost, customer_notes),
                'primary',
                modify=True
            )

            # Get the new order ID
            result = self.execute_query("SELECT LAST_INSERT_ID() as order_id", None, 'primary')
            order_id = result[0]['order_id'] if result else None

            if order_id:
                print(f"✅ Order created successfully: {order_number}")
                return order_id
            else:
                print("❌ Failed to get order ID after creation")
                return None

        except Exception as e:
            print(f"Error creating order: {e}")
            return None

    def update_order_status_permanent(
        self,
        order_id: int,
        status: str,
        employee_id: int = None,
        provider_notes: str = None,
        actual_cost: float = None
    ) -> bool:
        """Update order status permanently in primary database"""
        try:
            update_fields = {"status": status}
            if provider_notes:
                update_fields["provider_notes"] = provider_notes
            if employee_id:
                update_fields["employee_id"] = employee_id
            if actual_cost is not None:
                update_fields["estimated_cost"] = actual_cost

            if status == 'completed':
                update_fields["completed_at"] = "NOW()"
            elif status == 'accepted' and employee_id:
                update_fields["assigned_at"] = "NOW()"

            # Build dynamic update query
            set_clauses = []
            values = []
            for key, value in update_fields.items():
                if value == "NOW()":
                    set_clauses.append(f"{key} = NOW()")
                else:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)

            if values:
                query = f"UPDATE ORDER_TABLE SET {', '.join(set_clauses)}, updated_at = NOW() WHERE order_id = %s"
                values.append(order_id)
                self.execute_query(query, tuple(values), 'primary', modify=True)
            else:
                query = f"UPDATE ORDER_TABLE SET {', '.join(set_clauses)}, updated_at = NOW() WHERE order_id = %s"
                self.execute_query(query, (order_id,), 'primary', modify=True)

            print(f"✅ Order {order_id} status updated to: {status}")
            return True

        except Exception as e:
            print(f"Error updating order status: {e}")
            return False

    def cancel_order_permanent(self, order_id: int, employee_id: int) -> bool:
        """Cancel order permanently in primary database"""
        try:
            query = """
            UPDATE ORDER_TABLE
            SET status = 'cancelled',
                provider_notes = 'Cancelled by worker',
                employee_id = %s,
                updated_at = NOW()
            WHERE order_id = %s
            """

            self.execute_query(query, (employee_id, order_id), 'primary', modify=True)

            # Verify the update worked
            check_query = "SELECT status FROM ORDER_TABLE WHERE order_id = %s"
            result = self.execute_query(check_query, (order_id,), 'primary')
            if result and result[0]['status'] == 'cancelled':
                print(f"✅ Order {order_id} cancelled successfully - Status verified")
                return True
            else:
                print(f"⚠ Order {order_id} cancel may have failed - Status not updated")
                return False

        except Exception as e:
            print(f"Error cancelling order: {e}")
            return False

    # ---------------------------------------------------------------------
    # LEGACY SECONDARY ORDER / FEEDBACK HELPERS (ADAPTED TO YOUR SCHEMA)
    # ---------------------------------------------------------------------

    def get_customer_orders(self, customer_id: int) -> List[Dict]:
        """Get all orders for a customer from secondary.orders"""
        orders = []

        query = """
        SELECT
            o.*,
            e.name AS employee_name,
            'Secondary' AS data_source
        FROM orders o
        LEFT JOIN employee e ON o.employee_id = e.employee_id
        WHERE o.customer_id = %s
        ORDER BY o.created_at DESC
        """

        employee_orders = self.execute_query(query, (customer_id,), 'secondary')
        orders.extend(employee_orders or [])

        return orders

    def create_employee_order(self, order_data: Dict) -> bool:
        """
        Create a new order for an employee in secondary.orders
        Adapted to your secondary schema.
        """
        try:
            query = """
            INSERT INTO orders (
                customer_id,
                employee_id,
                service_type,
                description,
                status,
                urgency,
                preferred_date,
                budget,
                location
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            service_type = order_data.get('service_type', 'General Service')
            description = order_data.get('notes', '')
            status = order_data.get('status', 'pending')
            urgency = order_data.get('urgency_level', 'medium')
            preferred_date = order_data.get('preferred_date')  # date or None
            budget = order_data.get('total_cost', 0.0)
            location = order_data.get('service_location', '')

            params = (
                order_data['customer_id'],
                order_data['employee_id'],
                service_type,
                description,
                status,
                urgency,
                preferred_date,
                budget,
                location
            )

            cursor = self.secondary_connection.cursor()
            cursor.execute(query, params)
            self.secondary_connection.commit()
            cursor.close()

            return True
        except Error as e:
            print(f"Error creating employee order: {e}")
            return False

    def create_company_order(self, order_data: Dict) -> bool:
        """Create a new order for a company (placeholder for future implementation)"""
        print("Company order creation not yet implemented")
        return False

    def submit_feedback(self, feedback_data: Dict) -> bool:
        """Submit feedback for an employee using secondary.feedback schema"""
        try:
            if feedback_data['target_type'] == 'employee':
                query = """
                INSERT INTO feedback (order_id, employee_id, customer_id, rating, comment)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (
                    feedback_data['order_id'],
                    feedback_data['target_id'],
                    feedback_data['customer_id'],
                    feedback_data['rating'],
                    feedback_data.get('comments', '')
                )

                cursor = self.secondary_connection.cursor()
                cursor.execute(query, params)
                self.secondary_connection.commit()
                cursor.close()

                return True
            else:
                # Company feedback (placeholder for future implementation)
                print("Company feedback submission not yet implemented")
                return False

        except Error as e:
            print(f"Error submitting feedback: {e}")
            return False

    # ---------------------------------------------------------------------
    # ADMIN / HEALTH
    # ---------------------------------------------------------------------

    def get_database_health(self) -> Dict:
        """Check health of both database connections"""
        health = {
            'primary': self.primary_connection is not None,
            'secondary': self.secondary_connection is not None,
            'cache_size': len(self.cache),
            'last_sync': self.last_sync_time
        }

        # Test primary connection
        if health['primary']:
            try:
                result = self.execute_query("SELECT 1 as test", connection_name='primary')
                health['primary'] = len(result) > 0
            except Exception:
                health['primary'] = False

        # Test secondary connection
        if health['secondary']:
            try:
                result = self.execute_query("SELECT 1 as test", connection_name='secondary')
                health['secondary'] = len(result) > 0
            except Exception:
                health['secondary'] = False

        return health

    def get_all_users_admin(self) -> Dict[str, List[Dict]]:
        """Get all users (customers and employees) for admin dashboard"""
        try:
            users = {
                'customers': [],
                'employees': [],
                'companies': []
            }

            # Customers from primary USER (if exists) – original behavior
            try:
                customer_query = """
                SELECT user_id, name, email, phone, registration_date, is_active, is_verified
                FROM USER
                WHERE name LIKE 'Customer %'
                ORDER BY registration_date DESC
                """
                customer_results = self.execute_query(customer_query, None, 'primary')
                if customer_results:
                    for i, customer in enumerate(customer_results, 1):
                        users['customers'].append({
                            'id': i,
                            'user_id': customer['user_id'],
                            'name': customer['name'],
                            'email': customer['email'],
                            'phone': customer['phone'],
                            'type': 'Customer',
                            'membership_level': 'Bronze',
                            'total_orders': 0,
                            'total_spent': 0.00,
                            'registration_date': customer['registration_date'],
                            'is_active': customer['is_active'],
                            'is_verified': customer['is_verified']
                        })
            except Exception as e:
                print(f"Error getting customers: {e}")
                # Fallback sample
                sample_customers = [
                    {'name': 'John Doe', 'email': 'john@example.com', 'phone': '555-0101'},
                    {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '555-0102'},
                    {'name': 'Mike Johnson', 'email': 'mike@example.com', 'phone': '555-0103'},
                    {'name': 'Sarah Williams', 'email': 'sarah@example.com', 'phone': '555-0104'},
                    {'name': 'Tom Brown', 'email': 'tom@example.com', 'phone': '555-0105'}
                ]

                for i, customer in enumerate(sample_customers, 1):
                    users['customers'].append({
                        'id': i,
                        'user_id': 1000 + i,
                        'name': customer['name'],
                        'email': customer['email'],
                        'phone': customer['phone'],
                        'type': 'Customer',
                        'membership_level': 'Bronze',
                        'total_orders': 0,
                        'total_spent': 0.00,
                        'registration_date': None,
                        'is_active': True,
                        'is_verified': True
                    })

            # Employees from secondary.employee
            try:
                employee_query = """
                SELECT
                    employee_id,
                    name,
                    email,
                    phone,
                    specialization,
                    experience_years,
                    total_completed_orders,
                    rating,
                    availability_status,
                    certification_level,
                    created_at
                FROM employee
                ORDER BY created_at DESC
                """
                employee_results = self.execute_query(employee_query, None, 'secondary')
                if employee_results:
                    for employee in employee_results:
                        users['employees'].append({
                            'id': employee['employee_id'],
                            'user_id': employee['employee_id'],   # no separate user_id in this schema
                            'name': employee['name'],
                            'email': employee['email'],
                            'phone': employee['phone'],
                            'type': 'Employee',
                            'job_type': employee['specialization'],
                            'specialization': employee['specialization'],
                            'experience_years': float(employee['experience_years'] or 0),
                            'total_orders': employee['total_completed_orders'],
                            'total_earnings': 0.0,  # not tracked in this schema
                            'rating': float(employee['rating'] or 0),
                            'availability_status': employee['availability_status'],
                            'certification_level': employee['certification_level'],
                            'registration_date': employee['created_at'],
                            'is_active': True,
                            'is_verified': True
                        })
            except Exception as e:
                print(f"Error getting employees: {e}")

            # Fallback employees if secondary empty
            if not users['employees']:
                try:
                    from pathlib import Path
                    fallback_path = Path(__file__).parent / "Enhanced_Service_Booking_Secondary_Laptop" / "research_company_profiles.json"
                    if fallback_path.exists():
                        with fallback_path.open("r", encoding="utf-8") as fh:
                            payload = json.load(fh)
                            companies_fallback = payload.get("companies", [])

                        for idx, comp in enumerate(companies_fallback[:5], start=1):
                            users['employees'].append({
                                'id': 1000 + idx,
                                'user_id': 2000 + idx,
                                'name': comp.get('name', f'Provider {idx}'),
                                'email': '',
                                'phone': '',
                                'type': 'Employee',
                                'job_type': comp.get('service_categories', ["general"])[0],
                                'specialization': ", ".join(comp.get('service_categories', [])),
                                'experience_years': 5,
                                'total_orders': 0,
                                'total_earnings': 0.0,
                                'rating': 4.0,
                                'availability_status': 'Available',
                                'certification_level': 'standard',
                                'registration_date': None,
                                'is_active': True,
                                'is_verified': True
                            })
                except Exception:
                    pass

            # Companies from primary.companies
            try:
                company_query = """
                SELECT company_id, company_name, business_type, description, rating, total_reviews,
                       phone, email, website, specialization_areas, service_regions
                FROM companies
                ORDER BY company_name ASC
                """
                company_results = self.execute_query(company_query, None, 'primary')
                if company_results:
                    for company in company_results:
                        users['companies'].append({
                            'id': company['company_id'],
                            'name': company['company_name'],
                            'email': company['email'],
                            'phone': company['phone'],
                            'type': 'Company',
                            'business_type': company['business_type'],
                            'description': company['description'],
                            'rating': company['rating'],
                            'total_reviews': company['total_reviews'],
                            'specialization_areas': company['specialization_areas'],
                            'service_regions': company['service_regions'],
                            'website': company['website']
                        })
            except Exception as e:
                print(f"Error getting companies: {e}")

            return users

        except Exception as e:
            print(f"Error getting all users: {e}")
            return {'customers': [], 'employees': [], 'companies': []}

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for admin dashboard"""
        try:
            status = {
                'database_health': self.get_database_health(),
                'total_orders': 0,
                'orders_by_status': {
                    'pending': 0,
                    'accepted': 0,
                    'in_progress': 0,
                    'completed': 0,
                    'cancelled': 0
                },
                'total_users': 0,
                'active_users': 0,
                'services_offered': 0
            }

            # Order statistics from primary.ORDER_TABLE
            try:
                order_stats_query = """
                SELECT status, COUNT(*) as count
                FROM ORDER_TABLE
                GROUP BY status
                """
                order_results = self.execute_query(order_stats_query, None, 'primary')
                if order_results:
                    for row in order_results:
                        if row['status'] in status['orders_by_status']:
                            status['orders_by_status'][row['status']] = row['count']
                        status['total_orders'] += row['count']
            except Exception as e:
                print(f"Error getting order stats: {e}")

            # User statistics
            try:
                customer_count = self.execute_query("SELECT COUNT(*) as count FROM CUSTOMER", None, 'primary')
                employee_count = self.execute_query("SELECT COUNT(*) as count FROM employee", None, 'secondary')
                company_count = self.execute_query("SELECT COUNT(*) as count FROM companies", None, 'primary')

                if customer_count:
                    status['total_users'] += customer_count[0]['count']
                if employee_count:
                    status['total_users'] += employee_count[0]['count']
                if company_count:
                    status['total_users'] += company_count[0]['count']

                # Active users:
                # - customers: treat all as active (no flag)
                # - employees: available ones as active
                active_customers = customer_count  # all
                active_employees = self.execute_query(
                    "SELECT COUNT(*) as count FROM employee WHERE availability_status = 'Available'",
                    None,
                    'secondary'
                )

                if active_customers:
                    status['active_users'] += active_customers[0]['count']
                if active_employees:
                    status['active_users'] += active_employees[0]['count']

            except Exception as e:
                print(f"Error getting user stats: {e}")

            # Service statistics from primary.SERVICE_TYPE
            try:
                service_count = self.execute_query("SELECT COUNT(*) as count FROM SERVICE_TYPE WHERE is_active = 1", None, 'primary')
                if service_count:
                    status['services_offered'] = service_count[0]['count']
            except Exception as e:
                print(f"Error getting service stats: {e}")

            return status

        except Exception as e:
            print(f"Error getting system status: {e}")
            return {
                'database_health': {'primary': False, 'secondary': False, 'mode': 'error'},
                'total_orders': 0,
                'orders_by_status': {},
                'total_users': 0,
                'active_users': 0,
                'services_offered': 0
            }

    def close_connections(self):
        """Close all database connections"""
        if self.primary_connection:
            self.primary_connection.close()
        if self.secondary_connection:
            self.secondary_connection.close()
        # print("Database connections closed")  # Hidden for cleaner output
