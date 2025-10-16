# SQLite to PostgreSQL Migration Guide

## Overview
This guide will help you migrate your OD Management System from SQLite to PostgreSQL and ensure all future data uses PostgreSQL exclusively.

## Prerequisites

1. **PostgreSQL installed and running**
   - Default connection: `postgresql://postgres:Manisha14@localhost:5432/OD`
   - Database name: `OD`

2. **Python packages installed**
   ```bash
   pip install sqlalchemy psycopg2-binary python-dotenv
   ```

3. **Backup your data** (automatic backup is created during migration)

## Migration Steps

### Step 1: Verify PostgreSQL Connection

Test your PostgreSQL connection:
```bash
cd backend
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:Manisha14@localhost:5432/OD'); print('Connection successful!' if engine.connect() else 'Connection failed')"
```

### Step 2: Run the Migration Script

```bash
cd backend
python migrate_sqlite_to_postgres.py
```

The script will:
1. ✅ Check if SQLite database exists
2. ✅ Verify PostgreSQL connection
3. ✅ Create automatic backup of SQLite database
4. ✅ Migrate all tables and data
5. ✅ Show migration summary
6. ✅ Optionally delete SQLite files

### Step 3: Verify Migration

Check if data was migrated successfully:
```bash
python -c "from main import app, db, Student, Faculty, ODRequest; app.app_context().push(); print(f'Students: {Student.query.count()}'); print(f'Faculty: {Faculty.query.count()}'); print(f'OD Requests: {ODRequest.query.count()}')"
```

### Step 4: Update Configuration (Already Done)

The application has been updated to use PostgreSQL exclusively:
- ✅ `main.py` - Already configured for PostgreSQL
- ✅ `app/__init__.py` - Updated to use PostgreSQL
- ✅ `.env` file - Contains PostgreSQL configuration

## What Changed

### Before Migration
```python
# SQLite (old)
SQLALCHEMY_DATABASE_URI = 'sqlite:///od_management.db'
```

### After Migration
```python
# PostgreSQL (new)
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Manisha14@localhost:5432/OD'
```

## Files to be Deleted

After successful migration, the following SQLite files will be removed:
- `instance/od_development.db`
- `instance/od_management.db`
- `od_management.db` (if exists)

**Backups are saved as:** `instance/od_development_backup_YYYYMMDD_HHMMSS.db`

## Troubleshooting

### PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
# Windows:
net start postgresql-x64-14

# Check connection details in .env file
DATABASE_URL=postgresql://postgres:Manisha14@localhost:5432/OD
```

### Migration Failed
1. Check PostgreSQL logs
2. Verify database exists: `createdb -U postgres OD`
3. Ensure tables exist in PostgreSQL (run migrations first)
4. Check file permissions

### Rollback (If Needed)
If migration fails, your backup is safe:
```bash
# Restore from backup
cp instance/od_development_backup_*.db instance/od_development.db
```

## Post-Migration Checklist

- [ ] Migration script ran successfully
- [ ] All tables migrated (check console output)
- [ ] Data count matches between SQLite and PostgreSQL
- [ ] SQLite files deleted (or backed up)
- [ ] Application starts without errors
- [ ] Can create new records in PostgreSQL
- [ ] Can query existing migrated data

## Database Schema

The PostgreSQL database now contains all tables from the OD Management System:
- `students` - Student accounts and information
- `faculty` - Faculty accounts and information  
- `od_requests` - OD applications with proof submission tracking
- And other system tables

## Environment Variables

Ensure your `.env` file has the correct PostgreSQL configuration:
```env
DATABASE_URL=postgresql://postgres:Manisha14@localhost:5432/OD
```

## Benefits of PostgreSQL

✅ Better performance for concurrent users
✅ Advanced features (full-text search, JSON support)
✅ Better data integrity with ACID compliance
✅ Production-ready and scalable
✅ Better support for complex queries
✅ No file locking issues

## Next Steps

1. Test all application features
2. Verify proof submission system works
3. Test email notifications
4. Check file uploads
5. Verify authentication works

## Support

If you encounter issues:
1. Check PostgreSQL service is running
2. Verify database credentials in `.env`
3. Check migration logs for errors
4. Review backup files if rollback needed

---

**Note:** This migration is one-way. Once completed and SQLite files are deleted, you'll use PostgreSQL exclusively. Always keep backups!
