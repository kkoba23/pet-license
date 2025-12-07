from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel

from app.database import get_db
from app.models.database_models import Event, License
from app.services.s3_service import S3Service

router = APIRouter()
s3_service = S3Service()


class LicenseResponse(BaseModel):
    id: int
    receipt_number: Optional[str] = None
    pet_name: str
    owner_name: str
    animal_type: Optional[str] = None
    breed: Optional[str] = None
    color: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    favorite_food: Optional[str] = None
    favorite_word: Optional[str] = None
    microchip_no: Optional[str] = None
    license_image_url: str
    original_image_url: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class LicenseSaveResponse(BaseModel):
    id: int
    license_image_url: str
    original_image_url: Optional[str] = None
    receipt_number: str
    message: str


class PaginatedLicenseResponse(BaseModel):
    items: List[LicenseResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class NewLicensesResponse(BaseModel):
    items: List[LicenseResponse]
    total_count: int


def _license_to_response(lic: License) -> LicenseResponse:
    """LicenseモデルをLicenseResponseに変換するヘルパー"""
    return LicenseResponse(
        id=lic.id,
        receipt_number=lic.receipt_number,
        pet_name=lic.pet_name,
        owner_name=lic.owner_name,
        animal_type=lic.animal_type,
        breed=lic.breed,
        color=lic.color,
        birth_date=lic.birth_date.isoformat() if lic.birth_date else None,
        gender=lic.gender,
        favorite_food=lic.favorite_food,
        favorite_word=lic.favorite_word,
        microchip_no=lic.microchip_no,
        license_image_url=lic.license_image_url,
        original_image_url=lic.original_image_url,
        created_at=lic.created_at.isoformat() if lic.created_at else None
    )


# ===========================================
# 静的パスルート（by-event-id）を先に定義
# FastAPIはルート定義順で照合するため、
# 動的パス {event_code} より前に配置する必要がある
# ===========================================

@router.get("/by-event-id/{event_id}", response_model=List[LicenseResponse])
async def list_licenses_by_event_id(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    イベントIDに紐づく免許証一覧を取得（管理者向け・後方互換）
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    licenses = db.query(License).filter(
        License.event_id == event.id
    ).order_by(License.created_at.desc()).all()

    return [_license_to_response(lic) for lic in licenses]


@router.get("/by-event-id/{event_id}/paginated", response_model=PaginatedLicenseResponse)
async def list_licenses_by_event_id_paginated(
    event_id: int,
    page: int = Query(1, ge=1, description="ページ番号（1から開始）"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db)
):
    """
    イベントIDに紐づく免許証一覧をページングで取得（管理者向け）
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    total = db.query(License).filter(License.event_id == event.id).count()
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    offset = (page - 1) * per_page
    licenses = db.query(License).filter(
        License.event_id == event.id
    ).order_by(License.created_at.desc()).offset(offset).limit(per_page).all()

    return PaginatedLicenseResponse(
        items=[_license_to_response(lic) for lic in licenses],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/by-event-id/{event_id}/new", response_model=NewLicensesResponse)
async def list_new_licenses_by_event_id(
    event_id: int,
    since_id: int = Query(0, ge=0, description="このID以降の新規データを取得"),
    db: Session = Depends(get_db)
):
    """
    イベントIDに紐づく新規免許証のみ取得（管理者向けポーリング用）
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    total_count = db.query(License).filter(License.event_id == event.id).count()

    new_licenses = db.query(License).filter(
        License.event_id == event.id,
        License.id > since_id
    ).order_by(License.created_at.desc()).all()

    return NewLicensesResponse(
        items=[_license_to_response(lic) for lic in new_licenses],
        total_count=total_count
    )


# ===========================================
# 動的パスルート（{event_code}）を後に定義
# ===========================================

@router.post("/{event_code}/save", response_model=LicenseSaveResponse)
async def save_license(
    event_code: str,
    license_image: UploadFile = File(...),
    original_image: UploadFile = File(None),
    pet_name: str = Form(...),
    owner_name: str = Form(...),
    animal_type: str = Form(None),
    breed: str = Form(None),
    color: str = Form(None),
    birth_date: str = Form(None),
    gender: str = Form(None),
    favorite_food: str = Form(None),
    favorite_word: str = Form(None),
    microchip_no: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    免許証を保存する
    """
    event = db.query(Event).filter(Event.event_code == event_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")
    if not event.is_active:
        raise HTTPException(status_code=403, detail="このイベントは現在無効です")

    existing_count = db.query(License).filter(License.event_id == event.id).count()
    receipt_number = f"{existing_count + 1:04d}"

    try:
        license_bytes = await license_image.read()
        license_upload = await s3_service.upload_image(
            license_bytes,
            event_code=event_code
        )

        original_upload = None
        if original_image:
            original_bytes = await original_image.read()
            original_upload = await s3_service.upload_original_image(
                original_bytes,
                event_code=event_code
            )

        birth_date_obj = None
        if birth_date:
            try:
                birth_date_obj = date.fromisoformat(birth_date)
            except ValueError:
                pass

        new_license = License(
            event_id=event.id,
            receipt_number=receipt_number,
            pet_name=pet_name,
            owner_name=owner_name,
            animal_type=animal_type,
            breed=breed,
            color=color,
            birth_date=birth_date_obj,
            gender=gender,
            favorite_food=favorite_food,
            favorite_word=favorite_word,
            microchip_no=microchip_no,
            license_image_url=license_upload["url"],
            original_image_url=original_upload["url"] if original_upload else None,
            s3_license_key=license_upload["key"],
            s3_original_key=original_upload["key"] if original_upload else None,
        )
        db.add(new_license)
        db.commit()
        db.refresh(new_license)

        return LicenseSaveResponse(
            id=new_license.id,
            license_image_url=new_license.license_image_url,
            original_image_url=new_license.original_image_url,
            receipt_number=receipt_number,
            message="免許証を保存しました"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存に失敗しました: {str(e)}")


@router.get("/{event_code}", response_model=List[LicenseResponse])
async def list_licenses(
    event_code: str,
    db: Session = Depends(get_db)
):
    """
    イベントに紐づく免許証一覧を取得（後方互換性のため残す）
    """
    event = db.query(Event).filter(Event.event_code == event_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    licenses = db.query(License).filter(
        License.event_id == event.id
    ).order_by(License.created_at.desc()).all()

    return [_license_to_response(lic) for lic in licenses]


@router.get("/{event_code}/paginated", response_model=PaginatedLicenseResponse)
async def list_licenses_paginated(
    event_code: str,
    page: int = Query(1, ge=1, description="ページ番号（1から開始）"),
    per_page: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db)
):
    """
    イベントに紐づく免許証一覧をページングで取得
    """
    event = db.query(Event).filter(Event.event_code == event_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    total = db.query(License).filter(License.event_id == event.id).count()
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    offset = (page - 1) * per_page
    licenses = db.query(License).filter(
        License.event_id == event.id
    ).order_by(License.created_at.desc()).offset(offset).limit(per_page).all()

    return PaginatedLicenseResponse(
        items=[_license_to_response(lic) for lic in licenses],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{event_code}/new", response_model=NewLicensesResponse)
async def list_new_licenses(
    event_code: str,
    since_id: int = Query(0, ge=0, description="このID以降の新規データを取得"),
    db: Session = Depends(get_db)
):
    """
    指定したID以降の新規免許証のみ取得（ポーリング用）
    """
    event = db.query(Event).filter(Event.event_code == event_code).first()
    if not event:
        raise HTTPException(status_code=404, detail="イベントが見つかりません")

    total_count = db.query(License).filter(License.event_id == event.id).count()

    new_licenses = db.query(License).filter(
        License.event_id == event.id,
        License.id > since_id
    ).order_by(License.created_at.desc()).all()

    return NewLicensesResponse(
        items=[_license_to_response(lic) for lic in new_licenses],
        total_count=total_count
    )


@router.delete("/{license_id}")
async def delete_license(
    license_id: int,
    db: Session = Depends(get_db)
):
    """
    免許証を削除
    """
    license = db.query(License).filter(License.id == license_id).first()
    if not license:
        raise HTTPException(status_code=404, detail="免許証が見つかりません")

    try:
        if license.s3_license_key:
            await s3_service.delete_image(license.s3_license_key)
        if license.s3_original_key:
            await s3_service.delete_image(license.s3_original_key)
    except Exception:
        pass

    db.delete(license)
    db.commit()

    return {"message": "免許証を削除しました"}
