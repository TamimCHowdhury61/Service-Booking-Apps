#!/usr/bin/env python3

"""
Secondary Laptop Database Setup Script
Creates the employee database with all necessary tables
"""

import psycopg2
from psycopg2 import DatabaseError, OperationalError
import sys

# Database configuration for secondary laptop
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tamimchowdhury',
    'password': '',
    'database': 'service_booking_secondary',
    'port': 5432
}

def setup_secondary_database():
    """Setup the secondary laptop database (Individual Workers)"""
    print("=" * 60)
    print("SECONDARY LAPTOP DATABASE SETUP")
    print("Individual Workers Database")
    print("=" * 60)

    try:
        # Connect to postgres default database to create target database if needed
        try:
            connection = psycopg2.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                dbname='postgres'
            )
            cursor = connection.cursor()

            # Create database if not exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (DB_CONFIG['database'],))
            if not cursor.fetchone():
                cursor.execute(f'CREATE DATABASE {DB_CONFIG["database"]}')
                print(f"Created database: {DB_CONFIG['database']}")

            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Database creation step: {e}")

        # Connect to the target database
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        print("Creating tables for secondary laptop...")

        # Create SERVICE_TYPE table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SERVICE_TYPE (
                service_id SERIAL PRIMARY KEY,
                service_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create USER table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "USER" (
                user_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                address TEXT,
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create EMPLOYEE table (main table for this laptop)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS EMPLOYEE (
                employee_id SERIAL PRIMARY KEY,
                user_id INT REFERENCES "USER"(user_id),
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                specialization VARCHAR(50),
                job_type VARCHAR(50),
                certification_level VARCHAR(32) DEFAULT 'None',
                experience_years NUMERIC(3,1) DEFAULT 0,
                rating NUMERIC(3,2) DEFAULT 0.00,
                total_completed_orders INT DEFAULT 0,
                bio TEXT,
                avg_cost_per_hour NUMERIC(10,2),
                preferred_regions TEXT,
                emergency_service BOOLEAN DEFAULT FALSE,
                availability_status VARCHAR(32) DEFAULT 'Available',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create CUSTOMER table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CUSTOMER (
                customer_id SERIAL PRIMARY KEY,
                customer_code VARCHAR(50) UNIQUE,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                address TEXT,
                loyalty_points INT DEFAULT 0,
                total_orders INT DEFAULT 0,
                total_spent NUMERIC(10,2) DEFAULT 0.00,
                preferred_regions TEXT,
                membership_level VARCHAR(32) DEFAULT 'Bronze',
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create ORDER_TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ORDER_TABLE (
                order_id SERIAL PRIMARY KEY,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                customer_id INT NOT NULL REFERENCES CUSTOMER(customer_id),
                employee_id INT REFERENCES EMPLOYEE(employee_id),
                service_id INT REFERENCES SERVICE_TYPE(service_id),
                service_type VARCHAR(100) NOT NULL,
                service_description TEXT,
                urgency_level VARCHAR(32) DEFAULT 'medium',
                total_cost NUMERIC(10,2),
                service_location VARCHAR(100),
                notes TEXT,
                order_status VARCHAR(32) DEFAULT 'pending',
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_date TIMESTAMP,
                provider_notes TEXT,
                status VARCHAR(32) DEFAULT 'pending',
                estimated_cost NUMERIC(10,2)
            )
        """)

        # Create FEEDBACK table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS FEEDBACK (
                feedback_id SERIAL PRIMARY KEY,
                order_id INT REFERENCES ORDER_TABLE(order_id),
                employee_id INT REFERENCES EMPLOYEE(employee_id),
                customer_id INT REFERENCES CUSTOMER(customer_id),
                rating NUMERIC(3,2) NOT NULL CHECK (rating >= 1 AND rating <= 5),
                quality_rating NUMERIC(3,2) CHECK (quality_rating >= 1 AND quality_rating <= 5),
                professionalism_rating NUMERIC(3,2) CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
                value_rating NUMERIC(3,2) CHECK (value_rating >= 1 AND value_rating <= 5),
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for better performance
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_employee_specialization ON EMPLOYEE (specialization)",
            "CREATE INDEX IF NOT EXISTS idx_employee_job_type ON EMPLOYEE (job_type)",
            "CREATE INDEX IF NOT EXISTS idx_employee_rating ON EMPLOYEE (rating)",
            "CREATE INDEX IF NOT EXISTS idx_employee_availability ON EMPLOYEE (availability_status)",
            "CREATE INDEX IF NOT EXISTS idx_employee_active ON EMPLOYEE (is_active)",
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON ORDER_TABLE (customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_employee ON ORDER_TABLE (employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON ORDER_TABLE (order_status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_service_type ON ORDER_TABLE (service_type)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_employee ON FEEDBACK (employee_id)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_customer ON FEEDBACK (customer_id)"
        ]

        for index_query in indexes:
            cursor.execute(index_query)

        # Insert sample data
        print("Inserting sample individual workers...")

        # Insert service types
        service_types = [
            ('Plumbing', 'plumbing', 'Professional plumbing services'),
            ('Electrical', 'electrical', 'Electrical installation and repair'),
            ('Carpentry', 'carpentry', 'Custom carpentry and woodwork'),
            ('Cleaning', 'cleaning', 'Professional cleaning services'),
            ('HVAC', 'hvac', 'Heating and air conditioning'),
            ('Painting', 'painting', 'Interior and exterior painting'),
            ('Landscaping', 'landscaping', 'Garden and yard maintenance'),
            ('Automotive', 'automotive', 'Vehicle repair and maintenance'),
            ('Pest Control', 'pest_control', 'Pest control and extermination'),
            ('Roofing', 'roofing', 'Residential and commercial roofing'),
            ('Insulation', 'insulation', 'Home insulation installation'),
            ('Solar Installation', 'solar', 'Solar panel installation and maintenance')
        ]

        cursor.executemany("""
            INSERT INTO SERVICE_TYPE (service_name, category, description)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
        """, service_types)

        # Insert users (for employee accounts)
        users_data = [
            ('John Smith', 'john.smith@secondary.com', '555-0201', '456 Worker Ave', 'worker123'),
            ('Sarah Johnson', 'sarah.j@secondary.com', '555-0202', '789 Tech Blvd', 'worker123'),
            ('Mike Davis', 'mike.davis@secondary.com', '555-0203', '321 Craft St', 'worker123'),
            ('Emily Brown', 'emily.brown@secondary.com', '555-0204', '654 Clean Ave', 'worker123'),
            ('Tom Wilson', 'tom.wilson@secondary.com', '555-0205', '987 HVAC Rd', 'worker123'),
            ('Lisa Anderson', 'lisa.anderson@secondary.com', '555-0206', '147 Paint St', 'worker123'),
            ('David Miller', 'david.miller@secondary.com', '555-0207', '258 Auto Dr', 'worker123'),
            ('Carlos Reyes', 'carlos.reyes@secondary.com', '555-0208', '369 Electric Ave', 'worker123'),
            ('Nina Patel', 'nina.patel@secondary.com', '555-0209', '741 Solar Way', 'worker123'),
            ('Marcus Chen', 'marcus.chen@secondary.com', '555-0210', '852 Glass St', 'worker123')
        ]

        cursor.executemany("""
            INSERT INTO "USER" (name, email, phone, address, password)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, users_data)

        # Get user IDs for employees
        cursor.execute("SELECT user_id FROM \"USER\" WHERE email LIKE '%@secondary.com' ORDER BY user_id")
        user_ids = [row[0] for row in cursor.fetchall()]

        # Insert employees (individual workers)
        employees_data = [
            (user_ids[0], 'John Smith', 'john.smith@secondary.com', '555-0201', 'Plumbing', 'Plumber', 'Professional', 8.5, 4.5, 67, 'Expert plumber with 8+ years of residential and commercial experience', 45.00, 'Downtown, Suburbs', True, 'Available', True),
            (user_ids[1], 'Sarah Johnson', 'sarah.j@secondary.com', '555-0202', 'Electrical', 'Electrician', 'Master', 12.0, 4.8, 124, 'Master electrician, licensed and insured for commercial and residential work', 65.00, 'City Wide', True, 'Available', True),
            (user_ids[2], 'Mike Davis', 'mike.davis@secondary.com', '555-0203', 'Carpentry', 'Carpenter', 'Professional', 6.0, 4.3, 45, 'Custom carpentry and furniture making specialist', 55.00, 'Downtown, East Side', False, 'Available', True),
            (user_ids[3], 'Emily Brown', 'emily.brown@secondary.com', '555-0204', 'Cleaning', 'Cleaner', 'Basic', 3.0, 4.2, 89, 'Professional house cleaning and organization services', 25.00, 'City Wide', False, 'Available', True),
            (user_ids[4], 'Tom Wilson', 'tom.wilson@secondary.com', '555-0205', 'HVAC', 'HVAC Technician', 'Professional', 10.0, 4.6, 78, 'HVAC installation and repair specialist', 75.00, 'All Areas', True, 'Available', True),
            (user_ids[5], 'Lisa Anderson', 'lisa.anderson@secondary.com', '555-0206', 'Painting', 'Painter', 'Professional', 7.0, 4.4, 56, 'Interior and exterior painting specialist', 35.00, 'Downtown, West End', False, 'Available', True),
            (user_ids[6], 'David Miller', 'david.miller@secondary.com', '555-0207', 'Automotive', 'Mechanic', 'Master', 15.0, 4.9, 203, 'Auto repair and maintenance expert with dealership experience', 80.00, 'City Wide', True, 'Available', True),
            (user_ids[7], 'Carlos Reyes', 'carlos.reyes@secondary.com', '555-0208', 'Electrical', 'Electrician', 'Professional', 9.0, 4.6, 120, 'Journeyman electrician with commercial and residential experience', 58.00, 'City Wide', True, 'Available', True),
            (user_ids[8], 'Nina Patel', 'nina.patel@secondary.com', '555-0209', 'Solar', 'Solar Installer', 'Professional', 6.0, 4.7, 86, 'Solar panel installation and maintenance specialist', 60.00, 'Southwest, All Areas', True, 'Available', True),
            (user_ids[9], 'Marcus Chen', 'marcus.chen@secondary.com', '555-0210', 'Glass Work', 'Glazier', 'Professional', 8.0, 4.6, 73, 'Window and storefront glass installation specialist', 55.00, 'Pacific Northwest, Downtown', False, 'Available', True)
        ]

        cursor.executemany("""
            INSERT INTO EMPLOYEE (user_id, name, email, phone, specialization, job_type, certification_level, experience_years, rating, total_completed_orders, bio, avg_cost_per_hour, preferred_regions, emergency_service, availability_status, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, employees_data)

        # Insert sample customers
        customers_data = [
            ('CUST004', 'Alice Cooper', 'alice.cooper@email.com', '555-1001', '123 Main St', 100, 5, 750.00, 'Downtown', 'Silver', 'customer123'),
            ('CUST005', 'Bob Thompson', 'bob.thompson@email.com', '555-1002', '456 Oak Ave', 50, 3, 400.00, 'Suburbs', 'Bronze', 'customer123'),
            ('CUST006', 'Carol White', 'carol.white@email.com', '555-1003', '789 Pine Rd', 25, 2, 200.00, 'East Side', 'Bronze', 'customer123')
        ]

        cursor.executemany("""
            INSERT INTO CUSTOMER (customer_code, name, email, phone, address, loyalty_points, total_orders, total_spent, preferred_regions, membership_level, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, customers_data)

        connection.commit()

        # Verify data was inserted
        tables_to_check = ['SERVICE_TYPE', '"USER"', 'EMPLOYEE', 'CUSTOMER', 'ORDER_TABLE', 'FEEDBACK']
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"[OK] {table}: {count} records")

        print(f"[OK] Secondary database setup complete!")

    except (DatabaseError, OperationalError) as e:
        print(f"Error setting up secondary database: {e}")
        if 'connection' in locals():
            connection.rollback()
        return False

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return True

def test_database_connection():
    """Test database connection and basic functionality"""
    print("\nTesting secondary laptop database connection...")

    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Test all required tables
        tables = ['SERVICE_TYPE', '"USER"', 'EMPLOYEE', 'CUSTOMER', 'ORDER_TABLE', 'FEEDBACK']

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"[OK] {table}: {count} records")

        # Test search functionality
        print("\nTesting search functionality...")
        cursor.execute("""
            SELECT e.*, u.phone, u.email, u.address
            FROM EMPLOYEE e
            JOIN "USER" u ON e.user_id = u.user_id
            WHERE e.is_active = 1 AND e.specialization LIKE %s
            ORDER BY e.rating DESC
            LIMIT 3
        """, ('%plumbing%',))

        employees = cursor.fetchall()
        print(f"[OK] Found {len(employees)} plumbing specialists")

        cursor.close()
        connection.close()
        return True

    except (DatabaseError, OperationalError) as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("Enhanced Service Booking System - Secondary Laptop Setup")
    print("This configures the Individual Workers database")

    # Setup database
    if not setup_secondary_database():
        print("\n[ERROR] Database setup failed!")
        sys.exit(1)

    # Test connection
    if not test_database_connection():
        print("\n[ERROR] Database connection test failed!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("SECONDARY LAPTOP SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nWhat has been configured:")
    print("• Individual Workers Database (service_booking_secondary)")
    print("• Sample individual workers with different specializations")
    print("• Order management system")
    print("• Customer management")
    print("• Cross-database search capability")
    print("\nTo run the secondary laptop application:")
    print("python secondary_app.py")
    print("\nDefault worker credentials:")
    print("Email: john.smith@secondary.com")
    print("Password: worker123")
    print("\nConnection Configuration:")
    print("• Local Database: service_booking_secondary (Employees)")
    print("• Remote Database: service_booking_primary (Companies)")
    print("• Remote IP: 192.168.228.198 (Primary Laptop)")
    print("• Mode: Distributed (Local Employees + Remote Companies)")

if __name__ == "__main__":
    main()