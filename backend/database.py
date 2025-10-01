"""
Database setup and models for authentication
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = "trendxl_users.db"


@contextmanager
def get_db():
    """Context manager for database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize database with users table"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                avatar_url TEXT,
                bio TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)

        # Create token_usage table for tracking API usage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                openai_prompt_tokens INTEGER DEFAULT 0,
                openai_completion_tokens INTEGER DEFAULT 0,
                openai_total_tokens INTEGER DEFAULT 0,
                perplexity_prompt_tokens INTEGER DEFAULT 0,
                perplexity_completion_tokens INTEGER DEFAULT 0,
                perplexity_total_tokens INTEGER DEFAULT 0,
                ensemble_units INTEGER DEFAULT 0,
                total_cost_estimate REAL DEFAULT 0.0,
                profile_analyzed TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_token_usage_user_id 
            ON token_usage(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp 
            ON token_usage(analysis_timestamp DESC)
        """)

        conn.commit()
        logger.info("✅ Database initialized successfully")


def create_user(
    email: str,
    username: str,
    hashed_password: str,
    full_name: Optional[str] = None
) -> dict:
    """Create a new user"""
    with get_db() as conn:
        cursor = conn.cursor()
        created_at = datetime.utcnow().isoformat()

        try:
            cursor.execute("""
                INSERT INTO users (email, username, hashed_password, full_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (email, username, hashed_password, full_name, created_at))

            conn.commit()
            user_id = cursor.lastrowid

            # Retrieve the created user
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = dict(cursor.fetchone())

            logger.info(f"✅ User created: {username}")
            return user

        except sqlite3.IntegrityError as e:
            logger.error(f"❌ Failed to create user: {e}")
            raise ValueError("Email or username already exists")


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        return dict(result) if result else None


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        return dict(result) if result else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else None


def update_last_login(user_id: int):
    """Update user's last login timestamp"""
    with get_db() as conn:
        cursor = conn.cursor()
        last_login = datetime.utcnow().isoformat()
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (last_login, user_id)
        )
        conn.commit()


def update_user_profile(
    user_id: int,
    full_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    bio: Optional[str] = None
) -> Optional[dict]:
    """Update user profile information"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Build dynamic update query
        updates = []
        params = []

        if full_name is not None:
            updates.append("full_name = ?")
            params.append(full_name)

        if avatar_url is not None:
            updates.append("avatar_url = ?")
            params.append(avatar_url)

        if bio is not None:
            updates.append("bio = ?")
            params.append(bio)

        if not updates:
            return get_user_by_id(user_id)

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(query, params)
        conn.commit()

        return get_user_by_id(user_id)


def record_token_usage(
    user_id: int,
    openai_prompt_tokens: int,
    openai_completion_tokens: int,
    perplexity_prompt_tokens: int,
    perplexity_completion_tokens: int,
    ensemble_units: int,
    total_cost_estimate: float,
    profile_analyzed: Optional[str] = None
) -> dict:
    """Record token usage for a user analysis"""
    with get_db() as conn:
        cursor = conn.cursor()
        analysis_timestamp = datetime.utcnow().isoformat()

        openai_total = openai_prompt_tokens + openai_completion_tokens
        perplexity_total = perplexity_prompt_tokens + perplexity_completion_tokens

        try:
            cursor.execute("""
                INSERT INTO token_usage (
                    user_id, analysis_timestamp, 
                    openai_prompt_tokens, openai_completion_tokens, openai_total_tokens,
                    perplexity_prompt_tokens, perplexity_completion_tokens, perplexity_total_tokens,
                    ensemble_units, total_cost_estimate, profile_analyzed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, analysis_timestamp,
                openai_prompt_tokens, openai_completion_tokens, openai_total,
                perplexity_prompt_tokens, perplexity_completion_tokens, perplexity_total,
                ensemble_units, total_cost_estimate, profile_analyzed
            ))

            conn.commit()
            record_id = cursor.lastrowid

            logger.info(
                f"✅ Token usage recorded for user {user_id}: "
                f"OpenAI={openai_total}, Perplexity={perplexity_total}, Ensemble={ensemble_units}"
            )

            return {
                "id": record_id,
                "user_id": user_id,
                "analysis_timestamp": analysis_timestamp,
                "openai_total_tokens": openai_total,
                "perplexity_total_tokens": perplexity_total,
                "ensemble_units": ensemble_units,
                "total_cost_estimate": total_cost_estimate
            }

        except Exception as e:
            logger.error(f"❌ Failed to record token usage: {e}")
            raise


def get_user_token_usage(
    user_id: int,
    limit: int = 100,
    offset: int = 0
) -> list:
    """Get token usage history for a user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM token_usage 
            WHERE user_id = ? 
            ORDER BY analysis_timestamp DESC 
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset))

        results = cursor.fetchall()
        return [dict(row) for row in results]


def get_user_token_summary(user_id: int) -> dict:
    """Get aggregated token usage summary for a user"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Get total usage across all analyses
        cursor.execute("""
            SELECT 
                COUNT(*) as total_analyses,
                SUM(openai_total_tokens) as total_openai_tokens,
                SUM(openai_prompt_tokens) as total_openai_prompt,
                SUM(openai_completion_tokens) as total_openai_completion,
                SUM(perplexity_total_tokens) as total_perplexity_tokens,
                SUM(perplexity_prompt_tokens) as total_perplexity_prompt,
                SUM(perplexity_completion_tokens) as total_perplexity_completion,
                SUM(ensemble_units) as total_ensemble_units,
                SUM(total_cost_estimate) as total_cost,
                MIN(analysis_timestamp) as first_analysis,
                MAX(analysis_timestamp) as last_analysis
            FROM token_usage 
            WHERE user_id = ?
        """, (user_id,))

        result = cursor.fetchone()
        if not result:
            return {
                "total_analyses": 0,
                "total_openai_tokens": 0,
                "total_perplexity_tokens": 0,
                "total_ensemble_units": 0,
                "total_cost": 0.0
            }

        return dict(result)


def get_user_token_usage_by_period(
    user_id: int,
    period_days: int = 30
) -> dict:
    """Get token usage summary for a specific time period"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Calculate the start date
        start_date = (datetime.utcnow() -
                      timedelta(days=period_days)).isoformat()

        cursor.execute("""
            SELECT 
                COUNT(*) as analyses_count,
                SUM(openai_total_tokens) as openai_tokens,
                SUM(perplexity_total_tokens) as perplexity_tokens,
                SUM(ensemble_units) as ensemble_units,
                SUM(total_cost_estimate) as total_cost
            FROM token_usage 
            WHERE user_id = ? AND analysis_timestamp >= ?
        """, (user_id, start_date))

        result = cursor.fetchone()
        if not result:
            return {
                "period_days": period_days,
                "analyses_count": 0,
                "openai_tokens": 0,
                "perplexity_tokens": 0,
                "ensemble_units": 0,
                "total_cost": 0.0
            }

        data = dict(result)
        data["period_days"] = period_days
        return data


# Initialize database on module import
try:
    init_db()
except Exception as e:
    logger.error(f"❌ Failed to initialize database: {e}")
