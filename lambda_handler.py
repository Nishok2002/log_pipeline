import os
import logging
from io import BytesIO
import boto3
from processor import validate_and_transform
from storage import write_parquet_buffer, errors_to_jsonl_str

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CLEAN_BUCKET = os.getenv("CLEAN_BUCKET", "clean-logs")
ERROR_BUCKET = os.getenv("ERROR_BUCKET", "error-logs")

def lambda_handler(event, context=None):
    """
    AWS Lambda-style handler.
    Reads the S3 object in the event, validates + transforms logs,
    writes clean logs to CLEAN_BUCKET, invalid logs to ERROR_BUCKET.
    """
    s3 = boto3.client("s3", region_name="us-east-1")
    valid, errors = [], []
    last_key = None

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        last_key = key

        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
        for line in body.splitlines():
            if not line.strip():
                continue
            log, err = validate_and_transform(line)
            if err:
                errors.append({"raw": line, "error": err, "source_key": key})
            else:
                valid.append(log)

    if last_key is None:
        logger.warning("No S3 records to process.")
        return {"processed": 0, "valid": 0, "errors": 0}

    base_name = os.path.splitext(os.path.basename(last_key))[0]

    if valid:
        buf = BytesIO()
        write_parquet_buffer(valid, buf)
        buf.seek(0)
        s3.put_object(Bucket=CLEAN_BUCKET, Key=f"clean/{base_name}.parquet", Body=buf.read())

    if errors:
        s3.put_object(Bucket=ERROR_BUCKET, Key=f"errors/{base_name}.jsonl",
                      Body=errors_to_jsonl_str(errors).encode("utf-8"))

    logger.info(f"Processed={len(valid)+len(errors)} Valid={len(valid)} Errors={len(errors)}")
    return {"processed": len(valid) + len(errors), "valid": len(valid), "errors": len(errors)}
