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
    print("added to the database")

def addFile(file , user , postdescription):
    print("inside add file")
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = storage.Blob(file.filename, bucket)
    blob.upload_from_file(file.file)
    createPost(file.filename,user, postdescription)

def blobList(prefix):
    print("local_constants.PROJECT_NAME ",local_constants.PROJECT_NAME)
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    return storage_client.list_blobs(local_constants.PROJECT_STORAGE_BUCKET, prefix=prefix)

def downloadBlob(filename):
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)
    blob = bucket.get_blob(filename)
    return blob.download_as_bytes()



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


@app.post("/getUser")
async def geruserusingemail(data: UsernameLookupRequest , response_class=JSONResponse):
    user_ref = database.collection('User').where('email', '==', data.Username).limit(1).get()
    if not user_ref:
        return JSONResponse(content={"error": "User not found"}, status_code=404)
    else:
        user_data = user_ref[0].to_dict()
        return JSONResponse(content={"user": user_data}, status_code=200)

@app.post("/getUserUsingUsername")
async def getUserUsingUsername(data: UsernameLookupRequest , response_class=JSONResponse):
    print("getting usrr")
    user_ref = database.collection('User').where('Username', '==', data.Username).limit(1).get()
    if not user_ref:
        return JSONResponse(content={"error": "User not found"}, status_code=404)
    else:
        user_data = user_ref[0].to_dict()
        return JSONResponse(content={"user": user_data}, status_code=200)

@app.post("/fetchUserPosts")
async def getPostsOfUser(data: UsernameLookupRequest, response_class=JSONResponse):
    print("getting posts of user ",data)
    posts_ref = database.collection('Post').where('email', '==', data.Username).get()
    if not posts_ref:
        posts = []
    else:
        posts = [doc.to_dict() for doc in posts_ref]
    return JSONResponse(content={"posts": posts}, status_code=200)


@app.post("/unfollowuser")
async def unfollow_user(data: FollowingInfo):
    current_username = data.mainUser
    friend_username = data.secondUser
   

    user_docs = database.collection('User').where('Username', '==', current_username).limit(1).get()
    friend_docs = database.collection('User').where('Username', '==', friend_username).limit(1).get()

    if not user_docs or not friend_docs:
        raise HTTPException(status_code=404, detail="User or friend not found")

    user_ref = user_docs[0].reference
    friend_ref = friend_docs[0].reference

    user_data = user_docs[0].to_dict()
    friend_data = friend_docs[0].to_dict()

    updated_following = [entry for entry in user_data.get("following", []) if entry.get("username") != friend_username]
    user_ref.update({"following": updated_following})
    updated_followers = [entry for entry in friend_data.get("followers", []) if entry.get("username") != current_username]
    friend_ref.update({"followers": updated_followers})

    print(f"{current_username} unfollowed {friend_username}")
    return {"message": f"{current_username} unfollowed {friend_username}"}
    


@app.post("/modifyusername")
async def modify_user_credentials(payload: RegistrationRequest, response_class=JSONResponse):
    username_check = database.collection('User').where('Username', '==', payload.username).limit(1).get()
    
    if username_check:
        print("inside if")
        return JSONResponse(content={"error": "Username is already taken"}, status_code=400)

    user_search = database.collection('User').where('email', '==', payload.email).limit(1).get()
    if not user_search:
        return JSONResponse(content={"error": "No user found with this email"}, status_code=404)

    user_record = user_search[0]
    user_doc_ref = database.collection('User').document(user_record.id)

    user_doc_ref.update({
        "full_name": payload.profileName,
        "Username": payload.username,
        "bio":payload.bio
    })

    return JSONResponse(content={"message": "User profile updated successfully"}, status_code=200)



@app.get("/getusersfromAPI")
async def get_all_users():
    users = fetch_all_users()
    return {"users": users}



@app.post("/create-post")
async def create_post(
    file: UploadFile = File(...),
    caption: str = Form(...),
    file_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...)
):
    
    print("file is ",username,file)
   
    user = {
        "Username": username,
        "email": email 
    }

    filename = file.filename
    print("file name ",filename, " user ",user)

    addFile(file,user,caption)

    return {"message": "Post created successfully"}

@app.post("/add-directory", response_class=RedirectResponse)
async def addDirectoryHandler(request: Request):
    id_token = request.cookies.get("token")
    user_token= validateFirebaseToken(id_token)
    if not user_token:
      return RedirectResponse('/')
    form = await request.form()
    dir_name = form['dir_name']
    if dir_name == '' or dir_name[-1] != '/':
        return RedirectResponse('/')
    addDirectory(dir_name)
    return RedirectResponse('/', status_code=status.HTTP_302_FOUND)

@app.post("/download-file", response_class=Response)
async def downloadFileHandler(request: Request):
    
    id_token= request.cookies.get("token")
    user_token = validateFirebaseToken(id_token)
    if not user_token:
        return RedirectResponse('/')
  
    form = await request.form()
    filename = form['filename']
    return Response (downloadBlob(filename))



@app.post("/addCommentToPost", response_class=JSONResponse)
async def addCommentToPost(request: Request):
    data = await request.json() 
    print("data in api ",data)
    new_comment_data = data.get("comment")
    print("Received comment:", new_comment_data) 
    if not new_comment_data:
        return JSONResponse(content={"error": "No comment provided"}, status_code=400)

    post_id = new_comment_data.get("activePostId")
    if not post_id:
        return JSONResponse(content={"error": "No post ID provided"}, status_code=400)
    print("new_comment_data ",new_comment_data ,post_id )
    posts_ref = database.collection("Post")
    query = posts_ref.where("post_id", "==", post_id).limit(1)
    results = query.stream()
    print("active post id ",post_id, results)
    post_doc = None
    post_doc_id = None
    for doc in results:
        post_doc = doc.to_dict()
        post_doc_id = doc.id
        break
    print("post doc ",post_doc)
    if not post_doc:
        return JSONResponse(content={"error": "Post not found"}, status_code=404)

    new_comment = {
        "username": new_comment_data["email"],
        "comment": new_comment_data["comment"],
        "time": new_comment_data["timestamp"],
    }
    print("new comment ",new_comment)
    comments = post_doc.get("comments", [])
    comments.append(new_comment)

    post_ref = database.collection("Post").document(post_doc_id)
    post_ref.update({
        "comments": comments
    })

    return {"message": "Comment added successfully", "new_comment": new_comment}