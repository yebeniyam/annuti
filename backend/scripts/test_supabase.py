import os
import sys
import uuid
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from supabase import create_client

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables from .env file
load_dotenv(project_root / '.env')

# Get settings
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
API_URL = os.getenv('API_URL', 'http://localhost:8000/api/v1')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    sys.exit(1)

# Initialize Supabase client
print(f"🔗 Connecting to Supabase at: {SUPABASE_URL}")
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Successfully initialized Supabase client")
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}")
    sys.exit(1)

# Test user credentials
test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
test_password = "TestPassword123!"
access_token = None

def print_section(title: str):
    """Print a section header for better test output readability."""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None, token: Optional[str] = None) -> Dict:
    """Make an HTTP request to the API."""
    url = f"{API_URL}/{endpoint.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, params=data)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f"\nStatus Code: {e.response.status_code}"
            try:
                error_msg += f"\nResponse: {e.response.json()}"
            except:
                error_msg += f"\nResponse: {e.response.text}"
        print(f"❌ {error_msg}")
        return {"error": error_msg, "status_code": getattr(e.response, 'status_code', 500)}

def test_supabase_connection() -> bool:
    """Test the Supabase connection."""
    print_section("Testing Supabase Connection")
    
    try:
        print("🔍 Executing test query on 'users' table...")
        response = supabase.table('users').select('*').limit(1).execute()
        
        if hasattr(response, 'data'):
            users = response.data
            print(f"✅ Successfully connected to Supabase!")
            print(f"Found {len(users)} users in the database.")
            if users:
                print(f"First user email: {users[0].get('email', 'No email')}")
            return True
        else:
            print("❌ Unexpected response format from Supabase.")
            print(f"Response: {response}")
            return False
                
    except Exception as query_error:
        print(f"❌ Error executing query: {query_error}")
        print("\nThis might mean:")
        print("1. The 'users' table doesn't exist yet")
        print("2. There was an issue with the query")
        print("\nPlease check your Supabase dashboard and make sure to run the SQL script if you haven't already.")
        return False
            
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {e}")
        # Print more detailed error information
        import traceback
        traceback.print_exc()
        return False

def test_user_registration() -> bool:
    """Test user registration endpoint."""
    print_section("Testing User Registration")
    
    # Test data
    user_data = {
        "email": test_email,
        "password": test_password,
        "full_name": "Test User"
    }
    
    try:
        print(f"🔍 Attempting to register user: {user_data['email']}")
        response = make_api_request("POST", "/auth/register", user_data)
        
        if "error" in response:
            print(f"❌ Registration failed: {response['error']}")
            return False
        
        # Check if the response contains the expected fields
        if "email" in response and response["email"] == user_data["email"]:
            print(f"✅ Successfully registered user: {response['email']}")
            print(f"User ID: {response.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Unexpected response format: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error during user registration test: {e}")
        return False

def test_user_login() -> bool:
    """Test user login endpoint."""
    print_section("Testing User Login")
    
    # Test data
    login_data = {
        "username": test_email,
        "password": test_password
    }
    
    try:
        print(f"🔍 Attempting to login user: {login_data['username']}")
        response = make_api_request("POST", "/auth/login", 
                                 data={"username": login_data["username"], 
                                      "password": login_data["password"]})
        
        if "error" in response:
            print(f"❌ Login failed: {response['error']}")
            return False
        
        # Check if the response contains the expected fields
        if "access_token" in response and response.get("token_type") == "bearer":
            global access_token
            access_token = response["access_token"]
            print("✅ Successfully logged in")
            print(f"Access token: {access_token[:20]}...")
            return True
        else:
            print(f"❌ Unexpected response format: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

def test_token_verification() -> bool:
    """Test token verification endpoint."""
    print_section("Testing Token Verification")
    
    if not access_token:
        print("❌ No access token available. Please run login test first.")
        return False
    
    try:
        print("🔍 Testing token verification...")
        response = make_api_request("GET", "/auth/me", 
                                 token=access_token)
        
        if "error" in response:
            print(f"❌ Token verification failed: {response['error']}")
            return False
        
        # Check if the response contains the expected fields
        if "email" in response and response["email"] == test_email:
            print(f"✅ Token is valid")
            print(f"User email: {response['email']}")
            print(f"Full name: {response.get('full_name', 'N/A')}")
            return True
        else:
            print(f"❌ Unexpected response format: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error during token verification test: {e}")
        return False

def cleanup_test_user():
    """Clean up the test user from the database."""
    global access_token
    
    if not access_token:
        return
        
    try:
        print("\n🧹 Cleaning up test user...")
        # First, get the current user's ID
        user_info = make_api_request("GET", "/auth/me", token=access_token)
        if "id" not in user_info:
            print("❌ Could not get user ID for cleanup")
            return
            
        # Delete the test user
        response = make_api_request("DELETE", 
                                  f"/users/me",
                                  token=access_token)
        
        if "error" in response:
            print(f"❌ Failed to delete test user: {response['error']}")
        else:
            print("✅ Successfully deleted test user")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("User Registration", test_user_registration),
        ("User Login", test_user_login),
        ("Token Verification", test_token_verification)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n🚀 Running test: {test_name}")
        if not test_func():
            print(f"❌ Test failed: {test_name}")
            all_passed = False
            break
    
    # Clean up test user if all tests passed
    if all_passed:
        cleanup_test_user()
    
    if all_passed:
        print("\n✨ All tests passed! Your Supabase connection and authentication are working correctly.")
        print("\nNext steps:")
        print("1. Start your FastAPI server with: uvicorn app.main:app --reload")
        print("2. Test the API endpoints with the provided test script")
        print("3. Check the FastAPI docs at http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Here are some troubleshooting steps:")
        print("1. Make sure your Supabase project is running")
        print("2. Verify your .env file has the correct SUPABASE_URL and SUPABASE_KEY")
        print("3. Check if the required tables exist in your Supabase database")
        print("4. Ensure your IP is whitelisted in Supabase dashboard")
        print("5. Run the SQL script in the Supabase SQL Editor if needed")
        print("\nYou can find the SQL script in: scripts/setup_supabase.sql")
        sys.exit(1)