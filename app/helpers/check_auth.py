from fastapi import HTTPException
def check_user_authorization(firebase_user):
    if not firebase_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

def check_object_authorization(object, firebase_user):
    if object.user_uid != firebase_user.uid:
        raise HTTPException(status_code=403, detail="Forbidden")

def check_object_is_exist(object):
    if object is None:
        raise HTTPException(status_code=404, detail="Object not found")