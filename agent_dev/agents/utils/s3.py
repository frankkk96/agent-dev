import uuid
import boto3
import base64


class S3:
    def __init__(self, bucket: str, endpoint_url: str, access_key: str, secret_key: str, region: str, public_endpoint: str):
        self.bucket = bucket
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.public_endpoint = public_endpoint


def b64_to_s3(b64: str, s3: S3) -> str:
    file_name = f"{uuid.uuid4()}.png"

    # 解码 base64
    img_bytes = base64.b64decode(b64)

    # S3 客户端
    s3 = boto3.client(
        "s3",
        endpoint_url=s3.endpoint_url,
        aws_access_key_id=s3.access_key,
        aws_secret_access_key=s3.secret_key,
        region_name=s3.region,
    )

    key = f"results/{file_name}"
    s3.put_object(Bucket=s3.bucket, Key=key, Body=img_bytes,
                  ContentType="image/png")

    # 返回 S3 访问地址
    return f"{s3.public_endpoint}/results/{file_name}"
