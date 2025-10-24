import io

import boto3
import boto3.session

from utils.constants import AWS_BUCKET_NAME, AWS_CONFIG
from utils.logger import logThis
from utils.messages import (
    S3_INVALID_PARAMETERS,
    S3_PRESIGNED_URL_FAILURE,
    S3_UPLOAD_FAILURE,
)

s3 = boto3.client(
    "s3",
    region_name=AWS_CONFIG["region"],
    aws_access_key_id=AWS_CONFIG["access_key_id"],
    aws_secret_access_key=AWS_CONFIG["secret_access_key"],
    config=boto3.session.Config(signature_version="s3v4"),
)


# route_aws.py(helper fuctions)


def upload_file_to_s3(file_obj, s3_key):
    try:
        # If it's already a file-like object (Flask case)
        if hasattr(file_obj, "read"):
            file_obj.seek(0)
            s3.upload_fileobj(file_obj, AWS_BUCKET_NAME, s3_key)
        # If it's bytes (FastAPI case)
        elif isinstance(file_obj, bytes):
            file_like = io.BytesIO(file_obj)
            s3.upload_fileobj(file_like, AWS_BUCKET_NAME, s3_key)

        return True
    except Exception as e:
        logThis.error(f"{S3_UPLOAD_FAILURE}:{str(e)}")
        return False


def generate_presigned_url(object_key, expiration=3600):
    """
    Generates a pre-signed URL for accessing an S3 object.
    """

    try:
        if not object_key:
            raise ValueError(S3_INVALID_PARAMETERS)
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": AWS_CONFIG["bucket_name"], "Key": object_key},
            ExpiresIn=expiration,
        )
    except Exception as e:
        logThis.error(f"{S3_PRESIGNED_URL_FAILURE}: {e}")
        return None
