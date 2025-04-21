from fastapi import FastAPI, Request , Form, Response, UploadFile, File
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
from services import fetch_all_users
from models import (
    FollowerInfo,
    FollowingInfo,
    UserComment,
    Post,
    AccountProfile,
    EmailLookupRequest,
    RegistrationRequest,
    ConnectionRequest,
    UsernameLookupRequest,
    CommentPayload
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database = firestore.Client()
firebase_request_adapter = requests.Request()



def addDirectory(directory_name):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.blob(directory_name)
    blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')


def fetch_user_by_email(email_address):
    user_query = database.collection('User').where('email', '==', email_address).limit(1).get()
    default_profile = {
        'name': 'Nancy Reddy'
    }
    
    if not user_query:
        return default_profile
    else:
        user_profile = user_query[0].to_dict()
        return user_profile


def validateFirebaseToken(id_token):
    if not id_token:
        return None
    user_token = None 
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    except ValueError as e:
        print(str(e))

    return user_token

def getuserfromemail(email):
    user_ref = database.collection('User').where('email', '==', email).limit(1).get()
    user_data = {
            'name':'John Doe'
        }
    if not user_ref:
        return user_data
    else:
        user_data = user_ref[0].to_dict()
        return user_data

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    id_token = request.cookies.get('token')
    error_message = "No error here"
    user_token = None
    user = None
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return templates.TemplateResponse("login.html",{'request':request, 'user_token':None , 'error_message':None , 'user_info':None})
    return templates.TemplateResponse("timeline.html",{"request": request})

@app.get("/userprofile", response_class=HTMLResponse)
async def userprofile(request: Request):
    return templates.TemplateResponse("userProfilePage.html", {"request": request})

@app.get("/followers", response_class=HTMLResponse)
async def followerspage(request: Request):
    return templates.TemplateResponse("followers.html", {"request": request})

@app.get("/following", response_class=HTMLResponse)
async def followingpage(request: Request):
    return templates.TemplateResponse("following.html", {"request": request})

@app.get("/user/{username}", response_class=HTMLResponse)
async def firendaccount(request: Request, username:str ):
    print("profile")
    return templates.TemplateResponse("friendProfile.html", {"request": request, "username":username})



@app.get("/people", response_class=HTMLResponse)
async def getthepeople(request: Request):
    id_token = request.cookies.get('token')
    error_message = "No error here"
    user_token = None
    user = None

    print("inside get")
    user_token = validateFirebaseToken(id_token)
    print("inside user toekn ",user_token)

    if not user_token:
        return templates.TemplateResponse("main-page.html",{'request':request, 'user_token':None , 'error_message':None , 'user_info':None})
    
    return templates.TemplateResponse("followers.html", {"request": request , 'user_email':user_token['email']})


@app.post("/createnewuser")
async def createnewuser(data: EmailLookupRequest):
    # print("check user ", data)
    user_ref = database.collection('User').where('email', '==', data.email).limit(1).get()
    if not user_ref:
        database.collection('User').add({
                "full_name": "",
                "email":data.email,
                "Username":"",
                "followers":[],
                "following":[],
            })
        print("user created")
    else:
        print("user already exist")
        pass
    return 0

