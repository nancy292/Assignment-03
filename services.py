from fastapi import FastAPI, Request , Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel,Field
from google.cloud import firestore , storage
from uuid import uuid4
from typing import List, Optional
from fastapi import HTTPException , status ,APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from google.auth.transport import requests
import google.oauth2.id_token
import time
import starlette.status as status
import local_constants
import uuid
from datetime import datetime

from typing import List, Dict
from models import (
    FollowerInfo,
    FollowingInfo,
    UserComment,
    Post,
    AccountProfile,
    EmailLookupRequest,
    RegistrationRequest,
    ConnectionRequest,
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

database = firestore.Client()
firebase_request_adapter = requests.Request()





def fetch_all_users() -> List[Dict[str, str]]:
    user_ref = database.collection('User')
    docs = user_ref.stream()
    users = []
    print("inside fetch al users")
    for doc in docs:
        user_data = doc.to_dict()
        selected_data = {
            "Username": user_data.get("Username"),
            "useremail": user_data.get("email"),
            "full_name": user_data.get("full_name")
        }
        users.append(selected_data)

    return users



def createPost(filename, user, postdescription):
    post_id = str(uuid.uuid4())  
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    database.collection('Post').add({
                "post_id": post_id,
                "Username": user['Username'],  
                "email":user['email'],        
                "Date": current_time,            
                "filename": filename,
                "likes": 0,
                "description": postdescription,
                "comments":[]
            })

