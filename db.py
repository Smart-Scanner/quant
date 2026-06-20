"""Database layer - Supabase + SQLite dual-backend support."""

import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Any

class Database:
    """Dual-backend database abstraction layer."""
    
    def __init__(self):
        self.db_url = os.environ.get("DATABASE_URL")
        self.use_pg = self.db_url is not None
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database connection."""
        if self.use_pg:
            try:
                import psycopg2
                self.conn = psycopg2.connect(self.db_url)
            except Exception as e:
                print(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
                self.use_pg = False
        
        if not self.use_pg:
            self.conn = sqlite3.connect("scanner.db", check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._init_sqlite_schema()
    
    def _init_sqlite_schema(self):
        """Initialize SQLite schema."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                symbol TEXT PRIMARY KEY,
                data JSON,
                high_conviction INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.conn.commit()
    
    def execute_db(self, query: str, params: tuple = (), fetch: str = None):
        """Execute database query."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            
            if fetch == "one":
                return dict(cursor.fetchone() or {})
            elif fetch == "all":
                return [dict(row) for row in cursor.fetchall()]
            elif fetch == "rowcount":
                self.conn.commit()
                return cursor.rowcount
            else:
                self.conn.commit()
                return True
        except Exception as e:
            print(f"DB error: {e}")
            return None
    
    def get_meta(self, key: str, default: str = None) -> Optional[str]:
        """Get metadata value."""
        result = self.execute_db("SELECT value FROM meta WHERE key = ?", (key,), fetch="one")
        return result.get("value") if result else default
    
    def set_meta(self, key: str, value: str):
        """Set metadata value."""
        self.execute_db(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL."""
        return self.use_pg
    
    def pg_cooldown_active(self) -> bool:
        """Check if PostgreSQL is in cooldown."""
        return False

db = Database()
