from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import date, timedelta
from typing import Optional, Tuple
import os
from pathlib import Path

class LicenseGenerator:
    """ペット健康免許証画像生成サービス"""

    def __init__(self):
        # テンプレート画像のパス
        self.template_path = os.path.join(
            os.path.dirname(__file__),
            "../../../image/template.png"
        )

    def _find_japanese_font(self) -> Optional[str]:
        """日本語フォントを検索"""
        font_candidates = [
            # プロジェクト内のフォント
            Path(__file__).parent.parent / "fonts" / "NotoSansJP-Regular.otf",
            Path(__file__).parent.parent / "fonts" / "NotoSansJP-Regular.ttf",
            # Linux用
            "/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
            # Windows用
            "C:\\Windows\\Fonts\\msgothic.ttc",
            "C:\\Windows\\Fonts\\meiryo.ttc",
            # macOS用
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/Library/Fonts/ヒラギノ角ゴ ProN W3.otf",
        ]

        for font_path in font_candidates:
            if isinstance(font_path, Path):
                font_path = str(font_path)
            if os.path.exists(font_path):
                return font_path
        return None

    def _load_japanese_fonts(self) -> Tuple:
        """日本語フォントを読み込む"""
        font_path = self._find_japanese_font()

        try:
            if font_path:
                print(f"Using font: {font_path}")
                font_large = ImageFont.truetype(font_path, 18)
                font_medium = ImageFont.truetype(font_path, 14)
                font_small = ImageFont.truetype(font_path, 12)
            else:
                print("Warning: No Japanese font found. Using default font.")
                print("Japanese text may not display correctly.")
                print("Please see FONT_SETUP.md for font installation instructions.")
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except Exception as e:
            print(f"Font loading error: {e}")
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        return font_large, font_medium, font_small

    def _crop_and_resize_for_license(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """
        免許証用に画像を中央トリミング&リサイズ

        Args:
            img: 元画像
            target_size: 目標サイズ (width, height)

        Returns:
            Image: トリミング・リサイズされた画像
        """
        # 目標アスペクト比を計算
        target_width, target_height = target_size
        target_ratio = target_width / target_height

        # 元画像のサイズとアスペクト比
        original_width, original_height = img.size
        original_ratio = original_width / original_height

        # 中央を基準にクロップする領域を計算
        if original_ratio > target_ratio:
            # 横長の画像: 高さを基準に、幅を中央でクロップ
            new_height = original_height
            new_width = int(original_height * target_ratio)
            left = (original_width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = original_height
        else:
            # 縦長または正方形の画像: 幅を基準に、高さを上部寄りでクロップ
            new_width = original_width
            new_height = int(original_width / target_ratio)
            left = 0
            # 上部30%の位置からクロップ（顔が上部にあることが多いため）
            top = int(original_height * 0.1)
            # クロップ領域が画像をはみ出す場合は調整
            if top + new_height > original_height:
                top = original_height - new_height
            right = original_width
            bottom = top + new_height

        # クロップ
        cropped_img = img.crop((left, top, right, bottom))

        # リサイズ
        resized_img = cropped_img.resize(target_size, Image.Resampling.LANCZOS)

        print(f"画像トリミング: 元サイズ {img.size} -> クロップ {cropped_img.size} -> リサイズ {resized_img.size}")

        return resized_img

    def _draw_borders_and_lines(self, draw: ImageDraw.Draw, width: int, height: int):
        """罫線と枠線を描画"""
        border_color = (0, 0, 0)
        line_width = 2

        # 外枠（角丸四角形）
        margin = 10
        draw.rounded_rectangle(
            [(margin, margin), (width - margin, height - margin)],
            radius=15,
            outline=border_color,
            width=4
        )

        # 内枠
        inner_margin = 20
        draw.rounded_rectangle(
            [(inner_margin, inner_margin), (width - inner_margin, height - inner_margin)],
            radius=10,
            outline=border_color,
            width=2
        )

        # 氏名欄の罫線
        draw.line([(90, 50), (560, 50)], fill=border_color, width=line_width)

        # 交付場所欄の罫線
        draw.line([(90, 85), (660, 85)], fill=border_color, width=line_width)

        # 交付欄の罫線
        draw.line([(90, 115), (360, 115)], fill=border_color, width=line_width)

        # 有効期限の背景色（薄い緑）
        draw.rectangle([(20, 125), (360, 150)], fill=(230, 255, 230))

        # ペット情報セクションの罫線
        # 性別
        draw.line([(90, 170), (280, 170)], fill=border_color, width=1)
        # 種類
        draw.line([(90, 190), (280, 190)], fill=border_color, width=1)
        # 毛色
        draw.line([(90, 210), (280, 210)], fill=border_color, width=1)
        # 名称
        draw.line([(90, 230), (280, 230)], fill=border_color, width=1)

        # お好きな一言セクション
        draw.rectangle([(20, 250), (470, 290)], outline=border_color, width=line_width)

        # マイクロチップNoセクション
        draw.rectangle([(20, 300), (470, 340)], outline=border_color, width=line_width)

        # ペット画像枠
        draw.rectangle([(475, 85), (665, 280)], outline=border_color, width=2)

    async def generate_license(
        self,
        pet_image_bytes: bytes,
        owner_name: str,
        pet_name: str,
        issue_location: str,
        issue_date: date,
        animal_type: str,
        breed: str,
        gender: str,
        color: Optional[str] = None,
        favorite_word: Optional[str] = None,
        microchip_no: Optional[str] = None
    ) -> bytes:
        """
        ペット健康免許証画像を生成

        Args:
            pet_image_bytes: ペット画像のバイトデータ
            owner_name: 飼い主名
            pet_name: ペット名
            issue_location: 交付場所
            issue_date: 交付日
            animal_type: 動物種別（犬/猫）
            breed: 品種
            gender: 性別
            color: 毛色
            favorite_word: お好きな一言
            microchip_no: マイクロチップNo

        Returns:
            bytes: 生成された免許証画像のバイトデータ
        """
        try:
            # テンプレート画像を読み込み（なければ新規作成）
            if os.path.exists(self.template_path):
                license_img = Image.open(self.template_path).copy()
            else:
                # テンプレートがない場合は白背景で作成
                width, height = 680, 430
                license_img = Image.new('RGB', (width, height), 'white')

            # 描画オブジェクト作成
            draw = ImageDraw.Draw(license_img)

            # 罫線と枠線を描画
            self._draw_borders_and_lines(draw, license_img.width, license_img.height)

            # フォント設定（日本語対応フォント）
            font_large, font_medium, font_small = self._load_japanese_fonts()

            # 生年月日を計算（仮の値）
            birth_date = issue_date.replace(year=issue_date.year - 3)

            # 有効期限を計算（交付日から3年後）
            valid_until = issue_date.replace(year=issue_date.year + 3)

            # テキスト配置（座標は画像に合わせて調整が必要）
            text_color = (0, 0, 0)

            # ラベル
            draw.text((30, 30), "氏名", fill=text_color, font=font_small)
            draw.text((30, 65), "交付場所", fill=text_color, font=font_small)
            draw.text((30, 95), "交付", fill=text_color, font=font_small)

            # 氏名
            draw.text((100, 28), f"{owner_name}", fill=text_color, font=font_medium)

            # 生年月日
            draw.text((480, 28), f"{birth_date.strftime('%Y年%m月%d日')} 生", fill=text_color, font=font_small)

            # 交付場所
            draw.text((100, 63), issue_location, fill=text_color, font=font_small)

            # 交付日
            draw.text((100, 93), issue_date.strftime("%Y年 %m月 %d日"), fill=text_color, font=font_small)

            # 有効期限
            draw.text((30, 130), f"{valid_until.strftime('%Y年（令和%m）%m月%d日')} まで有効", fill=(0, 128, 0), font=font_medium)

            # ペット情報ラベル
            draw.text((30, 155), "性別　：", fill=text_color, font=font_small)
            draw.text((30, 175), "種類　：", fill=text_color, font=font_small)
            draw.text((30, 195), "毛色　：", fill=text_color, font=font_small)
            draw.text((30, 215), "名称　：", fill=text_color, font=font_small)

            # ペット情報
            draw.text((100, 155), gender, fill=text_color, font=font_small)
            animal_display = f"{animal_type}" if animal_type else "不明"
            draw.text((100, 175), animal_display, fill=text_color, font=font_small)
            if color:
                draw.text((100, 195), color, fill=text_color, font=font_small)
            draw.text((100, 215), pet_name, fill=text_color, font=font_small)

            # お好きな一言
            draw.text((30, 255), "お好きな一言", fill=text_color, font=font_small)
            if favorite_word:
                draw.text((140, 265), favorite_word, fill=text_color, font=font_small)

            # マイクロチップNo
            draw.text((30, 305), "マイクロチップNo.", fill=text_color, font=font_small)
            if microchip_no:
                draw.text((30, 320), microchip_no, fill=text_color, font=font_small)

            # ペット画像を配置
            pet_img = Image.open(BytesIO(pet_image_bytes))

            # ペット画像を免許証用にトリミング・リサイズ
            pet_img_cropped = self._crop_and_resize_for_license(pet_img, target_size=(185, 190))

            # ペット画像を貼り付け（右上のエリア）
            pet_position = (480, 90)
            license_img.paste(pet_img_cropped, pet_position)

            # 「ペット免許証」縦書きテキスト（右側）
            draw.text((650, 150), "ペ", fill=(100, 180, 100), font=font_medium)
            draw.text((650, 170), "ッ", fill=(100, 180, 100), font=font_medium)
            draw.text((650, 190), "ト", fill=(100, 180, 100), font=font_medium)
            draw.text((650, 210), "免", fill=(100, 180, 100), font=font_medium)
            draw.text((650, 230), "許", fill=(100, 180, 100), font=font_medium)
            draw.text((650, 250), "証", fill=(100, 180, 100), font=font_medium)

            # 画像をバイトデータに変換
            output = BytesIO()
            license_img.save(output, format='PNG', quality=95)
            output.seek(0)

            return output.getvalue()

        except Exception as e:
            raise Exception(f"免許証生成エラー: {str(e)}")
