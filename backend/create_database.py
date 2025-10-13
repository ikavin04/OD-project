#!/usr/bin/env python3
"""
Script to create the OD database in PostgreSQL
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    try:
        # Connect to postgres database (default)
        conn = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="Manisha14"
        )
        
        # Set isolation level to autocommit for database creation
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'OD'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'OD' already exists!")
        else:
            # Create database
            cursor.execute('CREATE DATABASE "OD"')
            print("✅ Database 'OD' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    if create_database():
        print("✅ Ready to initialize the OD database!")
    else:
        print("❌ Failed to create database. Please check your PostgreSQL connection.")
        sys.exit(1)