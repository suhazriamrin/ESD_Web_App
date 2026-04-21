"""
Utility script to set up API keys for the database.
Run this once to initialize the api_key column and generate keys for existing users.
"""

from db_queries import get_connection, ensure_api_key_column, generate_api_key_for_user
from mysql.connector import Error

def list_users():
    """List all users in the database."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, username, api_key FROM zhaji.users"
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Error as e:
            print(f"Error fetching users: {e}")
            return None
    return None

def setup():
    """Initialize API keys for all users."""
    print("Initializing API key setup...")
    
    # Step 1: Ensure column exists
    print("\n1. Ensuring api_key column exists in users table...")
    ensure_api_key_column()
    
    # Step 2: List existing users
    print("\n2. Fetching existing users...")
    users = list_users()
    
    if not users:
        print("No users found in database.")
        return
    
    print(f"Found {len(users)} user(s):")
    print("-" * 80)
    
    for user in users:
        username = user['username']
        existing_key = user['api_key']
        
        if existing_key:
            print(f"✓ {username}: Already has API key")
        else:
            print(f"→ {username}: Generating API key...")
            api_key = generate_api_key_for_user(username)
            if api_key:
                print(f"✓ {username}: API key generated: {api_key}")
            else:
                print(f"✗ {username}: Failed to generate API key")
    
    # Step 3: Show final status
    print("\n3. Final status:")
    print("-" * 80)
    users = list_users()
    for user in users:
        status = "✓" if user['api_key'] else "✗"
        print(f"{status} {user['username']}: {user['api_key'] or 'NO KEY'}")
    
    print("\n✓ Setup complete!")
    print("\nUsage: Include the API key in your HTTP requests:")
    print("  curl -H \"X-API-Key: <your-api-key>\" http://localhost:8080/api/namelist")

if __name__ == "__main__":
    setup()
