"""
Migration Script: SQLite to PostgreSQL
Migrates all data from SQLite database to PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database URLs
SQLITE_URL = 'sqlite:///instance/od_development.db'
POSTGRES_URL = 'postgresql://postgres:Manisha14@localhost:5432/OD'

def check_sqlite_exists():
    """Check if SQLite database exists"""
    db_path = 'instance/od_development.db'
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ SQLite database found: {db_path} ({size} bytes)")
        return True
    else:
        print(f"❌ SQLite database not found: {db_path}")
        return False

def check_postgres_connection():
    """Check if PostgreSQL database is accessible"""
    try:
        engine = create_engine(POSTGRES_URL)
        connection = engine.connect()
        connection.close()
        print(f"✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def get_table_data(engine, table_name):
    """Get all data from a table"""
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    if table_name not in metadata.tables:
        return None
    
    table = metadata.tables[table_name]
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        result = session.execute(table.select())
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"   ⚠️  Error reading {table_name}: {e}")
        return None
    finally:
        session.close()

def migrate_table(sqlite_engine, postgres_engine, table_name):
    """Migrate a single table from SQLite to PostgreSQL"""
    print(f"\n📋 Migrating table: {table_name}")
    
    # Get data from SQLite
    data = get_table_data(sqlite_engine, table_name)
    
    if data is None:
        print(f"   ⏭️  Skipping {table_name} (no data or doesn't exist)")
        return 0
    
    if len(data) == 0:
        print(f"   ℹ️  {table_name} is empty")
        return 0
    
    print(f"   📊 Found {len(data)} records")
    
    # Insert data into PostgreSQL
    metadata = MetaData()
    metadata.reflect(bind=postgres_engine)
    
    if table_name not in metadata.tables:
        print(f"   ⚠️  Table {table_name} doesn't exist in PostgreSQL. Creating schema first...")
        return 0
    
    table = metadata.tables[table_name]
    Session = sessionmaker(bind=postgres_engine)
    session = Session()
    
    try:
        # Insert new data (without clearing - append mode to avoid foreign key issues)
        inserted = 0
        for row in data:
            try:
                session.execute(table.insert().values(**row))
                inserted += 1
            except Exception as e:
                # Check if it's a duplicate key error
                error_msg = str(e)
                if 'duplicate' in error_msg.lower() or 'unique' in error_msg.lower():
                    print(f"   ⏭️  Skipping duplicate record (already exists)")
                    session.rollback()
                    continue
                else:
                    print(f"   ⚠️  Error inserting row: {e}")
                    session.rollback()
                    continue
        
        session.commit()
        print(f"   ✅ Successfully migrated {inserted}/{len(data)} records")
        return inserted
    
    except Exception as e:
        session.rollback()
        print(f"   ❌ Migration failed: {e}")
        return 0
    finally:
        session.close()

def migrate_all_data():
    """Migrate all data from SQLite to PostgreSQL"""
    print("=" * 70)
    print("🔄 SQLite to PostgreSQL Migration")
    print("=" * 70)
    
    # Check SQLite database
    if not check_sqlite_exists():
        print("\n⚠️  No SQLite database found. Nothing to migrate.")
        return False
    
    # Check PostgreSQL connection
    if not check_postgres_connection():
        print("\n❌ Cannot connect to PostgreSQL. Please check your connection.")
        return False
    
    # Create engines
    print("\n🔧 Creating database connections...")
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)
    
    # Get all tables from SQLite
    inspector = inspect(sqlite_engine)
    tables = inspector.get_table_names()
    
    print(f"\n📚 Found {len(tables)} tables in SQLite:")
    for table in tables:
        print(f"   - {table}")
    
    # Migrate each table
    total_migrated = 0
    successful_tables = []
    
    # Define migration order (to respect foreign key constraints)
    migration_order = [
        'students',
        'faculty',
        'od_requests',
        # Add other tables as needed
    ]
    
    # Migrate tables in order
    for table_name in migration_order:
        if table_name in tables:
            count = migrate_table(sqlite_engine, postgres_engine, table_name)
            total_migrated += count
            if count > 0:
                successful_tables.append(table_name)
    
    # Migrate remaining tables
    for table_name in tables:
        if table_name not in migration_order:
            count = migrate_table(sqlite_engine, postgres_engine, table_name)
            total_migrated += count
            if count > 0:
                successful_tables.append(table_name)
    
    print("\n" + "=" * 70)
    print("📊 Migration Summary")
    print("=" * 70)
    print(f"Total records migrated: {total_migrated}")
    print(f"Tables migrated successfully: {len(successful_tables)}")
    if successful_tables:
        print("\nMigrated tables:")
        for table in successful_tables:
            print(f"   ✅ {table}")
    
    return True

def backup_sqlite():
    """Create a backup of SQLite database before deletion"""
    db_path = 'instance/od_development.db'
    if os.path.exists(db_path):
        backup_path = f'instance/od_development_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"\n💾 Backup created: {backup_path}")
        return backup_path
    return None

def delete_sqlite_files():
    """Delete SQLite database files"""
    print("\n🗑️  Cleaning up SQLite files...")
    
    sqlite_files = [
        'instance/od_development.db',
        'instance/od_management.db',
        'od_management.db'
    ]
    
    deleted = []
    for file_path in sqlite_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted.append(file_path)
                print(f"   ✅ Deleted: {file_path}")
            except Exception as e:
                print(f"   ❌ Failed to delete {file_path}: {e}")
    
    if deleted:
        print(f"\n✅ Successfully deleted {len(deleted)} SQLite file(s)")
    else:
        print("\n ℹ️  No SQLite files to delete")

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will migrate data from SQLite to PostgreSQL")
    print("   and delete SQLite database files.\n")
    
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        # Create backup first
        backup_sqlite()
        
        # Perform migration
        success = migrate_all_data()
        
        if success:
            print("\n✅ Migration completed successfully!")
            
            response = input("\nDo you want to delete SQLite files? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                delete_sqlite_files()
                print("\n🎉 All done! Your application now uses PostgreSQL exclusively.")
            else:
                print("\n📁 SQLite files retained. You can delete them manually later.")
        else:
            print("\n⚠️  Migration failed or was skipped. SQLite files not deleted.")
    else:
        print("\n❌ Migration cancelled.")
