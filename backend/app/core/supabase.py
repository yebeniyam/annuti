from supabase import create_client
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Initialize the Supabase client with service role for admin operations
if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
    raise ValueError("Supabase URL and Service Key must be set in environment variables")

try:
    # Initialize the Supabase client with service role
    supabase = create_client(
        settings.SUPABASE_URL, 
        settings.SUPABASE_SERVICE_KEY
    )
    logger.info("Successfully initialized Supabase client with service role")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    raise

def test_connection() -> bool:
    """Test the Supabase connection with a simple query."""
    try:
        result = supabase.table('users').select('*').limit(1).execute()
        logger.info("Successfully connected to Supabase")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return False
