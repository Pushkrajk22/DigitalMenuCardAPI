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

router = APIRouter(prefix="/analytics", tags=["Analytics"])
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


# Get total number of menu items for the logged-in user
@router.get("/itemsSummary")
def get_total_items(Authorization: str = Security(api_key_header)):
	token = Authorization
	jwt_details = decode_token(token)
	user_id = jwt_details.get("user_id")

	if not user_id:
		raise HTTPException(status_code=401, detail="Invalid token")


	try:
			response = MenuItems_table.select("id,category").eq("user_id", user_id).execute()
			items = response.data if hasattr(response, 'data') and response.data else []
			total_items = len(items)
			categories = set()
			category_counts = {}
			for item in items:
				cat = item.get("category")
				if cat:
					categories.add(cat)
					category_counts[cat] = category_counts.get(cat, 0) + 1
			total_categories = len(categories)
			return {
				"total_dishes": total_items,
				"total_categories": total_categories,
				"category_wise_dishes": category_counts
			}
	except Exception as e:
			raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

