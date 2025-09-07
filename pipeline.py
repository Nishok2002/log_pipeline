import os
from moto import mock_aws
import boto3
from lambda_handler import lambda_handler

# ⚠️ Change first timestamp to today's date (UTC) if you want the API to count it
SAMPLE_LOGS = (
    '{"timestamp":"2025-09-07T10:01:15Z","user_id":"U1","action":"login"}\n'
    '{"timestamp":"invalid","user_id":"U2","action":"logout"}\n'
    '{"user_id":"U3","action":"login"}\n'
)

@mock_aws
def main():
    os.environ["CLEAN_BUCKET"] = "clean-logs"
    os.environ["ERROR_BUCKET"] = "error-logs"

    s3 = boto3.client("s3", region_name="us-east-1")
    for b in ("input-logs", "clean-logs", "error-logs"):
        s3.create_bucket(Bucket=b)

    key = "logs1.jsonl"
    s3.put_object(Bucket="input-logs", Key=key, Body=SAMPLE_LOGS.encode("utf-8"))

    event = {"Records": [{"s3": {"bucket": {"name": "input-logs"}, "object": {"key": key}}}]}
    result = lambda_handler(event)
    print("Lambda result:", result)

    # Export parquet from Moto to local file for API
    obj = s3.get_object(Bucket="clean-logs", Key="clean/logs1.parquet")
    os.makedirs("data/clean", exist_ok=True)
    with open("data/clean/clean_from_moto.parquet", "wb") as f:
        f.write(obj["Body"].read())
    print("Wrote local copy: data/clean/clean_from_moto.parquet")

if __name__ == "__main__":
    main()
