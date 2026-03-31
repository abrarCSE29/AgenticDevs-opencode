"""
Upload project documentation files to AWS S3.

Uses an existing bucket (from AWS_S3_BUCKET env var) and creates a folder
named after the project, then uploads all .md files there.

Usage:
    python scripts/upload-docs-to-s3.py --project-name <name> --project-dir <path>

Security:
    - Validates that project_dir is within the projects/ directory
    - Only uploads .md files
    - Bucket name is read from AWS_S3_BUCKET environment variable
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print(json.dumps({"error": "boto3 is required. Install with: pip install boto3"}))
    sys.exit(1)


def validate_project_dir(project_dir: str) -> bool:
    """Assert that project_dir is within the projects/ directory."""
    resolved = os.path.realpath(project_dir)
    project_root = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "projects"))
    if not resolved.startswith(project_root):
        return False
    if not os.path.isdir(resolved):
        return False
    return True


def upload_files(s3_client, project_dir: str, bucket_name: str, project_name: str, region: str) -> dict:
    """Upload all .md files from project_dir to S3 under a project-name folder."""
    urls = {}
    project_path = Path(project_dir)

    for md_file in sorted(project_path.glob("*.md")):
        if not md_file.is_file():
            continue

        s3_key = f"{project_name}/{md_file.name}"
        try:
            s3_client.upload_file(
                str(md_file),
                bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": "text/markdown",
                    "ContentDisposition": "attachment"
                },
            )
            url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
            urls[md_file.name] = url
        except ClientError as e:
            print(json.dumps({"error": f"Failed to upload {md_file.name}: {e}"}))
            sys.exit(1)

    return urls


def main():
    parser = argparse.ArgumentParser(description="Upload project docs to AWS S3")
    parser.add_argument("--project-name", required=True, help="Project name (kebab-case)")
    parser.add_argument("--project-dir", required=True, help="Path to the project directory")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    args = parser.parse_args()

    project_dir = os.path.realpath(args.project_dir)

    if not validate_project_dir(project_dir):
        print(json.dumps({
            "error": f"Invalid project directory. Must be within projects/. Got: {args.project_dir}"
        }))
        sys.exit(1)

    md_files = list(Path(project_dir).glob("*.md"))
    if not md_files:
        print(json.dumps({"error": f"No .md files found in {project_dir}"}))
        sys.exit(1)

    from dotenv import load_dotenv
    load_dotenv()

    bucket_name = os.getenv("AWS_S3_BUCKET")
    if not bucket_name:
        print(json.dumps({"error": "AWS_S3_BUCKET environment variable not set"}))
        sys.exit(1)

    region = os.getenv("AWS_S3_REGION")
    if not region:
        region = "us-east-1"

    try:
        s3_client = boto3.client("s3", region_name=region)
    except NoCredentialsError:
        print(json.dumps({
            "error": "AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
        }))
        sys.exit(1)

    urls = upload_files(s3_client, project_dir, bucket_name, args.project_name, region)

    result = {
        "bucket": bucket_name,
        "region": region,
        "folder": args.project_name,
        "files": urls,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
