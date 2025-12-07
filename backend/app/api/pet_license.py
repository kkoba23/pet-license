from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional
import base64

from app.models.pet import PetInfo, LicenseResponse, ExtraFeatures
from app.services.clarifai_service import ClarifaiService
from app.services.s3_service import S3Service
from app.services.license_generator import LicenseGenerator
from app.services.openai_service import OpenAIService

router = APIRouter()

clarifai_service = ClarifaiService()
s3_service = S3Service()
license_generator = LicenseGenerator()
openai_service = OpenAIService()

@router.post("/analyze-pet")
async def analyze_pet(file: UploadFile = File(...)):
    """
    ペット画像を分析してAIで動物種別・品種を判定

    Args:
        file: アップロードされたペット画像

    Returns:
        PetInfo: AI判定結果
    """
    try:
        # 画像データを読み込み
        image_bytes = await file.read()

        # Clarifai APIで分析
        result = await clarifai_service.identify_pet(image_bytes)

        # 追加特徴を構築
        extra_features_data = result.get("extra_features")
        extra_features = None
        if extra_features_data:
            extra_features = ExtraFeatures(
                expression=extra_features_data.get("expression"),
                posture=extra_features_data.get("posture"),
                fur_amount=extra_features_data.get("fur_amount"),
                mood=extra_features_data.get("mood"),
                size=extra_features_data.get("size"),
                age_estimate=extra_features_data.get("age_estimate"),
                other_traits=extra_features_data.get("other_traits", [])
            )

        return PetInfo(
            animal_type=result["animal_type"],
            breed=result["breed"],
            confidence=result["confidence"],
            color=result.get("color"),
            general_confidence=result.get("general_confidence"),
            breed_confidence=result.get("breed_confidence"),
            extra_features=extra_features
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-license", response_model=LicenseResponse)
async def generate_license(
    pet_image: UploadFile = File(...),
    owner_name: str = Form(...),
    pet_name: str = Form(...),
    issue_location: str = Form(...),
    issue_date: str = Form(...),
    gender: str = Form(...),
    color: Optional[str] = Form(None),
    favorite_word: Optional[str] = Form(None),
    microchip_no: Optional[str] = Form(None)
):
    """
    ペット健康免許証を生成

    Args:
        pet_image: ペット画像
        owner_name: 飼い主名
        pet_name: ペット名
        issue_location: 交付場所
        issue_date: 交付日 (YYYY-MM-DD)
        gender: 性別
        color: 毛色（オプション）
        favorite_word: お好きな一言（オプション）
        microchip_no: マイクロチップNo（オプション）

    Returns:
        LicenseResponse: 生成された免許証情報
    """
    try:
        # 画像データを読み込み
        pet_image_bytes = await pet_image.read()

        # 1. Clarifai APIでペット分析
        pet_analysis = await clarifai_service.identify_pet(pet_image_bytes)

        # 2. オリジナル画像をS3に保存
        original_upload = await s3_service.upload_original_image(
            pet_image_bytes,
            filename=f"originals/{pet_name}_{owner_name}_original.jpg"
        )

        # 3. 免許証画像を生成
        issue_date_obj = date.fromisoformat(issue_date)

        license_image_bytes = await license_generator.generate_license(
            pet_image_bytes=pet_image_bytes,
            owner_name=owner_name,
            pet_name=pet_name,
            issue_location=issue_location,
            issue_date=issue_date_obj,
            animal_type=pet_analysis["animal_type"],
            breed=pet_analysis["breed"],
            gender=gender,
            color=color or pet_analysis.get("color"),
            favorite_word=favorite_word,
            microchip_no=microchip_no
        )

        # 4. 生成した免許証をS3に保存
        license_upload = await s3_service.upload_image(
            license_image_bytes,
            filename=f"licenses/{pet_name}_{owner_name}_license.png"
        )

        # 5. レスポンスを返す
        return LicenseResponse(
            license_image_url=license_upload["url"],
            pet_info=PetInfo(
                animal_type=pet_analysis["animal_type"],
                breed=pet_analysis["breed"],
                confidence=pet_analysis["confidence"],
                color=pet_analysis.get("color"),
                general_confidence=pet_analysis.get("general_confidence"),
                breed_confidence=pet_analysis.get("breed_confidence")
            ),
            s3_key=license_upload["key"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test():
    """動作確認用エンドポイント"""
    return {"message": "Pet License API is working"}


@router.post("/generate-profile")
async def generate_profile(
    animal_type: str = Form(...),
    breed: str = Form(...),
    color: Optional[str] = Form(None),
    expression: Optional[str] = Form(None),
    posture: Optional[str] = Form(None),
    fur_amount: Optional[str] = Form(None),
    size: Optional[str] = Form(None),
    age_estimate: Optional[str] = Form(None),
    other_traits: Optional[str] = Form(None)
):
    """
    OpenAI APIを使用してペットプロフィールを自動生成

    Args:
        animal_type: 動物種別（犬、猫など）
        breed: 品種
        color: 毛色（オプション）
        expression: 表情（オプション）
        posture: 姿勢（オプション）
        fur_amount: 毛量（オプション）
        size: サイズ（オプション）
        age_estimate: 推定年齢（オプション）
        other_traits: その他の特徴（カンマ区切り、オプション）

    Returns:
        dict: 生成されたプロフィール
            - gender: 性別
            - pet_name: ペット名
            - owner_name: 飼い主名
            - special_notes: 特記事項（5つ）
            - favorite_word: お好きな一言
    """
    try:
        # other_traitsをリストに変換
        other_traits_list = other_traits.split(",") if other_traits else []

        extra_features = {
            "expression": expression,
            "posture": posture,
            "fur_amount": fur_amount,
            "size": size,
            "age_estimate": age_estimate,
            "other_traits": other_traits_list
        }

        profile = await openai_service.generate_pet_profile(
            animal_type=animal_type,
            breed=breed,
            color=color,
            extra_features=extra_features
        )
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
