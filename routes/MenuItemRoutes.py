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

router = APIRouter(prefix="/menuManagement", tags=["MenuManagement"])
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


#Add Menu Item
@router.post("/addMenuItem")
def add_menu_item(menuItem: MenuItem=Body(...), Authorization: str = Security(api_key_header)):
    token = Authorization
    jwt_details = decode_token(token)
    user_id = jwt_details.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Insert into DB
    menuItemData = jsonable_encoder(menuItem, exclude={"id","user_id"})
    menuItemData["user_id"] = user_id

    try:
        response = MenuItems_table.insert(menuItemData).execute()
        # If no exception, insert was successful
        return {
                "message": "Menu item added successfully", 
                "ID": response.data[0]["id"],
                "Dish Name": response.data[0]["dish_name"],
                "Description": response.data[0]["description"],
                "User ID": response.data[0]["user_id"],
                "Price": response.data[0]["price"],
                "Category": response.data[0]["category"],
                }
    except Exception as e:
        # handle or log error e here
        # return {"error": str(e)}
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Get all dishes for the logged-in user
@router.get("/getMyDishes")
def get_my_dishes(Authorization: str = Security(api_key_header)):
    token = Authorization
    jwt_details = decode_token(token)
    user_id = jwt_details.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        response = MenuItems_table.select("*").eq("user_id", user_id).execute()
        dishes = response.data if hasattr(response, 'data') else []
        return {"dishes": dishes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Update a menu item for the logged-in user
@router.put("/updateMenuItem/{dish_id}")
def update_menu_item(dish_id: int, menuItem: MenuItem = Body(...), Authorization: str = Security(api_key_header)):
    token = Authorization
    jwt_details = decode_token(token)
    user_id = jwt_details.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    update_data = jsonable_encoder(menuItem, exclude_unset=True, exclude={"id", "user_id"})

    try:
        # Only allow updating if the dish belongs to the user
        response = MenuItems_table.update(update_data).eq("id", dish_id).eq("user_id", user_id).execute()
        if hasattr(response, 'data') and response.data:
            return {"message": "Menu item updated successfully", "updated_id": dish_id, "updated_fields": update_data}
        else:
            raise HTTPException(status_code=404, detail="Menu item not found or not authorized to update")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Delete a menu item for the logged-in user
@router.delete("/deleteMenuItem/{dish_id}")
def delete_menu_item(dish_id: int, Authorization: str = Security(api_key_header)):
    token = Authorization
    jwt_details = decode_token(token)
    user_id = jwt_details.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        # Only allow deleting if the dish belongs to the user
        response = MenuItems_table.delete().eq("id", dish_id).eq("user_id", user_id).execute()
        if hasattr(response, 'data') and response.data:
            return {"message": "Menu item deleted successfully", "deleted_id": dish_id}
        else:
            raise HTTPException(status_code=404, detail="Menu item not found or not authorized to delete")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/getMenuCardFor/{user_id}")
def get_menu_card_for(user_id: str):
    try:
        response = MenuItems_table.select("*").eq("user_id", user_id).execute()
        dishes = response.data if hasattr(response, 'data') else []
        if not dishes:
            raise HTTPException(status_code=404, detail="No menu items found for this user")
        return {"dishes": dishes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")