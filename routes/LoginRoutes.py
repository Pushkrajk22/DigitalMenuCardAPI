#Change Passoword


from fastapi import APIRouter, HTTPException, Depends, Header, Query
from models import UserDetails, UserRegisterModel, LoginRequest
from database import UserDetails_table
from auth import hash_password, verify_password, create_access_token, decode_token
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
import requests
import pytz
from datetime import datetime
from nanoid import generate
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/auth", tags=["Authentication"])
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


@router.post("/register")
def register(user_input: UserRegisterModel):
    # Check if email already exists
    existing_user = UserDetails_table.select("*").eq("email", user_input.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate hashed password and user_id
    hashed_password = hash_password(user_input.password)
    user_id = generate(size=12)

    # Create new user model
    new_user = UserDetails(
        name=user_input.name,
        email=user_input.email,
        password=hashed_password,
        user_id=user_id,
    )

    # Insert into DB
    user_data = jsonable_encoder(new_user, exclude={"id"})

    try:
        response = UserDetails_table.insert(user_data).execute()
        # If no exception, insert was successful
        return {
                "message": "User registered successfully", 
                "Name": response.data[0]["name"],
                "Email": response.data[0]["email"],
                "User ID": response.data[0]["user_id"]
                }
    except Exception as e:
        # handle or log error e here
        return {"error": str(e)}

    if response.status_code != 201:
        raise HTTPException(status_code=500, detail="User registration failed")

    return {"message": "User registered successfully", "user_id": user_id}


@router.post("/login")
def login(request: LoginRequest):
    email = request.email
    password = request.password
    # Fetch user by email
    response = UserDetails_table.select("*").eq("email", email).execute()
    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_record = response.data[0]
    if not verify_password(password, user_record["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create JWT token
    token = create_access_token(data={"user_id": user_record["user_id"], "email": user_record["email"]})

    return {
            "message": "Login successful",
            "access_token": token, 
            }


#Delete Account
@router.delete("/delete_account")
def delete_account(Authorization: str = Security(api_key_header)):
    try:
        # Get token from "Bearer <token>"
        token = Authorization
        payload = decode_token(token)
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Delete user from UserDetails table
        result = UserDetails_table.delete().eq("user_id", user_id).execute()

        # result is likely a list or dict, not a Response object
        if not result:  # Empty response means nothing was deleted
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "Account deleted successfully"}

    except IndexError:
        raise HTTPException(status_code=401, detail="Authorization header malformed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account deletion failed: {str(e)}")

@router.get("/validateToken")
def checkToken(token:str):
    try:
        payload = decode_token(token)
        return {"isValid": True, "email": payload["email"], "user_id": payload["user_id"]}
    except HTTPException as e:
        return {"isValid": False, "detail": str(e.detail)}
