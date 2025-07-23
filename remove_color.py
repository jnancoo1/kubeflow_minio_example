import os
import io
import boto3
from PIL import Image

# MinIO config
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "host.docker.internal:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "mlpipeline")
INPUT_PREFIX = os.environ.get("INPUT_PREFIX", "my-input-images/")
OUTPUT_PREFIX = os.environ.get("OUTPUT_PREFIX", "output-images/")

def connect_minio():
    return boto3.client(
        's3',
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )

def list_images(s3):
    response = s3.list_objects_v2(Bucket=MINIO_BUCKET, Prefix=INPUT_PREFIX)
    images = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].lower().endswith(('.jpg', '.jpeg'))]
    print(f"Found {len(images)} images in {MINIO_BUCKET}/{INPUT_PREFIX}")
    return images

def download_image(s3, key):
    response = s3.get_object(Bucket=MINIO_BUCKET, Key=key)
    return Image.open(io.BytesIO(response['Body'].read()))

def upload_image(s3, key, image):
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG')
    buffer.seek(0)
    s3.put_object(Bucket=MINIO_BUCKET, Key=key, Body=buffer, ContentType='image/jpeg')

def process_images():
    s3 = connect_minio()
    images = list_images(s3)
    processed = 0

    for key in images:
        try:
            print(f"Processing {key}")
            img = download_image(s3, key)
            grayscale_img = img.convert("L")

            basename = os.path.basename(key)
            name, ext = os.path.splitext(basename)
            output_key = f"{OUTPUT_PREFIX}{name}_grayscale{ext}"

            upload_image(s3, output_key, grayscale_img)
            print(f"Uploaded: {output_key}")
            processed += 1
        except Exception as e:
            print(f"Error processing {key}: {e}")

    print(f"Successfully processed {processed}/{len(images)} images")

if __name__ == "__main__":
    process_images()
