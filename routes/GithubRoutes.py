from fastapi import APIRouter, File, UploadFile, HTTPException, Body
import requests
import base64
from fastapi import APIRouter, HTTPException, Security, Body
from datetime import datetime
from fastapi.security.api_key import APIKeyHeader
from auth import decode_token
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/github", tags=["GitHub File Upload"])
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)


# Replace with your GitHub details
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")
# Headers for GitHub API authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}


@router.post("/uploadFile")
async def upload_file_to_github(file: UploadFile = File(...), Authorization: str = Security(api_key_header)):
    token = Authorization
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")

    try:
        # Read file content
        content = await file.read()
        encoded_content = base64.b64encode(content).decode()
        path = "Menu"+"/"+user_id if user_id else "Menu"
        print("Path:", path)
        # Construct file path
        file_path = f"{path}/{file.filename}" if path else file.filename

        # API URL to upload the file
        api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{file_path}"

        # Commit message
        commit_message = f"Upload {file.filename} on {datetime.now().isoformat()}"

        # Prepare payload
        payload = {
            "message": commit_message,
            "content": encoded_content,
            "branch": GITHUB_BRANCH
        }

        # Upload the file via PUT
        response = requests.put(api_url, json=payload, headers=HEADERS)
        if response.status_code not in [200, 201]:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        # Construct URLs
        github_url = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/{file_path}"
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{file_path}"

        return {
            "message": "File uploaded successfully",
            "github_url": github_url,
            "raw_url": raw_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

