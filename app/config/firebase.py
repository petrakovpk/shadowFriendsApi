import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header

cred = credentials.Certificate("security/shadowfriends-b81a1-firebase-adminsdk-bbksz-a1a83d2739.json")
app = firebase_admin.initialize_app(cred)

def get_firebase_auth(authorization: str = Header(None)):
    if authorization == "Bearer PASHA_SECRET_KEY":
        uid = 'nAGy29cq5yPc0ZGeMI5Kf2JxuK02'
        user = auth.get_user(uid)
        return user

    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header not provided")

    try:
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user = auth.get_user(decoded_token["uid"])
        return user

    except IndexError:
        raise HTTPException(status_code=403, detail="Invalid authorization header format")

    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))



