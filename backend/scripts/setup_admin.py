import sys
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.supabase import supabase
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_admin_user():
    admin_email = "admin@example.com"
    admin_password = "Admin@Secure123!"  # In production, use a more secure password
    admin_name = "Admin"

    try:
        logger.info(f"Attempting to create admin user: {admin_email}")
        
        # Check if user already exists
        try:
            result = supabase.auth.admin.list_users()
            existing_user = next((user for user in result.users if user.email == admin_email), None)
            
            if existing_user:
                logger.info(f"Admin user {admin_email} already exists")
                # Update password if needed
                supabase.auth.admin.update_user_by_id(existing_user.id, {"password": admin_password})
                logger.info("Admin password updated")
                return
        except Exception as e:
            logger.warning(f"Error checking for existing user: {e}")

        # Create the admin user
        user = supabase.auth.admin.create_user({
            "email": admin_email,
            "password": admin_password,
            "email_confirm": True,
            "user_metadata": {
                "name": admin_name,
                "role": "admin"
            }
        })
        
        logger.info(f"Successfully created admin user: {admin_email}")
        
        # Add user to public.users table
        db_user = {
            'id': user.user.id,
            'email': admin_email,
            'full_name': admin_name,
            'is_superuser': True,
            'is_active': True,
            'role': 'admin'
        }
        
        supabase.table('users').upsert(db_user).execute()
        logger.info("Admin user added to public.users table")
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise

if __name__ == "__main__":
    # Load environment variables
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    # Run the async function
    asyncio.run(create_admin_user())
