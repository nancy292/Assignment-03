from typing import List, Optional
from pydantic import BaseModel

class FollowerInfo(BaseModel):
    mainUser: str
    secondUser:str
    profilenameofuser:str
    profilenameoffriend:str

class FollowingInfo(BaseModel):
    mainUser: str
    secondUser:str
    profilenameofuser:str
    profilenameoffriend:str


class UserComment(BaseModel):
    username: str
    content: str
    timestamp: str 

class Post(BaseModel):
    post_identifier: str
    username: str   
    useremail:str          
    upload_date: str                 
    media_file: str
    like_count: int
    caption: str
    feedback: Optional[List[UserComment]] = []

class AccountProfile(BaseModel):
    full_name: str
    Username: str
    useremail:str
    followers_list: Optional[List[FollowerInfo]] = []
    following_list: Optional[List[FollowingInfo]] = []
    bio:str

class EmailLookupRequest(BaseModel):
    email: str

class UsernameLookupRequest(BaseModel):
    Username: str

class CommentPayload(BaseModel):
    comment: dict  

class RegistrationRequest(BaseModel):
    profileName:str
    username:str
    bio:str
    email:str

class ConnectionRequest(BaseModel):
    requester_handle: str 
    target_handle: str
    requester_display_name: str
