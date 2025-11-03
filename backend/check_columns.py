#!/usr/bin/env python3
from main import app, db
from sqlalchemy import text

def check_columns():
    with app.app_context():
        # Check column names
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'od_requests' 
            AND (column_name LIKE '%proof%' OR column_name LIKE '%certificate%') 
            ORDER BY column_name;
        """))
        
        print('Database columns:')
        for row in result:
            print(f'  {row[0]}')

if __name__ == "__main__":
    check_columns()