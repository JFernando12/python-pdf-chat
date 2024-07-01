import os, json
import boto3
from boto3.dynamodb.conditions import Key
from aws_lambda_powertools import Logger

DOCUMENT_TABLE = os.environ["DOCUMENT_TABLE"]
MEMORY_TABLE = os.environ["MEMORY_TABLE"]
BUCKET = os.environ["BUCKET"]

ddb = boto3.resource("dynamodb")
document_table = ddb.Table(DOCUMENT_TABLE)
memory_table = ddb.Table(MEMORY_TABLE)
s3 = boto3.client('s3')

logger = Logger()

@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    document_id = event["pathParameters"]["documentid"]
    conversation_id = event["pathParameters"]["conversationid"]

    response = document_table.get_item(
        Key={"userid": user_id, "documentid": document_id}
    )

    document = response["Item"]
    document["conversations"] = sorted(
        document["conversations"], key=lambda conv: conv["created"], reverse=True
    )
    logger.info({"document": document})

    response = memory_table.get_item(Key={"SessionId": conversation_id})
    messages = response["Item"]["History"]
    logger.info({"messages": messages})

    filename = document["filename"]
    object_name = f"{user_id}/{filename}/{filename}"
    logger.info({"object_name": object_name})
    logger.info({"BUCKET": BUCKET})
    url = s3.generate_presigned_url(
        'get_object', 
        Params={'Bucket': BUCKET, 'Key': object_name},
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
        },
        "body": json.dumps(
            {
                "conversationid": conversation_id,
                "document": document,
                "messages": messages,
                "url": url,
            },
            default=str,
        ),
    }
