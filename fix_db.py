#!/usr/bin/env python
"""
Migration script to add the missing last_active column to the users table.

This script should be run once to fix the database schema.
"""

import asyncio
import logging
import aiosqlite
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from config.config import load_config
from config.logging_config import setup_logging

# Set up logging
logger = logging.getLogger(__name__)

async def add_last_active_column(db_path: str = 'translations.db') -> bool:
    """
    Add the last_active column to the users table if it doesn't exist.
    
    Args:
        db_path: Path to the database file.
        
    Returns:
        True if the migration was successful, False otherwise.
    """
    conn = None
    try:
        # Connect to the database
        conn = await aiosqlite.connect(db_path)
        
        # Check if the column already exists
        cursor = await conn.execute(
            """
            PRAGMA table_info(users)
            """
        )
        
        columns = await cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'last_active' not in column_names:
            # Add the last_active column without a default value
            await conn.execute(
                """
                ALTER TABLE users 
                ADD COLUMN last_active TIMESTAMP
                """
            )
            
            # Update all existing rows to set last_active to the current time
            await conn.execute(
                """
                UPDATE users
                SET last_active = CURRENT_TIMESTAMP
                """
            )
            
            logger.info(f"Added 'last_active' column to users table in {db_path}")
            await conn.commit()
            
            # Verify the column was added
            cursor = await conn.execute(
                """
                PRAGMA table_info(users)
                """
            )
            
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'last_active' in column_names:
                logger.info("Column 'last_active' was successfully added and verified")
                return True
            else:
                logger.error("Failed to verify 'last_active' column after adding it")
                return False
        else:
            logger.info("Column 'last_active' already exists in users table")
            return True
            
    except Exception as e:
        logger.error(f"Error adding 'last_active' column: {e}")
        if conn:
            await conn.rollback()
        return False
    finally:
        if conn:
            await conn.close()

async def main():
    """Main function to run the migration."""
    # Set up logging
    setup_logging()
    logger.info("Starting database migration to add last_active column")
    
    # Load configuration
    config = load_config()
    db_path = config.db_path
    
    # Run the migration
    success = await add_last_active_column(db_path)
    
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")

if __name__ == "__main__":
    asyncio.run(main())