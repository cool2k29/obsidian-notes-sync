#!/usr/bin/env python3
"""
Sync markdown files to PostgreSQL database
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'admin',
    'password': 'admin123',
    'dbname': 'trainingdb'
}

PROJECT_NAME = 'obsidian-notes-sync'


def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def create_documents_table(conn):
    """Create documents table if it doesn't exist"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS documents (
        id BIGSERIAL PRIMARY KEY,
        project TEXT NOT NULL,
        path TEXT UNIQUE NOT NULL,
        title TEXT,
        content TEXT NOT NULL,
        architecture TEXT,
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """
    
    # Add architecture column if it doesn't exist (for existing tables)
    alter_table_sql = """
    ALTER TABLE documents 
    ADD COLUMN IF NOT EXISTS architecture TEXT;
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            cursor.execute(alter_table_sql)
            conn.commit()
            print("✓ Table 'documents' created or already exists with architecture column")
    except psycopg2.Error as e:
        print(f"Error creating table: {e}")
        conn.rollback()
        raise


def extract_title_from_content(content):
    """Extract title from markdown content (first # heading or first line)"""
    lines = content.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        # Look for markdown heading
        if line.startswith('#'):
            # Remove # symbols and return the title
            title = line.lstrip('#').strip()
            if title:
                return title
        # Skip empty lines
        elif line:
            # Return first non-empty line if no heading found
            return line[:100]  # Limit title length
    
    return "Untitled"


def find_markdown_files(base_path):
    """Find all .md files in the project directory"""
    markdown_files = []
    base_path = Path(base_path)
    
    for md_file in base_path.rglob('*.md'):
        relative_path = md_file.relative_to(base_path)
        markdown_files.append({
            'absolute_path': str(md_file),
            'relative_path': str(relative_path)
        })
    
    return markdown_files


def determine_architecture(path):
    """Determine architecture based on file path"""
    if '2-詳細設計' in path:
        return '詳細'
    elif 'テスト' in path:
        return 'テスト'
    elif 'データベース' in path:
        return 'データベース'
    elif '1-要件定義' in path:
        return '要件'
    else:
        return None


def upsert_document(conn, file_info):
    """Insert or update a document in the database"""
    try:
        # Read file content
        with open(file_info['absolute_path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from content
        title = extract_title_from_content(content)
        
        # Determine architecture based on path
        architecture = determine_architecture(file_info['relative_path'])
        
        # Upsert query using INSERT ... ON CONFLICT
        upsert_sql = """
        INSERT INTO documents (project, path, title, content, architecture, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (path) 
        DO UPDATE SET
            project = EXCLUDED.project,
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            architecture = EXCLUDED.architecture,
            updated_at = EXCLUDED.updated_at
        RETURNING id, path;
        """
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(upsert_sql, (
                PROJECT_NAME,
                file_info['relative_path'],
                title,
                content,
                architecture,
                datetime.now()
            ))
            result = cursor.fetchone()
            conn.commit()
            
            return result
            
    except Exception as e:
        print(f"Error processing file {file_info['relative_path']}: {e}")
        conn.rollback()
        return None


def main():
    """Main function to sync markdown files to PostgreSQL"""
    print("Starting markdown files sync to PostgreSQL...")
    print(f"Project: {PROJECT_NAME}")
    print("-" * 50)
    
    # Connect to database
    conn = connect_to_database()
    print(f"✓ Connected to database: {DB_CONFIG['dbname']}")
    
    try:
        # Create table if not exists
        create_documents_table(conn)
        
        # Find all markdown files
        base_path = os.path.dirname(os.path.abspath(__file__))
        markdown_files = find_markdown_files(base_path)
        print(f"✓ Found {len(markdown_files)} markdown files")
        print("-" * 50)
        
        # Process each file
        success_count = 0
        for file_info in markdown_files:
            result = upsert_document(conn, file_info)
            if result:
                success_count += 1
                print(f"✓ Synced: {file_info['relative_path']} (ID: {result['id']})")
            else:
                print(f"✗ Failed: {file_info['relative_path']}")
        
        print("-" * 50)
        print(f"Sync completed: {success_count}/{len(markdown_files)} files processed successfully")
        
        # Show summary
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as total_docs,
                       COUNT(DISTINCT project) as projects
                FROM documents
                WHERE project = %s
            """, (PROJECT_NAME,))
            summary = cursor.fetchone()
            print(f"Database now contains {summary['total_docs']} documents for project '{PROJECT_NAME}'")
        
    except Exception as e:
        print(f"Error during sync: {e}")
        sys.exit(1)
    finally:
        conn.close()
        print("✓ Database connection closed")


if __name__ == "__main__":
    main()