from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware


# Set allowed origins — in dev you can use "*" or allow localhost
origins = [
    "http://localhost:3000",          # for local frontend dev
    #"https://your-frontend-domain.com" , # replace with real frontend URL

]



# Load environment variables from .env file
load_dotenv()

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,   
    allow_origins=["*"],           # or ["*"] for all origins (not recommended in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only used if you're running it directly (Render uses this)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Use PORT from env, required by Render
    uvicorn.run(app, host="0.0.0.0", port=port)