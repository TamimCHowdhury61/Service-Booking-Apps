#!/usr/bin/env python3
"""

This script will automatically run the SQL setup files on both laptops
"""

import mysql.connector
from mysql.connector import Error
import subprocess
import sys
import os
from datetime import datetime

def check_mysql_client():
    """Check if MySQL client is available"""
    try:
        result = subprocess.run(['mysql', '--version'],
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def run_sql_file_with_client(sql_file, mysql_host='localhost', mysql_user='root', mysql_password='12345678'):
    """Run SQL file using MySQL client command line"""
    try:
        # Check if file exists
        if not os.path.exists(sql_file):
            print(f"❌ SQL file not found: {sql_file}")
            return False

        print(f"🔧 Running SQL file: {sql_file}")
        print(f"   Host: {mysql_host}")
        print(f"   User: {mysql_user}")

        # Use subprocess to run mysql client
        cmd = [
            'mysql',
            f'--host={mysql_host}',
            f'--user={mysql_user}',
            f'--password={mysql_password}',
            f'--execute=source {sql_file}'
        ]

        # Set environment variable for password (more secure)
        env = os.environ.copy()
        env['MYSQL_PWD'] = mysql_password

        try:
            result = subprocess.run(
                ['mysql', f'--host={mysql_host}', f'--user={mysql_user}', f'--default-character-set=utf8mb4'],
                input=open(sql_file, 'r').read(),
                text=True,
                timeout=300,  # 5 minute timeout
                env=env,
                capture_output=True
            )

            if result.returncode == 0:
                print(f"✅ SQL file executed successfully!")
                if result.stdout:
                    print(f"📄 Output: {result.stdout[:200]}...")
                return True
            else:
                print(f"❌ SQL execution failed!")
                print(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"❌ SQL execution timed out (5 minutes)")
            return False

    except FileNotFoundError:
        print(f"❌ MySQL client not found. Please install MySQL client tools.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error running SQL file: {str(e)}")
        return False

def setup_database_with_python(sql_file, mysql_host='localhost', mysql_user='root', mysql_password='12345678'):
    """Setup database using Python MySQL connector"""
    try:
        print(f"🔧 Setting up database using Python connector")
        print(f"   Host: {mysql_host}")
        print(f"   User: {mysql_user}")

        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4',
            connect_timeout=30
        )

        if not connection.is_connected():
            print("❌ Failed to connect to MySQL server")
            return False

        # Read and execute SQL file
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        cursor = connection.cursor()

        # Split SQL file into individual statements
        statements = []
        current_statement = ""

        for line in sql_content.split('\n'):
            line = line.strip()

            # Skip comments and empty lines
            if line.startswith('--') or not line:
                continue

            current_statement += line + " "

            # If statement ends with semicolon, add to statements
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""

        # Add the last statement if it doesn't end with semicolon
        if current_statement.strip():
            statements.append(current_statement.strip())

        print(f"📝 Found {len(statements)} SQL statements to execute")

        # Execute each statement
        executed_count = 0
        error_count = 0

        for i, statement in enumerate(statements):
            try:
                # Skip empty statements
                if not statement or statement == ';':
                    continue

                cursor.execute(statement)
                executed_count += 1

                # Show progress for every 10 statements
                if (executed_count % 10) == 0:
                    print(f"   Executed {executed_count} statements...")

            except Error as e:
                # Some errors are expected (like CREATE TABLE IF NOT EXISTS)
                if "already exists" in str(e) or "Duplicate entry" in str(e):
                    # This is expected, continue
                    continue
                else:
                    error_count += 1
                    print(f"⚠️  SQL Warning: {str(e)[:100]}...")

        connection.commit()
        cursor.close()
        connection.close()

        print(f"✅ Database setup completed!")
        print(f"   Executed: {executed_count} statements")
        print(f"   Warnings: {error_count}")

        return True

    except Error as e:
        print(f"❌ MySQL Error: {str(e)}")
        return False
    except FileNotFoundError:
        print(f"❌ SQL file not found: {sql_file}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_database_connection(mysql_host='localhost', mysql_user='root', mysql_password='12345678', database_name='test'):
    """Test if we can connect to MySQL"""
    try:
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=database_name,
            connect_timeout=10
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            cursor.close()
            connection.close()

            print(f"✅ MySQL Connection Test: SUCCESS")
            print(f"   Version: {version}")
            print(f"   Host: {mysql_host}")
            print(f"   User: {mysql_user}")

            return True
        else:
            print("❌ MySQL Connection Test: FAILED")
            return False

    except Error as e:
        print(f"❌ MySQL Connection Error: {str(e)}")
        return False

def main():
    """Main execution function"""
    print("🚀 Automated Database Setup")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check which setup to run
    if len(sys.argv) > 1:
        setup_type = sys.argv[1].lower()
    else:
        print("\n🔧 What would you like to setup?")
        print("1. Primary database (companies)")
        print("2. Secondary database (workers)")
        print("3. Both databases")
        print("4. Test MySQL connection only")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == '1':
            setup_type = 'primary'
        elif choice == '2':
            setup_type = 'secondary'
        elif choice == '3':
            setup_type = 'both'
        elif choice == '4':
            setup_type = 'test'
        else:
            print("❌ Invalid choice")
            return 1

    # Get connection details
    print(f"\n🔧 Database Connection Details:")
    mysql_host = input("MySQL host (default: localhost): ").strip() or 'localhost'
    mysql_user = input("MySQL user (default: root): ").strip() or 'root'
    mysql_password = input("MySQL password (default: 12345678): ").strip() or '12345678'

    # Test basic MySQL connection first
    print(f"\n🔍 Testing MySQL connection...")
    if not test_database_connection(mysql_host, mysql_user, mysql_password):
        print(f"\n❌ Cannot connect to MySQL server!")
        print(f"Please check:")
        print(f"1. MySQL server is running")
        print(f"2. Connection details are correct")
        print(f"3. User has necessary permissions")
        return 1

    # Check if MySQL client is available
    use_mysql_client = check_mysql_client()
    if use_mysql_client:
        print(f"✅ MySQL client found - using for faster setup")
    else:
        print(f"⚠️  MySQL client not found - using Python connector")

    setup_success = True

    # Run based on setup type
    if setup_type == 'test':
        print(f"\n✅ MySQL connection test completed successfully!")
        return 0

    elif setup_type in ['primary', 'both']:
        print(f"\n🔧 Setting up PRIMARY database (companies)...")
        sql_file = 'setup_primary_database.sql'

        if os.path.exists(sql_file):
            if use_mysql_client:
                success = run_sql_file_with_client(sql_file, mysql_host, mysql_user, mysql_password)
            else:
                success = setup_database_with_python(sql_file, mysql_host, mysql_user, mysql_password)

            if success:
                print(f"✅ Primary database setup completed!")

                # Test connection to primary database
                if test_database_connection(mysql_host, mysql_user, mysql_password, 'service_booking_primary'):
                    print(f"✅ Primary database connection test: SUCCESS")
                else:
                    print(f"⚠️  Primary database connection test: FAILED")
                    setup_success = False
            else:
                print(f"❌ Primary database setup FAILED!")
                setup_success = False
        else:
            print(f"❌ Primary database SQL file not found: {sql_file}")
            setup_success = False

    elif setup_type in ['secondary', 'both']:
        print(f"\n🔧 Setting up SECONDARY database (workers)...")
        sql_file = 'setup_secondary_database.sql'

        if os.path.exists(sql_file):
            if use_mysql_client:
                success = run_sql_file_with_client(sql_file, mysql_host, mysql_user, mysql_password)
            else:
                success = setup_database_with_python(sql_file, mysql_host, mysql_user, mysql_password)

            if success:
                print(f"✅ Secondary database setup completed!")

                # Test connection to secondary database
                if test_database_connection(mysql_host, mysql_user, mysql_password, 'service_booking_secondary'):
                    print(f"✅ Secondary database connection test: SUCCESS")
                else:
                    print(f"⚠️  Secondary database connection test: FAILED")
                    setup_success = False
            else:
                print(f"❌ Secondary database setup FAILED!")
                setup_success = False
        else:
            print(f"❌ Secondary database SQL file not found: {sql_file}")
            setup_success = False

    # Final summary
    print(f"\n" + "="*50)
    print(f"📊 SETUP SUMMARY")
    print(f"="*50)

    if setup_success:
        print(f"🎉 Database setup completed successfully!")
        print(f"")
        print(f"📝 Next Steps:")
        print(f"1. Run connection test: python quick_connection_test.py")
        print(f"2. Run comprehensive test: python database_connection_test.py")
        print(f"3. Start your distributed application")

        if setup_type == 'primary':
            print(f"4. Copy this setup to secondary laptop and run 'python run_database_setup.py secondary'")
        elif setup_type == 'secondary':
            print(f"4. Test connection to primary laptop database")

        return 0
    else:
        print(f"❌ Database setup encountered errors!")
        print(f"")
        print(f"🔧 Troubleshooting:")
        print(f"1. Check MySQL server is running")
        print(f"2. Verify user permissions")
        print(f"3. Check SQL files exist and are readable")
        print(f"4. Review error messages above")
        print(f"5. Run: python database_connection_test.py for detailed diagnostics")

        return 1

if __name__ == "__main__":
    # Help option
    if '--help' in sys.argv or '-h' in sys.argv:
        print("🚀 Automated Database Setup")
        print("="*50)
        print("Usage:")
        print("  python run_database_setup.py                    # Interactive mode")
        print("  python run_database_setup.py primary            # Setup primary database")
        print("  python run_database_setup.py secondary          # Setup secondary database")
        print("  python run_database_setup.py both               # Setup both databases")
        print("  python run_database_setup.py test               # Test connection only")
        print("  python run_database_setup.py --help             # Show this help")
        print("")
        print("What this does:")
        print("  - Creates MySQL databases and tables")
        print("  - Inserts sample data")
        print("  - Creates users for remote access")
        print("  - Tests database connections")
        print("")
        print("Requirements:")
        print("  - MySQL server running")
        print("  - Python mysql-connector-python (pip install mysql-connector-python)")
        print("  - MySQL client tools (optional, for faster setup)")
        sys.exit(0)

    exit_code = main()
    sys.exit(exit_code)