import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
from typing import Optional
import uuid
from pathlib import Path

class S3Service:
    """AWS S3ストレージサービス（開発モードはローカル保存）"""

    def __init__(self):
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        self.region = os.getenv("AWS_REGION", "ap-northeast-1")

        # 開発モード判定（AWS認証情報がない場合）
        aws_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.dev_mode = not aws_key or aws_key == "your_aws_access_key"

        # デバッグログ
        print(f"[S3Service Init] AWS_ACCESS_KEY_ID: {aws_key}")
        print(f"[S3Service Init] AWS_S3_BUCKET: {self.bucket_name}")
        print(f"[S3Service Init] AWS_REGION: {self.region}")
        print(f"[S3Service Init] Dev mode: {self.dev_mode}")

        if self.dev_mode:
            # 開発モード: ローカルディレクトリに保存
            self.local_storage = Path("./storage")
            self.local_storage.mkdir(exist_ok=True)
            (self.local_storage / "licenses").mkdir(exist_ok=True)
            (self.local_storage / "originals").mkdir(exist_ok=True)
        else:
            # 本番モード: S3を使用
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_key,
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region
            )

    async def upload_image(
        self,
        image_data: bytes,
        filename: Optional[str] = None,
        content_type: str = "image/png",
        event_code: Optional[str] = None
    ) -> dict:
        """
        画像をS3またはローカルにアップロード

        Args:
            image_data: 画像のバイトデータ
            filename: ファイル名（指定しない場合は自動生成）
            content_type: MIMEタイプ
            event_code: イベントコード（指定するとイベントフォルダーに保存）

        Returns:
            dict: {key, url}
        """
        try:
            # ファイル名生成
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                if event_code:
                    filename = f"events/{event_code}/licenses/{timestamp}_{unique_id}.png"
                else:
                    filename = f"licenses/{timestamp}_{unique_id}.png"

            if self.dev_mode:
                # 開発モード: ローカルに保存
                file_path = self.local_storage / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(image_data)

                # ローカルファイルのURLを生成
                url = f"http://localhost:8000/storage/{filename}"

                return {
                    "key": filename,
                    "url": url
                }
            else:
                # 本番モード: S3にアップロード
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=image_data,
                    ContentType=content_type
                )

                # URLを生成
                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"

                return {
                    "key": filename,
                    "url": url
                }

        except Exception as e:
            raise Exception(f"画像アップロードエラー: {str(e)}")

    async def upload_original_image(
        self,
        image_data: bytes,
        filename: Optional[str] = None,
        event_code: Optional[str] = None
    ) -> dict:
        """
        オリジナル画像をS3またはローカルにアップロード

        Args:
            image_data: 画像のバイトデータ
            filename: ファイル名
            event_code: イベントコード（指定するとイベントフォルダーに保存）

        Returns:
            dict: {key, url}
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                if event_code:
                    filename = f"events/{event_code}/originals/{timestamp}_{unique_id}.jpg"
                else:
                    filename = f"originals/{timestamp}_{unique_id}.jpg"

            if self.dev_mode:
                # 開発モード: ローカルに保存
                file_path = self.local_storage / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(image_data)

                url = f"http://localhost:8000/storage/{filename}"

                return {
                    "key": filename,
                    "url": url
                }
            else:
                # 本番モード: S3にアップロード
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=image_data,
                    ContentType="image/jpeg"
                )

                url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"

                return {
                    "key": filename,
                    "url": url
                }

        except Exception as e:
            raise Exception(f"画像アップロードエラー: {str(e)}")

    async def delete_image(self, key: str) -> bool:
        """
        S3から画像を削除

        Args:
            key: S3オブジェクトキー

        Returns:
            bool: 削除成功かどうか
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError as e:
            raise Exception(f"S3削除エラー: {str(e)}")
