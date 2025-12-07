import os
import json
from openai import AsyncOpenAI
from typing import Optional


class OpenAIService:
    """OpenAI APIを使用してペット情報を自動生成するサービス"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            print("[OpenAIService] Warning: OPENAI_API_KEY not set")

    async def generate_pet_profile(
        self,
        animal_type: str,
        breed: str,
        color: Optional[str] = None,
        extra_features: Optional[dict] = None
    ) -> dict:
        """
        ClarifaiのAI分析結果を基に、ペット免許証の情報を自動生成

        Args:
            animal_type: 動物種別（犬、猫など）
            breed: 品種
            color: 毛色（オプション）
            extra_features: 追加特徴（オプション）
                - expression: 表情
                - posture: 姿勢
                - fur_amount: 毛量
                - size: サイズ
                - age_estimate: 推定年齢
                - other_traits: その他の特徴リスト

        Returns:
            dict: 生成された情報
                - gender: 性別
                - pet_name: ペット名
                - owner_name: 飼い主名
                - special_notes: 特記事項（5つ）
                - favorite_word: 免許の条件等（お好きな一言）
        """
        if not self.client:
            return self._get_default_profile()

        try:
            # 追加特徴の情報を構築
            extra_info = ""
            if extra_features:
                if extra_features.get("expression"):
                    extra_info += f"- 表情: {extra_features['expression']}\n"
                if extra_features.get("posture"):
                    extra_info += f"- 姿勢: {extra_features['posture']}\n"
                if extra_features.get("fur_amount"):
                    extra_info += f"- 毛量/毛質: {extra_features['fur_amount']}\n"
                if extra_features.get("size"):
                    extra_info += f"- サイズ: {extra_features['size']}\n"
                if extra_features.get("age_estimate"):
                    extra_info += f"- 推定年齢: {extra_features['age_estimate']}\n"
                if extra_features.get("other_traits") and len(extra_features["other_traits"]) > 0:
                    traits_str = "、".join(extra_features["other_traits"])
                    extra_info += f"- その他の特徴: {traits_str}\n"

            prompt = f"""あなたはペット健康免許証を作成するアシスタントです。
以下のペット情報を基に、免許証に記載する情報を日本語で生成してください。

ペット情報:
- 動物種別: {animal_type}
- 品種: {breed}
- 毛色: {color or '不明'}
{extra_info}
以下の項目を生成してください:
1. gender: 性別（オスまたはメス）- ランダムに選択
2. pet_name: ペットの名前 - {animal_type}や{breed}に合う可愛らしい日本語の名前
   - 2〜8文字のひらがな、カタカナ、または漢字混じりでもOK
   - 例: ポチ、ミケ、ハナコ、小太郎、さくら、チョコ、むぎ、大福、レオン、ひなた
3. owner_name: 飼い主のハンドルネーム - ペットの飼い主らしい可愛いニックネーム
   - 日本人の本名ではなく、SNSで使うような親しみやすいハンドルネーム
   - 例: ぽちママ、もふもふパパ、にゃんこ大好き、わんこの母、ねこ吉、柴犬のおかあさん、みけねこ係長
4. special_notes: 特記事項 - そのペットの性格や特徴を表す短い言葉を5つ（各3〜5文字）
   - 画像から検出された特徴（表情、姿勢、毛量など）を参考にして、そのペットにぴったりな特徴を自動生成してください
   - 既存の選択肢から選ぶのではなく、ペットの個性に合わせてオリジナルの特徴を考えてください
   - 参考例: もふもふ、つぶらな瞳、マイペース、よく寝る、食いしん坊、甘えん坊、元気っ子、おとなしい、人なつこい、いたずら好き、ふわふわ、お座り上手、散歩好き、ボール好き
5. favorite_word: お好きな一言 - そのペットらしい可愛いキャッチフレーズ（15文字以内）
   - 検出された表情や特徴を反映した一言にしてください

JSONフォーマットで出力してください:
{{
  "gender": "オス or メス",
  "pet_name": "ペット名",
  "owner_name": "ハンドルネーム",
  "special_notes": ["特徴1", "特徴2", "特徴3", "特徴4", "特徴5"],
  "favorite_word": "キャッチフレーズ"
}}"""

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたはペット免許証作成のアシスタントです。必ずJSONフォーマットで回答してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)

            # 特記事項が5つ未満の場合はデフォルト値で補完
            if len(result.get("special_notes", [])) < 5:
                defaults = ["もふもふ", "つぶらな瞳", "マイペース", "良く寝る", "食欲旺盛"]
                special_notes = result.get("special_notes", [])
                for default in defaults:
                    if len(special_notes) >= 5:
                        break
                    if default not in special_notes:
                        special_notes.append(default)
                result["special_notes"] = special_notes[:5]

            return result

        except Exception as e:
            print(f"[OpenAIService] Error generating profile: {e}")
            return self._get_default_profile()

    def _get_default_profile(self) -> dict:
        """デフォルトのプロフィールを返す"""
        return {
            "gender": "オス",
            "pet_name": "ポチ",
            "owner_name": "わんこの母",
            "special_notes": ["もふもふ", "つぶらな瞳", "マイペース", "よく寝る", "食いしん坊"],
            "favorite_word": "元気いっぱい！"
        }
