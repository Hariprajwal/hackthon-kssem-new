from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models
from .auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class FileBase(BaseModel):
    name: str
    content: str
    folder_id: Optional[int] = None
    language: str = "python"

class FileCreate(FileBase):
    pass

class FileResponse(FileBase):
    id: int
    user_id: int
    last_modified: datetime

    class Config:
        orm_mode = True

class FolderBase(BaseModel):
    name: str

class FolderCreate(FolderBase):
    pass

class FolderResponse(FolderBase):
    id: int
    user_id: int
    files: List[FileResponse] = []

    class Config:
        orm_mode = True

# FOLDERS
@router.post("/folders", response_model=FolderResponse)
async def create_folder(folder: FolderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_folder = models.Folder(name=folder.name, user_id=current_user.id)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)
    return new_folder

@router.get("/folders", response_model=List[FolderResponse])
async def get_folders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Folder).filter(models.Folder.user_id == current_user.id).all()

# FILES
@router.post("/files", response_model=FileResponse)
async def create_file(file: FileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_file = models.File(**file.dict(), user_id=current_user.id)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

@router.get("/files", response_model=List[FileResponse])
async def get_files(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.File).filter(models.File.user_id == current_user.id).all()

@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    file = db.query(models.File).filter(models.File.id == file_id, models.File.user_id == current_user.id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.put("/files/{file_id}", response_model=FileResponse)
async def update_file(file_id: int, file_update: FileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_file = db.query(models.File).filter(models.File.id == file_id, models.File.user_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    for key, value in file_update.dict().items():
        setattr(db_file, key, value)
    
    db_file.last_modified = datetime.utcnow()
    db.commit()
    db.refresh(db_file)
    return db_file

@router.delete("/files/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_file = db.query(models.File).filter(models.File.id == file_id, models.File.user_id == current_user.id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(db_file)
    db.commit()
    return {"status": "success"}

@router.get("/explorer")
async def get_explorer_data(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    folders = db.query(models.Folder).filter(models.Folder.user_id == current_user.id).all()
    # files without folders
    orphan_files = db.query(models.File).filter(models.File.user_id == current_user.id, models.File.folder_id == None).all()
    
    return {
        "folders": folders,
        "orphan_files": orphan_files
    }
