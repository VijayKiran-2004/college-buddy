"""
Analytics System for College Chatbot
Tracks queries, performance, cache effectiveness, and usage patterns
"""

import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path


class AnalyticsSystem:
    """Track chatbot usage and performance metrics"""
    
    def __init__(self, db_path='app/database/analytics.db'):
        """Initialize analytics system with SQLite database"""
        self.db_path = db_path
        
        # Create database directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create analytics tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Queries table - log every query
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query TEXT NOT NULL,
                tool_used TEXT,
                response_time_ms INTEGER,
                success BOOLEAN,
                cached BOOLEAN,
                error TEXT
            )
        """)
        
        # Daily stats table - aggregated daily metrics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_queries INTEGER DEFAULT 0,
                successful_queries INTEGER DEFAULT 0,
                failed_queries INTEGER DEFAULT 0,
                cache_hits INTEGER DEFAULT 0,
                avg_response_time_ms INTEGER DEFAULT 0
            )
        """)
        
        # Popular queries table - track most asked questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS popular_queries (
                query_normalized TEXT PRIMARY KEY,
                count INTEGER DEFAULT 1,
                last_asked DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_query(self, query: str, tool_used: str, response_time_ms: int, 
                  success: bool, cached: bool = False, error: str = None):
        """Log a single query with metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert query log
            cursor.execute("""
                INSERT INTO queries (query, tool_used, response_time_ms, success, cached, error)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (query, tool_used, response_time_ms, success, cached, error))
            
            # Update daily stats
            today = datetime.now().date()
            cursor.execute("""
                INSERT INTO daily_stats (date, total_queries, successful_queries, failed_queries, cache_hits)
                VALUES (?, 1, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    total_queries = total_queries + 1,
                    successful_queries = successful_queries + ?,
                    failed_queries = failed_queries + ?,
                    cache_hits = cache_hits + ?
            """, (today, 1 if success else 0, 0 if success else 1, 1 if cached else 0,
                  1 if success else 0, 0 if success else 1, 1 if cached else 0))
            
            # Update popular queries
            query_normalized = query.lower().strip()
            cursor.execute("""
                INSERT INTO popular_queries (query_normalized, count, last_asked)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(query_normalized) DO UPDATE SET
                    count = count + 1,
                    last_asked = CURRENT_TIMESTAMP
            """, (query_normalized,))
            
            conn.commit()
            conn.close()
        
        except Exception as e:
            print(f"Analytics logging error: {e}")
    
    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics for last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Total queries
            cursor.execute("""
                SELECT COUNT(*) FROM queries 
                WHERE DATE(timestamp) BETWEEN ? AND ?
            """, (start_date, end_date))
            total_queries = cursor.fetchone()[0]
            
            # Success rate
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
                FROM queries 
                WHERE DATE(timestamp) BETWEEN ? AND ?
            """, (start_date, end_date))
            successful, failed = cursor.fetchone()
            
            # Cache hit rate
            cursor.execute("""
                SELECT COUNT(*) FROM queries 
                WHERE cached = 1 AND DATE(timestamp) BETWEEN ? AND ?
            """, (start_date, end_date))
            cache_hits = cursor.fetchone()[0]
            
            # Average response time
            cursor.execute("""
                SELECT AVG(response_time_ms) FROM queries 
                WHERE DATE(timestamp) BETWEEN ? AND ?
            """, (start_date, end_date))
            avg_response_time = cursor.fetchone()[0] or 0
            
            # Tool usage distribution
            cursor.execute("""
                SELECT tool_used, COUNT(*) as count 
                FROM queries 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY tool_used 
                ORDER BY count DESC
            """, (start_date, end_date))
            tool_usage = dict(cursor.fetchall())
            
            # Top 10 queries
            cursor.execute("""
                SELECT query_normalized, count 
                FROM popular_queries 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_queries = cursor.fetchall()
            
            conn.close()
            
            return {
                "period_days": days,
                "total_queries": total_queries,
                "successful": successful or 0,
                "failed": failed or 0,
                "success_rate": round((successful or 0) / total_queries * 100, 2) if total_queries > 0 else 0,
                "cache_hits": cache_hits,
                "cache_hit_rate": round(cache_hits / total_queries * 100, 2) if total_queries > 0 else 0,
                "avg_response_time_ms": round(avg_response_time, 2),
                "tool_usage": tool_usage,
                "top_queries": top_queries
            }
        
        except Exception as e:
            print(f"Analytics stats error: {e}")
            return {}
    
    def get_recent_queries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent queries with details"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, query, tool_used, response_time_ms, success, cached, error
                FROM queries 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "query": row[1],
                    "tool_used": row[2],
                    "response_time_ms": row[3],
                    "success": bool(row[4]),
                    "cached": bool(row[5]),
                    "error": row[6]
                }
                for row in rows
            ]
        
        except Exception as e:
            print(f"Analytics recent queries error: {e}")
            return []
    
    def get_failed_queries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent failed queries for debugging"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, query, tool_used, error
                FROM queries 
                WHERE success = 0
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "query": row[1],
                    "tool_used": row[2],
                    "error": row[3]
                }
                for row in rows
            ]
        
        except Exception as e:
            print(f"Analytics failed queries error: {e}")
            return []


if __name__ == "__main__":
    # Test analytics system
    analytics = AnalyticsSystem()
    
    # Log some test queries
    analytics.log_query("who is the principal?", "check_static_facts", 100, True, True)
    analytics.log_query("how many students placed?", "query_database", 1500, True, False)
    analytics.log_query("campus life?", "search_website", 5000, True, False)
    
    # Get stats
    stats = analytics.get_stats(days=7)
    print("Analytics Stats:")
    print(f"Total queries: {stats['total_queries']}")
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Cache hit rate: {stats['cache_hit_rate']}%")
    print(f"Avg response time: {stats['avg_response_time_ms']}ms")
    print(f"\nTool usage: {stats['tool_usage']}")
    print(f"\nTop queries: {stats['top_queries']}")
