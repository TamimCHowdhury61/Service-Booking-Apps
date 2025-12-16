import threading
import time
from typing import Dict, List, Optional, Tuple
import mysql.connector
from mysql.connector import Error
from config_primary_only import DATABASE_CONFIG


class DistributedDatabaseManager:
    def __init__(self):
        self.primary_connection = None
        self.secondary_connection = None
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.last_sync_time = 0
        self.primary_only_mode = False  # Will detect automatically

        # Initialize connections
        self.connect_to_databases()

    def connect_to_databases(self):
        """Connect to both primary and secondary databases"""
        try:
            # Connect to primary database
            self.primary_connection = mysql.connector.connect(**DATABASE_CONFIG['primary'])
            print("Connected to primary database")
        except Error as e:
            print(f"Warning: Could not connect to primary database: {e}")
            self.primary_connection = None

        try:
            # Connect to secondary database
            self.secondary_connection = mysql.connector.connect(**DATABASE_CONFIG['secondary'])
            print("Connected to secondary database")
        except Error as e:
            print(f"Warning: Could not connect to secondary database: {e}")
            # Check if we have employee data in primary database
            if self.primary_connection:
                try:
                    cursor = self.primary_connection.cursor()
                    cursor.execute("SHOW TABLES LIKE 'EMPLOYEE'")
                    if cursor.fetchone():
                        print("Operating in Primary-Only Mode (employees in primary database)")
                        self.primary_only_mode = True
                    cursor.close()
                except:
                    pass

            # For single laptop mode, try connecting to localhost if primary_only_mode
            if not self.primary_only_mode:
                try:
                    local_config = DATABASE_CONFIG['secondary'].copy()
                    local_config['host'] = 'localhost'
                    self.secondary_connection = mysql.connector.connect(**local_config)
                    print("Connected to secondary database on localhost (Single laptop mode)")
                except Error as e2:
                    print(f"Could not connect to secondary database on localhost: {e2}")
                    self.secondary_connection = None

    def execute_query(self, query: str, params: Optional[Tuple] = None, connection_name: str = 'primary') -> List[Dict]:
        """Execute query on specified database"""
        # If in primary-only mode, use primary connection for everything
        if self.primary_only_mode:
            connection = self.primary_connection
        else:
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

            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"Error executing query on {connection_name}: {e}")
            return []

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

        query += " ORDER BY c.rating DESC, c.total_reviews DESC LIMIT 20"

        return self.execute_query(query, tuple(params) if params else None, 'primary')

    def search_employees(self, service_type: str, region: str = None) -> List[Dict]:
        """Search employees in database (primary if primary_only_mode, else secondary)"""
        db_name = 'primary' if self.primary_only_mode else 'secondary'

        query = """
        SELECT e.*, u.phone, u.email, u.address,
               s.service_name, s.category
        FROM EMPLOYEE e
        JOIN USER u ON e.user_id = u.user_id
        LEFT JOIN SERVICE_TYPE s ON s.service_name LIKE CONCAT('%', e.job_type, '%')
        WHERE e.is_active = 1
        """

        params = []
        if service_type:
            query += " AND (e.job_type LIKE %s OR e.job_type LIKE %s OR s.service_name LIKE %s)"
            params.extend([f"%{service_type}%", f"%{service_type}%", f"%{service_type}%", f"%{service_type}%"])

        if region:
            query += " AND e.preferred_regions LIKE %s"
            params.append(f"%{region}%")

        query += " ORDER BY e.rating DESC, e.total_completed_orders DESC LIMIT 20"

        return self.execute_query(query, tuple(params) if params else None, db_name)

    def get_cross_laptop_results(self, service_type: str, region: str = None) -> Dict:
        """Get combined results from available databases"""
        # Search companies (primary database)
        companies = self.search_companies(service_type, region)

        # Search employees (primary if primary_only_mode, else secondary)
        employees = self.search_employees(service_type, region)

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
            combined_results.append({
                'id': employee['employee_id'],
                'name': employee.get('name', f'Employee {employee["employee_id"]}'),
                'type': 'Individual Worker',
                'business_type': employee['job_type'],
                'rating': employee['rating'],
                'description': employee.get('bio', ''),
                'service_regions': employee['preferred_regions'],
                'avg_cost': employee['avg_cost_per_hour'],
                'specialization': employee['specialization'],
                'data_source': 'Primary' if self.primary_only_mode else 'Secondary',
                'service_name': employee.get('service_name', employee['job_type']),
                'experience_years': employee['experience_years'],
                'total_orders': employee['total_completed_orders'],
                'phone': employee.get('phone', 'N/A'),
                'email': employee.get('email', 'N/A'),
                'certification_level': employee['certification_level'],
                'emergency_service': employee['emergency_service']
            })

        return {
            'companies': companies,
            'employees': employees,
            'combined_results': combined_results,
            'total_count': len(combined_results),
            'companies_count': len(companies),
            'employees_count': len(employees),
            'mode': 'Primary-Only' if self.primary_only_mode else 'Distributed'
        }

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
        """Get detailed information about an employee"""
        db_name = 'primary' if self.primary_only_mode else 'secondary'

        # Get basic employee info
        query = """
        SELECT e.*, u.phone, u.email, u.address
        FROM EMPLOYEE e
        JOIN USER u ON e.user_id = u.user_id
        WHERE e.employee_id = %s
        """

        result = self.execute_query(query, (employee_id,), db_name)
        if not result:
            return {}

        employee = result[0]

        # Skills are stored in the skills field as text
        employee['skills'] = []

        # Get recent orders
        orders_query = """
        SELECT o.*, s.service_name
        FROM ORDER_TABLE o
        LEFT JOIN SERVICE_TYPE s ON o.service_id = s.service_id
        WHERE o.employee_id = %s
        ORDER BY o.order_date DESC
        LIMIT 5
        """

        try:
            recent_orders = self.execute_query(orders_query, (employee_id,), db_name)
            employee['recent_orders'] = recent_orders
        except:
            employee['recent_orders'] = []

        # Get average feedback ratings
        feedback_query = """
        SELECT AVG(rating) as avg_rating, AVG(quality_rating) as avg_quality,
               AVG(professionalism_rating) as avg_professionalism, AVG(value_rating) as avg_value
        FROM FEEDBACK
        WHERE employee_id = %s
        """

        try:
            feedback = self.execute_query(feedback_query, (employee_id,), db_name)
            if feedback and feedback[0]['avg_rating']:
                employee['feedback_stats'] = feedback[0]
        except:
            employee['feedback_stats'] = {}

        return employee

    def get_customer_orders(self, customer_id: int) -> List[Dict]:
        """Get all orders for a customer from available database"""
        db_name = 'primary' if self.primary_only_mode else 'secondary'
        orders = []

        # Get orders from database
        query = """
        SELECT o.*, e.name as employee_name, e.job_type, s.service_name,
               'Primary' as data_source
        FROM ORDER_TABLE o
        LEFT JOIN EMPLOYEE e ON o.employee_id = e.employee_id
        LEFT JOIN USER eu ON e.user_id = eu.user_id
        LEFT JOIN SERVICE_TYPE s ON o.service_id = s.service_id
        WHERE o.customer_id = %s
        ORDER BY o.order_date DESC
        """

        employee_orders = self.execute_query(query, (customer_id,), db_name)
        orders.extend(employee_orders)

        return orders

    def create_employee_order(self, order_data: Dict) -> bool:
        """Create a new order for an employee"""
        db_name = 'primary' if self.primary_only_mode else 'secondary'
        connection = self.primary_connection if self.primary_only_mode else self.secondary_connection

        try:
            query = """
            INSERT INTO ORDER_TABLE (customer_id, employee_id, service_id, total_cost,
                                   urgency_level, service_location, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            params = (
                order_data['customer_id'],
                order_data['employee_id'],
                order_data['service_id'],
                order_data['total_cost'],
                order_data.get('urgency_level', 'Medium'),
                order_data.get('service_location', ''),
                order_data.get('notes', '')
            )

            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            cursor.close()

            return True
        except Error as e:
            print(f"Error creating employee order: {e}")
            return False

    def create_company_order(self, order_data: Dict) -> bool:
        """Create a new order for a company (placeholder for future implementation)"""
        # This would be implemented if we want to track company orders in primary database
        print("Company order creation not yet implemented")
        return False

    def submit_feedback(self, feedback_data: Dict) -> bool:
        """Submit feedback for an employee or company"""
        db_name = 'primary' if self.primary_only_mode else 'secondary'
        connection = self.primary_connection if self.primary_only_mode else self.secondary_connection

        try:
            if feedback_data['target_type'] == 'employee':
                query = """
                INSERT INTO FEEDBACK (order_id, employee_id, customer_id, rating,
                                    comments, quality_rating, professionalism_rating, value_rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    feedback_data['order_id'],
                    feedback_data['target_id'],
                    feedback_data['customer_id'],
                    feedback_data['rating'],
                    feedback_data.get('comments', ''),
                    feedback_data.get('quality_rating', feedback_data['rating']),
                    feedback_data.get('professionalism_rating', feedback_data['rating']),
                    feedback_data.get('value_rating', feedback_data['rating'])
                )

                cursor = connection.cursor()
                cursor.execute(query, params)
                connection.commit()
                cursor.close()

                return True
            else:
                # Company feedback (placeholder for future implementation)
                print("Company feedback submission not yet implemented")
                return False

        except Error as e:
            print(f"Error submitting feedback: {e}")
            return False

    def get_database_health(self) -> Dict:
        """Check health of database connections"""
        health = {
            'primary': self.primary_connection is not None,
            'secondary': self.secondary_connection is not None,
            'cache_size': len(self.cache),
            'last_sync': self.last_sync_time,
            'mode': 'Primary-Only' if self.primary_only_mode else 'Distributed'
        }

        # Test primary connection
        if health['primary']:
            try:
                result = self.execute_query("SELECT 1 as test", connection_name='primary')
                health['primary'] = len(result) > 0
            except:
                health['primary'] = False

        # Test secondary connection (if not in primary-only mode)
        if not self.primary_only_mode and health['secondary']:
            try:
                result = self.execute_query("SELECT 1 as test", connection_name='secondary')
                health['secondary'] = len(result) > 0
            except:
                health['secondary'] = False

        return health

    def close_connections(self):
        """Close all database connections"""
        if self.primary_connection:
            self.primary_connection.close()
        if self.secondary_connection:
            self.secondary_connection.close()
        print("Database connections closed")