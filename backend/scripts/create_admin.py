import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.security import get_password_hash
from app.core.supabase import supabase
from app.models.user import UserRole
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user(email: str, password: str, full_name: str = "Admin User"):
    """Create an admin user in the database."""
    try:
        logger.info(f"Attempting to create admin user: {email}")
        
        # Check if user already exists
        result = supabase.client.table('users').select('*').eq('email', email).execute()
        if result.data and len(result.data) > 0:
            logger.warning(f"User with email {email} already exists")
            return {"status": "exists", "message": f"User with email {email} already exists"}
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user data
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
            "is_superuser": True,
            "role": UserRole.ADMIN.value
        }
        
        # Insert user into database
        result = supabase.client.table('users').insert(user_data).execute()
        
        if not result.data or len(result.data) == 0:
            logger.error("Failed to create admin user: No data returned from database")
            return {"status": "error", "message": "Failed to create admin user: No data returned from database"}
        
        logger.info(f"Successfully created admin user: {email}")
        return {
            "status": "success",
            "message": f"Admin user {email} created successfully",
            "user": result.data[0]
        }
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}", exc_info=True)
        return {"status": "error", "message": f"Error creating admin user: {str(e)}"}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password (at least 8 characters)")
    parser.add_argument("--name", default="Admin User", help="Admin full name")
    
    args = parser.parse_args()
    
    if len(args.password) < 8:
        print("Error: Password must be at least 8 characters long")
        sys.exit(1)
    
    result = create_admin_user(args.email, args.password, args.name)
    print(result)
