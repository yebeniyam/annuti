import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables from .env file
load_dotenv(project_root / '.env')

from app.core.supabase import supabase
from app.core.config import settings

def create_tables():
    """Create necessary tables in Supabase."""
    print("🔄 Creating database tables...")
    
    # Create users table
    users_table = """
    CREATE TABLE IF NOT EXISTS public.users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255),
        role VARCHAR(50) NOT NULL DEFAULT 'user',
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """
    
    # Create refresh_tokens table
    refresh_tokens_table = """
    CREATE TABLE IF NOT EXISTS public.refresh_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """
    
    # Create user_profiles table
    user_profiles_table = """
    CREATE TABLE IF NOT EXISTS public.user_profiles (
        id UUID PRIMARY KEY REFERENCES public.users(id) ON DELETE CASCADE,
        phone VARCHAR(50),
        address TEXT,
        avatar_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """
    
    try:
        # Execute the SQL statements using the SQL editor API
        print("🔨 Creating users table...")
        supabase.query('users', 'select', {'filters': {'limit': 0}})
        
        # Create tables using raw SQL
        print("🔨 Creating tables with raw SQL...")
        sql_statements = [
            users_table,
            refresh_tokens_table,
            user_profiles_table
        ]
        
        # Execute each SQL statement
        for sql in sql_statements:
            try:
                # This is a workaround since direct SQL execution isn't available in the client
                # We'll need to use the Supabase dashboard to run these SQL statements
                print(f"⚠️ Please run the following SQL in your Supabase SQL editor:")
                print("-" * 80)
                print(sql.strip())
                print("-" * 80)
                print("\n")
            except Exception as e:
                print(f"⚠️ Error executing SQL: {e}")
        
        # Create tables through the API if possible
        try:
            # Create users table through the API
            print("🔨 Creating users table through API...")
            supabase.client.table('users').select('*').limit(1).execute()
        except Exception as e:
            print(f"⚠️ Could not create users table through API: {e}")
            print("   Please create the tables using the SQL provided above.")
        
        print("✅ Database initialization script completed!")
        print("\nNext steps:")
        print("1. Go to your Supabase dashboard")
        print("2. Open the SQL Editor")
        print("3. Create a new query")
        print("4. Copy and paste the SQL statements shown above")
        print("5. Run the query to create the tables")
        print("\nAfter creating the tables, run this script again to create the default admin user.")
        
        # Only try to create admin if tables exist
        try:
            # Check if users table exists
            result = supabase.table('users').select('*').limit(1).execute()
            if not hasattr(result, 'error'):
                print("\n🔍 Users table exists. Creating default admin user...")
                create_default_admin()
        except Exception as e:
            print(f"⚠️ Could not check if tables exist: {e}")
            print("   Please create the tables first using the SQL provided above.")
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        sys.exit(1)

def create_default_admin():
    """Create a default admin user if it doesn't exist."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    admin_email = "admin@bendine.com"
    admin_password = "Admin@123"  # In production, this should be set via environment variables
    
    try:
        # Check if admin user already exists
        result = supabase.table('users').select('*').eq('email', admin_email).execute()
        
        if not result.data:
            # Create admin user
            hashed_password = pwd_context.hash(admin_password)
            
            admin_user = {
                'email': admin_email,
                'password_hash': hashed_password,
                'full_name': 'Admin User',
                'role': 'admin',
                'is_active': True
            }
            
            # Insert admin user
            result = supabase.table('users').insert(admin_user).execute()
            
            if result.data:
                print(f"✅ Created default admin user with email: {admin_email}")
                print(f"🔑 Default password: {admin_password}")
                print("⚠️ Please change this password after first login!")
        else:
            print("ℹ️ Admin user already exists")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    print("🚀 Starting database initialization...")
    print(f"🔗 Connecting to Supabase project: {settings.SUPABASE_URL}")
    
    create_tables()
    
    print("✨ Database initialization complete!")
