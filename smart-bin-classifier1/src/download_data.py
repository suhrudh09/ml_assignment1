import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os
from concurrent.futures import ThreadPoolExecutor

BUCKET_NAME = "aft-vbi-pds"
IMG_PREFIX = "bin-images/"
META_PREFIX = "metadata/"
SAVE_DIR_IMG = "data/bin-images"
SAVE_DIR_META = "data/metadata"

def download_pair(filename):
    """Downloads a single image and its JSON metadata."""
    s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED), region_name="us-east-1")
    try:
        # Download Image
        s3.download_file(BUCKET_NAME, f"{IMG_PREFIX}{filename}", f"{SAVE_DIR_IMG}/{filename}")
        
        # Download Metadata
        json_filename = filename.replace(".jpg", ".json")
        s3.download_file(BUCKET_NAME, f"{META_PREFIX}{json_filename}", f"{SAVE_DIR_META}/{json_filename}")
        return True
    except Exception:
        return False

def main():
    os.makedirs(SAVE_DIR_IMG, exist_ok=True)
    os.makedirs(SAVE_DIR_META, exist_ok=True)
    
    # 1. Fetch file list
    s3_list = boto3.client("s3", config=Config(signature_version=UNSIGNED), region_name="us-east-1")
    print("Fetching file list from AWS...")
    response = s3_list.list_objects_v2(Bucket=BUCKET_NAME, Prefix=IMG_PREFIX, MaxKeys=1200)
    
    keys_to_download = []
    for obj in response.get("Contents", []):
        key = obj["Key"]
        filename = key.split("/")[-1]
        if filename.endswith(".jpg"):
            keys_to_download.append(filename)
        if len(keys_to_download) >= 1000:
            break
            
    # 2. Parallel Download
    print(f"Starting download of {len(keys_to_download)} items...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(download_pair, keys_to_download))
        
    print(f"✅ Download complete. {sum(results)} pairs saved to 'data/'.")

if __name__ == "__main__":
    main()
