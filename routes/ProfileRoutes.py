#get details(name, email, user id, subscription expiry date)
#modify Hotel name
#get hotel Name


from fastapi import APIRouter, HTTPException, Depends, Header, Query
from fastapi import Security, Body
from models import MenuItem
from database import MenuItems_table
from auth import hash_password, verify_password, create_access_token, decode_token
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
import requests
import pytz
from datetime import datetime
from nanoid import generate
from fastapi.encoders import jsonable_encoder
from database import UserDetails_table

router = APIRouter(prefix="/profile", tags=["Profile Details"])
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


# Get all user details except password for the logged-in user

@router.get("/myDetails")
def get_my_details(Authorization: str = Security(api_key_header)):
	token = Authorization
	jwt_details = decode_token(token)
	user_id = jwt_details.get("user_id")

	if not user_id:
		raise HTTPException(status_code=401, detail="Invalid token")

	try:
		response = UserDetails_table.select("id, name, email, user_id, created_at, subscription_end, display_name").eq("user_id", user_id).single().execute()
		user_data = response.data if hasattr(response, 'data') else None
		if not user_data:
			raise HTTPException(status_code=404, detail="User not found")
		return user_data
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

