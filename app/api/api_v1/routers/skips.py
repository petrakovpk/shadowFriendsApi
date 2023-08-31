from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from firebase_admin import auth
from pydantic import UUID4

import crud
from config import get_db, get_firebase_auth
from helpers import check_user_authorization, check_object_authorization
from schemas import SkipCreate, Skip

router = APIRouter()

@router.get("/{skip_uuid}", response_model=Skip, status_code=200)
async def get_skip(
        skip_uuid: UUID4,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    skip_in_db = await crud.skips.get_skip(db=db, skip_uuid=skip_uuid)

    if skip_in_db is None:
        raise HTTPException(status_code=404, detail="Not found")

    return skip_in_db

@router.post("/{skip_uuid}", response_model=Skip, status_code=200)
async def create_skip(
        skip_uuid: UUID4,
        skip: Skip,
        db: Session = Depends(get_db),
        firebase_user: auth.UserRecord = Depends(get_firebase_auth)
):
    check_user_authorization(firebase_user)

    skip_in_db = await crud.skips.get_skip(db=db, skip_uuid=skip_uuid)

    if skip_in_db is not None:
        raise HTTPException(405, "Skip already exists")

    skip = SkipCreate(**skip.__dict__)
    result = await crud.skips.create_skip(db=db, skip=skip)

    return result