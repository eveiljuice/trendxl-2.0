"""
Database setup and models for authentication
"""
import sqlite3
from datetime import datetime
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


# Initialize database on module import
try:
    init_db()
except Exception as e:
    logger.error(f"❌ Failed to initialize database: {e}")
