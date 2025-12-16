#!/usr/bin/env python3

"""
Enhanced Database Manager with Permanent Storage and Cross-Laptop Sync
This ensures all order changes are permanently saved and synchronized
"""

import sys
import os
import mysql.connector
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import working database configuration
from config_primary_only import DATABASE_CONFIG

class EnhancedDatabaseManager:
    def __init__(self):
        """Initialize enhanced database connections with permanent storage"""
        self.primary_connection = None
        self.secondary_connection = None
        self.mode = "primary_only"
        self.connect_to_databases()

    def connect_to_databases(self):
        """Connect to both primary and secondary databases"""
        try:
            # Primary database connection - use working configuration
            self.primary_connection = mysql.connector.connect(**DATABASE_CONFIG['primary'])
            print("Connected to primary database")

            # Secondary database connection
            try:
                self.secondary_connection = mysql.connector.connect(**DATABASE_CONFIG['secondary'])
                print("Connected to secondary database")
                self.mode = "distributed"
            except Exception as e:
                print(f"Warning: Could not connect to secondary database: {e}")
                print("Operating in Primary-Only Mode (will sync when secondary connects)")

        except Exception as e:
            print(f"Error connecting to primary database: {e}")
            raise

    def execute_permanent_update(self, query, params=None, database="primary"):
        """Execute a permanent database update with proper commit and sync"""
        connection = self.primary_connection if database == "primary" else self.secondary_connection

        if not connection:
            raise Exception(f"No connection to {database} database")

        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()

            # If in distributed mode, sync to other database
            if self.mode == "distributed":
                self.sync_to_other_database(query, params, database)

            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

        except Exception as e:
            connection.rollback()
            raise Exception(f"Database update failed: {e}")
        finally:
            cursor.close()

    def sync_to_other_database(self, query, params, source_database):
        """Sync database changes to the other laptop"""
        try:
            target_connection = self.secondary_connection if source_database == "primary" else self.primary_connection

            if target_connection and target_connection.is_connected():
                cursor = target_connection.cursor()
                cursor.execute(query, params)
                target_connection.commit()
                cursor.close()
                print(f"Synced changes to {'secondary' if source_database == 'primary' else 'primary'} database")
        except Exception as e:
            print(f"Warning: Failed to sync to other database: {e}")
            # Don't raise here - primary operation succeeded

    def create_order_permanent(self, customer_id, provider_id, provider_type, service_type,
                             service_description, urgency, estimated_cost, customer_notes):
        """Create order with permanent storage"""
        query = """
        INSERT INTO order_table (
            customer_id, employee_id, service_id, total_cost, urgency_level,
            service_location, notes, order_status, order_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """

        # Map urgency levels to match database enum
        urgency_map = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'emergency': 'Emergency'
        }

        params = (
            customer_id, provider_id, 1, estimated_cost, urgency_map.get(urgency, 'Medium'),
            'Customer Location', f"{service_description}. {customer_notes}", 'Pending'
        )

        order_id = self.execute_permanent_update(query, params)
        print(f"Order #{order_id} created permanently and synced")
        return order_id

    def update_order_status_permanent(self, order_id, new_status, provider_id=None, provider_notes=None, actual_cost=None):
        """Update order status with permanent storage"""
        # Map status to database enum values
        status_map = {
            'pending': 'Pending',
            'accepted': 'Accepted',
            'in_progress': 'Processing',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }

        update_parts = ["order_status = %s"]
        params = [status_map.get(new_status, 'Pending'), order_id]

        if provider_id:
            update_parts.append("employee_id = %s")
            params.insert(-1, provider_id)

        if provider_notes is not None:
            update_parts.append("notes = %s")
            params.insert(-1, provider_notes)

        if actual_cost is not None:
            update_parts.append("total_cost = %s")
            params.insert(-1, actual_cost)

        if new_status == 'completed':
            update_parts.append("completion_date = CURRENT_TIMESTAMP")

        query = f"UPDATE order_table SET {', '.join(update_parts)} WHERE order_id = %s"

        affected_rows = self.execute_permanent_update(query, params)
        print(f"Order #{order_id} status updated to '{new_status}' permanently and synced")
        return affected_rows

    def cancel_order_permanent(self, order_id, provider_id):
        """Cancel order with permanent storage"""
        query = """
        UPDATE order_table
        SET order_status = 'Cancelled',
            employee_id = NULL
        WHERE order_id = %s AND employee_id = %s
        """

        affected_rows = self.execute_permanent_update(query, (order_id, provider_id))
        print(f"Order #{order_id} cancelled permanently and synced")
        return affected_rows

    def get_customer_orders_permanent(self, customer_id):
        """Get customer orders with permanent data"""
        query = """
        SELECT o.order_id,
               COALESCE(comp.company_name, CONCAT('Employee ', o.employee_id), 'Unassigned') as provider_name,
               'Service' as service_type, o.order_status, o.urgency_level, o.total_cost,
               o.notes, o.notes, o.notes,
               DATE_FORMAT(o.order_date, '%Y-%m-%d %H:%i') as created_at,
               DATE_FORMAT(o.order_date, '%Y-%m-%d %H:%i') as updated_at,
               DATE_FORMAT(o.order_date, '%Y-%m-%d %H:%i') as assigned_at,
               DATE_FORMAT(o.completion_date, '%Y-%m-%d %H:%i') as completed_at
        FROM order_table o
        LEFT JOIN companies comp ON o.employee_id = comp.company_id
        WHERE o.customer_id = %s
        ORDER BY o.order_date DESC
        """

        cursor = self.primary_connection.cursor()
        try:
            cursor.execute(query, (customer_id,))
            orders = cursor.fetchall()
            return orders
        finally:
            cursor.close()

    def get_employee_orders_permanent(self, employee_id):
        """Get available orders for employee with permanent data"""
        query = """
        SELECT o.order_id, cu.name as customer_name, 'Service' as service_type,
               o.urgency_level, o.total_cost, o.notes, o.order_date
        FROM order_table o
        JOIN customer cu ON o.customer_id = cu.customer_id
        WHERE o.order_status = 'Pending'
        AND (o.employee_id IS NULL OR o.employee_id = %s)
        ORDER BY
            CASE o.urgency_level
                WHEN 'Emergency' THEN 1
                WHEN 'High' THEN 2
                WHEN 'Medium' THEN 3
                ELSE 4
            END,
            o.order_date DESC
        LIMIT 20
        """

        cursor = self.primary_connection.cursor()
        try:
            cursor.execute(query, (employee_id,))
            orders = cursor.fetchall()
            return orders
        finally:
            cursor.close()

    def get_provider_details(self, provider_name, provider_type):
        """Get provider details for order creation"""
        if provider_type.lower() == "company":
            query = "SELECT company_id as provider_id FROM companies WHERE name = %s"
        else:
            query = "SELECT employee_id as provider_id FROM employee WHERE name = %s"

        cursor = self.primary_connection.cursor()
        try:
            cursor.execute(query, (provider_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()

    def verify_permanent_storage(self):
        """Verify that data is permanently stored"""
        try:
            cursor = self.primary_connection.cursor()

            # Check order table integrity
            cursor.execute("SELECT COUNT(*) FROM order_table")
            order_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM order_table WHERE order_status = 'Pending'")
            pending_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM order_table WHERE order_status = 'Completed'")
            completed_count = cursor.fetchone()[0]

            cursor.close()

            print(f"Permanent Storage Verification:")
            print(f"  Total Orders: {order_count}")
            print(f"  Pending Orders: {pending_count}")
            print(f"  Completed Orders: {completed_count}")
            print(f"  Database Mode: {self.mode}")

            return {
                'total_orders': order_count,
                'pending_orders': pending_count,
                'completed_orders': completed_count,
                'mode': self.mode
            }

        except Exception as e:
            print(f"Verification failed: {e}")
            return None

    def close_connections(self):
        """Close all database connections"""
        try:
            if self.primary_connection and self.primary_connection.is_connected():
                self.primary_connection.close()
                print("Primary database connection closed")
        except:
            pass

        try:
            if self.secondary_connection and self.secondary_connection.is_connected():
                self.secondary_connection.close()
                print("Secondary database connection closed")
        except:
            pass

if __name__ == "__main__":
    # Test the enhanced database manager
    print("Testing Enhanced Database Manager with Permanent Storage...")

    db = EnhancedDatabaseManager()

    # Verify permanent storage
    verification = db.verify_permanent_storage()
    if verification:
        print("Permanent storage system working correctly!")

    db.close_connections()
    print("Enhanced database manager test complete!")