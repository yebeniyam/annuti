# Admin User Creation Script

This script helps you create an admin user in the Supabase database.

## Prerequisites

1. Python 3.7+
2. Required Python packages (install using `pip install -r requirements.txt`)
3. A `.env` file in the `backend` directory with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SECRET_KEY=your_secret_key
   ```

## Usage

Run the script with the following command:

```bash
python -m scripts.create_admin --email admin@example.com --password yourpassword --name "Admin User"
```

### Arguments

- `--email`: Email address for the admin user (required)
- `--password`: Password for the admin user (must be at least 8 characters, required)
- `--name`: Full name of the admin user (optional, defaults to "Admin User")

## Example

```bash
# Create an admin user
python -m scripts.create_admin --email admin@example.com --password SecurePass123! --name "Admin User"
```

## Output

On success, the script will output a JSON object with the status and details of the created user.

```json
{
  "status": "success",
  "message": "Admin user admin@example.com created successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "is_active": true,
    "is_superuser": true,
    "role": "admin",
    "created_at": "2023-01-01T12:00:00",
    "updated_at": "2023-01-01T12:00:00"
  }
}
```

If the user already exists, you'll see a message indicating that.

## Troubleshooting

- Make sure your `.env` file is properly configured
- Ensure the Supabase URL and key are correct
- Check that the users table exists in your Supabase database
- Verify that the user doesn't already exist in the database
