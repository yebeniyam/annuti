from supabase import create_client
from app.core.config import settings
from typing import Optional, Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

# Initialize the Supabase client directly
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    raise ValueError("Supabase URL and Key must be set in environment variables")

try:
    # Initialize the Supabase client
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info("Successfully initialized Supabase client")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    raise

def test_connection() -> bool:
    """Test the Supabase connection."""
    try:
        # A simple query to test the connection
        result = supabase.from_('users').select('*').limit(1).execute()
        logger.info("Successfully connected to Supabase")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {e}")
        return False
