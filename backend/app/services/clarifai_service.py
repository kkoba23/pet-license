from clarifai.client.model import Model
import os
import base64
from typing import Dict

class ClarifaiService:
    """Clarifai APIを使用したペット認識サービス（ハイブリッド方式）"""

    def __init__(self):
        self.api_key = os.getenv("CLARIFAI_API_KEY")

    async def identify_pet(self, image_bytes: bytes) -> Dict:
        """
        ハイブリッド方式でペット画像を分析
        1. 一般モデルで犬/猫を判別
        2. 判別結果に応じて専用モデルで詳細な品種を識別

        Args:
            image_bytes: 画像のバイトデータ

        Returns:
            Dict: 判定結果 {animal_type, breed, confidence, color}
        """
        try:
            # ステップ1: 一般画像認識モデルで犬/猫を判別
            general_model = Model(
                url="https://clarifai.com/clarifai/main/models/general-image-recognition",
                pat=self.api_key
            )

            general_prediction = general_model.predict_by_bytes(
                image_bytes,
                input_type="image"
            )

            concepts = general_prediction.outputs[0].data.concepts
            animal_type = None
            general_confidence = 0.0

            # 犬・猫の判定
            for concept in concepts[:10]:
                name = concept.name.lower()
                confidence = concept.value

                if not animal_type:
                    if "dog" in name or "canine" in name or "puppy" in name:
                        animal_type = "犬"
                        general_confidence = confidence
                        break
                    elif "cat" in name or "feline" in name or "kitten" in name:
                        animal_type = "猫"
                        general_confidence = confidence
                        break

            # ステップ2: 専用モデルで品種を詳細に識別
            breed = "ミックス"
            breed_confidence = 0.0
            color = None

            if animal_type == "犬":
                breed, breed_confidence, color = await self._identify_dog_breed(image_bytes)
            elif animal_type == "猫":
                breed, breed_confidence, color = await self._identify_cat_breed(image_bytes)

            # デフォルト値
            if not animal_type:
                animal_type = "不明"

            # 追加特徴を抽出（表情・姿勢・毛量など）
            extra_features = self._extract_extra_features(concepts)

            return {
                "animal_type": animal_type,
                "breed": breed,
                "confidence": max(general_confidence, breed_confidence),
                "general_confidence": general_confidence,
                "breed_confidence": breed_confidence,
                "color": color,
                "raw_concepts": [{"name": c.name, "confidence": c.value} for c in concepts[:20]],
                "extra_features": extra_features
            }

        except Exception as e:
            raise Exception(f"ペット認識エラー: {str(e)}")

    async def _identify_dog_breed(self, image_bytes: bytes) -> tuple:
        """
        一般モデルで犬の品種を識別
        (general-image-recognition モデルを使用)

        Returns:
            tuple: (品種名, 信頼度, 毛色)
        """
        try:
            # 一般画像認識モデルを使用
            general_model = Model(
                url="https://clarifai.com/clarifai/main/models/general-image-recognition",
                pat=self.api_key
            )

            prediction = general_model.predict_by_bytes(
                image_bytes,
                input_type="image"
            )

            concepts = prediction.outputs[0].data.concepts

            # 犬の品種を検出
            dog_breeds = {
                "golden retriever": "ゴールデンレトリバー",
                "labrador": "ラブラドール",
                "labrador retriever": "ラブラドール",
                "poodle": "プードル",
                "toy poodle": "トイプードル",
                "chihuahua": "チワワ",
                "bulldog": "ブルドッグ",
                "french bulldog": "フレンチブルドッグ",
                "beagle": "ビーグル",
                "shiba": "柴犬",
                "shiba inu": "柴犬",
                "corgi": "コーギー",
                "welsh corgi": "コーギー",
                "pug": "パグ",
                "husky": "ハスキー",
                "siberian husky": "シベリアンハスキー",
                "german shepherd": "ジャーマンシェパード",
                "dachshund": "ダックスフンド",
                "pomeranian": "ポメラニアン",
                "yorkshire": "ヨークシャーテリア",
                "maltese": "マルチーズ",
                "schnauzer": "シュナウザー",
                "boxer": "ボクサー",
                "dalmatian": "ダルメシアン",
                "rottweiler": "ロットワイラー",
                "doberman": "ドーベルマン",
                "saint bernard": "セントバーナード",
                "great dane": "グレートデーン",
            }

            # Color Recognition モデルで色を検出
            color = await self._detect_color(image_bytes)

            # 上位20件の概念から犬種を探す
            for concept in concepts[:20]:
                name = concept.name.lower()
                for breed_key, breed_jp in dog_breeds.items():
                    if breed_key in name:
                        print(f"犬種検出: {name} -> {breed_jp} (confidence: {concept.value:.2f})")
                        return breed_jp, concept.value, color

            # 品種が特定できない場合
            print(f"犬種が特定できませんでした。検出された概念: {[c.name for c in concepts[:10]]}")
            return "ミックス", 0.0, color

        except Exception as e:
            print(f"犬種識別エラー: {e}")
            return "ミックス", 0.0, None

    async def _identify_cat_breed(self, image_bytes: bytes) -> tuple:
        """
        一般モデルで猫の品種を識別
        (専用の猫種モデルが利用不可のため、一般画像認識を使用)

        Returns:
            tuple: (品種名, 信頼度, 毛色)
        """
        try:
            # 一般画像認識モデルを使用
            general_model = Model(
                url="https://clarifai.com/clarifai/main/models/general-image-recognition",
                pat=self.api_key
            )

            prediction = general_model.predict_by_bytes(
                image_bytes,
                input_type="image"
            )

            concepts = prediction.outputs[0].data.concepts

            # 猫の品種を検出
            cat_breeds = {
                "persian": "ペルシャ",
                "siamese": "シャム",
                "maine coon": "メインクーン",
                "ragdoll": "ラグドール",
                "bengal": "ベンガル",
                "british shorthair": "ブリティッシュショートヘア",
                "scottish fold": "スコティッシュフォールド",
                "sphynx": "スフィンクス",
                "abyssinian": "アビシニアン",
                "tabby": "タビー",
                "american shorthair": "アメリカンショートヘア",
                "russian blue": "ロシアンブルー",
                "norwegian forest": "ノルウェージャンフォレスト",
                "birman": "バーマン",
                "exotic shorthair": "エキゾチックショートヘア",
                "somali": "ソマリ",
                "oriental": "オリエンタル",
                "burmese": "バーミーズ",
                "tonkinese": "トンキニーズ",
                "turkish angora": "ターキッシュアンゴラ",
                "manx": "マンクス",
                "munchkin": "マンチカン",
                "himalayan": "ヒマラヤン",
                "chartreuse": "シャルトリュー",
                "egyptian mau": "エジプシャンマウ",
                "selkirk rex": "セルカークレックス",
                "cornish rex": "コーニッシュレックス",
                "devon rex": "デボンレックス",
                "calico": "三毛猫",
                "tortoiseshell": "サビ猫",
            }

            # Color Recognition モデルで色を検出
            color = await self._detect_color(image_bytes)

            # 上位20件の概念から猫種を探す
            for concept in concepts[:20]:
                name = concept.name.lower()
                for breed_key, breed_jp in cat_breeds.items():
                    if breed_key in name:
                        print(f"猫種検出: {name} -> {breed_jp} (confidence: {concept.value:.2f})")
                        return breed_jp, concept.value, color

            # 品種が特定できない場合
            print(f"猫種が特定できませんでした。検出された概念: {[c.name for c in concepts[:10]]}")
            return "ミックス", 0.0, color

        except Exception as e:
            print(f"猫種識別エラー: {e}")
            return "ミックス", 0.0, None

    async def _detect_color(self, image_bytes: bytes) -> str:
        """
        Color Recognition モデルで画像の主要な色を検出
        顔検出を使って体の部分から色を抽出

        Returns:
            str: 日本語の色名 (例: "オレンジ", "黒", "白")
        """
        try:
            # まず顔検出を試みる
            face_region_bytes = await self._extract_body_region(image_bytes)

            # 顔検出に成功した場合は、体の部分から色を検出
            # 失敗した場合は元の画像全体から色を検出
            target_bytes = face_region_bytes if face_region_bytes else image_bytes

            color_model = Model(
                url="https://clarifai.com/clarifai/main/models/color-recognition",
                pat=self.api_key
            )

            prediction = color_model.predict_by_bytes(
                target_bytes,
                input_type="image"
            )

            colors = prediction.outputs[0].data.colors

            if colors and len(colors) > 0:
                # 背景色を除外するリスト（グレー、白系の無彩色）
                background_colors = [
                    "gray", "grey", "darkgray", "lightgray", "dimgray", "slategray",
                    "gainsboro", "whitesmoke", "lightsteelblue", "lightslategray"
                ]

                # 英語の色名を日本語に変換
                color_translation = {
                    "orange": "オレンジ",
                    "darkorange": "オレンジ",
                    "sandybrown": "オレンジ",
                    "coral": "オレンジ",
                    "tomato": "オレンジ",
                    "black": "黒",
                    "white": "白",
                    "brown": "茶",
                    "gray": "グレー",
                    "grey": "グレー",
                    "darkgray": "グレー",
                    "lightgray": "グレー",
                    "gold": "ゴールデン",
                    "goldenrod": "ゴールデン",
                    "red": "赤茶",
                    "darkred": "赤茶",
                    "indianred": "赤茶",
                    "firebrick": "赤茶",
                    "cream": "クリーム",
                    "beige": "ベージュ",
                    "tan": "タン",
                    "blue": "ブルー",
                    "silver": "シルバー",
                    "yellow": "黄色",
                    "lightyellow": "クリーム",
                    "peru": "茶",
                    "sienna": "茶",
                    "saddlebrown": "茶",
                    "chocolate": "茶",
                    "burlywood": "ベージュ",
                    "wheat": "ベージュ",
                }

                # 上位5色をログ出力
                print(f"検出された色 (上位5色): {[(c.w3c.name, f'{c.value:.2f}') for c in colors[:5]]}")

                # 背景色を除外して、最も支配的な色を取得
                for color in colors[:5]:
                    color_name = color.w3c.name.lower()

                    # 背景色でない場合
                    if not any(bg in color_name for bg in background_colors):
                        print(f"ペットの毛色として選択: {color_name} (value: {color.value:.2f})")

                        # 色名を日本語に変換
                        for eng, jpn in color_translation.items():
                            if eng in color_name:
                                print(f"色を日本語に変換: {color_name} -> {jpn}")
                                return jpn

                        # 辞書にない場合はそのまま返す
                        print(f"辞書にない色: {color_name}")
                        return color_name.capitalize()

                # すべて背景色だった場合は、最初の色を返す
                top_color = colors[0]
                color_name = top_color.w3c.name.lower()
                print(f"背景色のみ検出、最初の色を使用: {color_name} (value: {top_color.value:.2f})")

                for eng, jpn in color_translation.items():
                    if eng in color_name:
                        return jpn

                return color_name.capitalize()

            print("色が検出されませんでした (Color Recognition)")
            return None

        except Exception as e:
            print(f"色検出エラー: {e}")
            return None

    async def _extract_body_region(self, image_bytes: bytes) -> bytes:
        """
        画像の中央部分を抽出（背景を除外してペットの体部分を取得）

        Returns:
            bytes: 体の領域の画像バイト（失敗した場合はNone）
        """
        try:
            from PIL import Image
            from io import BytesIO

            # 画像を読み込み
            img = Image.open(BytesIO(image_bytes))
            width, height = img.size

            # 画像の中央60%の領域を抽出（周辺の背景を除外）
            # 上下左右から20%ずつマージンを取る
            margin_horizontal = int(width * 0.2)
            margin_vertical = int(height * 0.2)

            left = margin_horizontal
            top = margin_vertical
            right = width - margin_horizontal
            bottom = height - margin_vertical

            print(f"中央領域抽出: 元サイズ {img.size} -> 領域 ({left},{top})-({right},{bottom})")

            # 領域が有効かチェック
            if bottom > top and right > left:
                # 中央領域をクロップ
                center_region = img.crop((left, top, right, bottom))

                # RGBAモードの場合はRGBに変換（JPEG保存のため）
                if center_region.mode == 'RGBA':
                    # 白背景で合成
                    rgb_img = Image.new('RGB', center_region.size, (255, 255, 255))
                    rgb_img.paste(center_region, mask=center_region.split()[3])  # アルファチャンネルをマスクとして使用
                    center_region = rgb_img

                # バイトデータに変換
                output = BytesIO()
                center_region.save(output, format='JPEG')
                output.seek(0)

                print(f"中央領域のサイズ: {center_region.size}")
                return output.getvalue()
            else:
                print("領域が無効です")
                return None

        except Exception as e:
            print(f"領域抽出エラー: {e}")
            return None

    def _extract_color_from_concepts(self, concepts) -> str:
        """
        概念リストから毛色を抽出
        """
        color_keywords = {
            "black": "黒",
            "white": "白",
            "brown": "茶",
            "gray": "グレー",
            "grey": "グレー",
            "golden": "ゴールデン",
            "red": "赤茶",
            "orange": "オレンジ",
            "cream": "クリーム",
            "tan": "タン",
            "blue": "ブルー",
            "silver": "シルバー",
            "yellow": "黄色",
            "beige": "ベージュ",
            "ginger": "茶トラ",
            "tabby": "トラ"
        }

        # デバッグ: より多くの概念をログ出力
        print(f"検出された概念 (色抽出用、上位20件): {[f'{c.name}:{c.value:.2f}' for c in concepts[:20]]}")

        # 上位20件の概念から色を探す
        for concept in concepts[:20]:
            name = concept.name.lower()
            for eng, jpn in color_keywords.items():
                if eng in name:
                    print(f"毛色検出: {name} -> {jpn}")
                    return jpn

        print("毛色が検出されませんでした")
        return None

    def _extract_extra_features(self, concepts) -> dict:
        """
        Clarifaiの概念リストから追加特徴を抽出
        （表情・姿勢・毛量・その他の特徴）

        Returns:
            dict: 抽出された特徴
                - expression: 表情（笑顔、眠そう、警戒など）
                - posture: 姿勢（座っている、立っている、寝ているなど）
                - fur_amount: 毛量（ふわふわ、短毛など）
                - mood: 気分（穏やか、活発など）
                - size: サイズ感（小型、大型など）
                - age_estimate: 推定年齢（子犬/子猫、成犬/成猫など）
                - other_traits: その他の特徴リスト
        """
        features = {
            "expression": None,
            "posture": None,
            "fur_amount": None,
            "mood": None,
            "size": None,
            "age_estimate": None,
            "other_traits": []
        }

        # 表情関連のキーワード
        expression_keywords = {
            "happy": "嬉しそう",
            "smiling": "笑顔",
            "sleepy": "眠そう",
            "sleeping": "眠っている",
            "alert": "警戒している",
            "curious": "好奇心旺盛",
            "relaxed": "リラックス",
            "calm": "穏やか",
            "playful": "遊び好き",
            "sad": "悲しそう",
            "surprised": "驚いている",
            "tongue": "舌を出している",
            "yawning": "あくび",
            "panting": "はあはあ",
        }

        # 姿勢関連のキーワード
        posture_keywords = {
            "sitting": "座っている",
            "standing": "立っている",
            "lying": "横になっている",
            "running": "走っている",
            "walking": "歩いている",
            "jumping": "ジャンプ",
            "stretching": "伸び",
            "curled": "丸まっている",
            "resting": "休んでいる",
        }

        # 毛量・毛質関連のキーワード
        fur_keywords = {
            "fluffy": "ふわふわ",
            "furry": "毛深い",
            "shaggy": "もじゃもじゃ",
            "smooth": "なめらか",
            "short hair": "短毛",
            "long hair": "長毛",
            "curly": "巻き毛",
            "soft": "柔らか",
            "silky": "シルキー",
            "woolly": "ウーリー",
            "thick": "厚い毛",
            "thin": "薄い毛",
        }

        # サイズ関連のキーワード
        size_keywords = {
            "small": "小型",
            "tiny": "極小",
            "large": "大型",
            "big": "大きい",
            "medium": "中型",
            "miniature": "ミニチュア",
            "giant": "超大型",
        }

        # 年齢関連のキーワード
        age_keywords = {
            "puppy": "子犬",
            "kitten": "子猫",
            "baby": "赤ちゃん",
            "young": "若い",
            "adult": "成体",
            "old": "老犬/老猫",
            "senior": "シニア",
        }

        # その他の興味深い特徴
        other_trait_keywords = {
            "cute": "かわいい",
            "adorable": "愛らしい",
            "beautiful": "美しい",
            "handsome": "凛々しい",
            "elegant": "優雅",
            "fat": "ぽっちゃり",
            "healthy": "健康的",
            "muscular": "筋肉質",
            "friendly": "フレンドリー",
            "gentle": "優しい",
            "outdoor": "アウトドア派",
            "indoor": "インドア派",
            "collar": "首輪あり",
            "spotted": "斑点模様",
            "striped": "縞模様",
        }

        found_traits = []

        # 概念を走査して特徴を抽出
        for concept in concepts:
            name = concept.name.lower()
            confidence = concept.value

            # 信頼度が低いものはスキップ
            if confidence < 0.3:
                continue

            # 表情の検出
            if not features["expression"]:
                for eng, jpn in expression_keywords.items():
                    if eng in name:
                        features["expression"] = jpn
                        print(f"表情検出: {name} -> {jpn} (confidence: {confidence:.2f})")
                        break

            # 姿勢の検出
            if not features["posture"]:
                for eng, jpn in posture_keywords.items():
                    if eng in name:
                        features["posture"] = jpn
                        print(f"姿勢検出: {name} -> {jpn} (confidence: {confidence:.2f})")
                        break

            # 毛量の検出
            if not features["fur_amount"]:
                for eng, jpn in fur_keywords.items():
                    if eng in name:
                        features["fur_amount"] = jpn
                        print(f"毛量検出: {name} -> {jpn} (confidence: {confidence:.2f})")
                        break

            # サイズの検出
            if not features["size"]:
                for eng, jpn in size_keywords.items():
                    if eng in name:
                        features["size"] = jpn
                        print(f"サイズ検出: {name} -> {jpn} (confidence: {confidence:.2f})")
                        break

            # 年齢の検出
            if not features["age_estimate"]:
                for eng, jpn in age_keywords.items():
                    if eng in name:
                        features["age_estimate"] = jpn
                        print(f"年齢検出: {name} -> {jpn} (confidence: {confidence:.2f})")
                        break

            # その他の特徴
            for eng, jpn in other_trait_keywords.items():
                if eng in name and jpn not in found_traits:
                    found_traits.append(jpn)
                    print(f"特徴検出: {name} -> {jpn} (confidence: {confidence:.2f})")

        features["other_traits"] = found_traits[:5]  # 最大5つまで

        print(f"抽出された追加特徴: {features}")
        return features

    def _translate_breed(self, breed_name: str) -> str:
        """
        英語の品種名を日本語に翻訳（主要な品種のみ）
        """
        breed_dict = {
            "golden retriever": "ゴールデンレトリバー",
            "labrador": "ラブラドール",
            "poodle": "プードル",
            "chihuahua": "チワワ",
            "bulldog": "ブルドッグ",
            "beagle": "ビーグル",
            "shiba": "柴犬",
            "corgi": "コーギー",
            "persian": "ペルシャ",
            "siamese": "シャム",
            "maine coon": "メインクーン",
            "ragdoll": "ラグドール",
            "bengal": "ベンガル",
            "british shorthair": "ブリティッシュショートヘア",
            "scottish fold": "スコティッシュフォールド",
        }

        breed_lower = breed_name.lower()
        for eng, jpn in breed_dict.items():
            if eng in breed_lower:
                return jpn

        # 辞書にない場合は英語のまま返す（頭文字を大文字に）
        return breed_name.title()
