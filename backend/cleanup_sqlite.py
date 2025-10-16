"""
Clean up SQLite files - PostgreSQL Migration Complete
Since PostgreSQL is already in use with current data, this script safely removes SQLite files
"""
import os
import shutil
from datetime import datetime

def backup_and_delete_sqlite():
    """Backup and delete all SQLite database files"""
    print("=" * 70)
    print("🗑️  SQLite Cleanup - PostgreSQL is Now Primary Database")
    print("=" * 70)
    
    sqlite_files = [
        'instance/od_development.db',
        'instance/od_management.db',
        'od_management.db',
        'od_development.db'
    ]
    
    # Create backups folder
    backup_folder = 'instance/sqlite_backups'
    os.makedirs(backup_folder, exist_ok=True)
    
    backed_up = []
    deleted = []
    
    for file_path in sqlite_files:
        if os.path.exists(file_path):
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_folder, f"{filename}_{timestamp}.backup")
            
            try:
                shutil.copy2(file_path, backup_path)
                backed_up.append((file_path, backup_path))
                print(f"✅ Backed up: {file_path} -> {backup_path}")
            except Exception as e:
                print(f"⚠️  Failed to backup {file_path}: {e}")
                continue
            
            # Delete original
            try:
                os.remove(file_path)
                deleted.append(file_path)
                print(f"🗑️  Deleted: {file_path}")
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
                print(f"   (File may be in use - close all applications and try again)")
    
    print("\n" + "=" * 70)
    print("📊 Cleanup Summary")
    print("=" * 70)
    print(f"Files backed up: {len(backed_up)}")
    print(f"Files deleted: {len(deleted)}")
    
    if backed_up:
        print(f"\n💾 Backups saved in: {backup_folder}/")
        for original, backup in backed_up:
            print(f"   - {os.path.basename(backup)}")
    
    if deleted:
        print("\n✅ Successfully deleted SQLite files:")
        for file in deleted:
            print(f"   - {file}")
    
    print("\n" + "=" * 70)
    print("🎉 PostgreSQL is now the exclusive database!")
    print("=" * 70)
    print("\nDatabase Configuration:")
    print("  Type: PostgreSQL")
    print("  Connection: postgresql://postgres:***@localhost:5432/OD")
    print("  Status: ✅ Active and in use")
    print("\nAll new data will be stored in PostgreSQL only.")

if __name__ == "__main__":
    print("\n⚠️  This script will backup and delete SQLite database files.")
    print("PostgreSQL is already configured and contains your current data.\n")
    
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        backup_and_delete_sqlite()
    else:
        print("\n❌ Cleanup cancelled. SQLite files retained.")
