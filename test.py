from supabase import create_client
from database import supabase

# # Replace with your actual Supabase URL and API key
# SUPABASE_URL = "https://your-project.supabase.co"
# SUPABASE_KEY = "your-anon-or-service-role-key"
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_users():
    response = supabase.table("UserDetails").select("*").execute()
    if response.status_code == 200:
        return response.data  # List of dicts (rows)
    else:
        raise Exception(f"Error fetching users: {response.status_code}")

if __name__ == "__main__":
    # users = get_all_users()
    # print(users)
    new_user = {
  "name": "John Doe",
  "email": "john.doe@example.com",
  "user_id": "user_abc123",
  "password": "securePassword123!",
  "created_at": "2025-09-28T10:30:00+05:30",
  "subscription_expiry_date": "2025-12-31"
}


    response = supabase.table("UserDetails").insert(new_user).execute()
    print(response.data)
