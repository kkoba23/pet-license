from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date


class ExtraFeatures(BaseModel):
    """追加特徴モデル（表情・姿勢・毛量など）"""
    expression: Optional[str] = None  # 表情
    posture: Optional[str] = None  # 姿勢
    fur_amount: Optional[str] = None  # 毛量
    mood: Optional[str] = None  # 気分
    size: Optional[str] = None  # サイズ
    age_estimate: Optional[str] = None  # 推定年齢
    other_traits: List[str] = []  # その他の特徴


class PetInfo(BaseModel):
    """ペット情報モデル"""
    animal_type: str  # 犬 or 猫
    breed: str  # 品種
    color: Optional[str] = None  # 毛色
    confidence: float  # AI判定の信頼度
    general_confidence: Optional[float] = None  # 一般認識の信頼度
    breed_confidence: Optional[float] = None  # 品種認識の信頼度
    extra_features: Optional[ExtraFeatures] = None  # 追加特徴

class LicenseRequest(BaseModel):
    """免許証生成リクエスト"""
    owner_name: str  # 飼い主名
    pet_name: str  # ペット名
    issue_location: str  # 交付場所
    issue_date: date  # 交付日
    gender: str  # 性別
    color: Optional[str] = None  # 毛色（AIで判定できない場合は入力）
    favorite_word: Optional[str] = None  # お好きな一言
    microchip_no: Optional[str] = None  # マイクロチップNo

class LicenseResponse(BaseModel):
    """免許証生成レスポンス"""
    license_image_url: str  # 生成された免許証画像のURL
    pet_info: PetInfo  # AI判定結果
    s3_key: str  # S3に保存された画像のキー
