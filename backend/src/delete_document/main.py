import os
import json
import boto3
from aws_lambda_powertools import Logger

DOCUMENT_TABLE = os.environ["DOCUMENT_TABLE"]
MEMORY_TABLE = os.environ["MEMORY_TABLE"]

ddb = boto3.resource("dynamodb")
document_table = ddb.Table(DOCUMENT_TABLE)
memory_table = ddb.Table(MEMORY_TABLE)
s3 = boto3.client('s3')

logger = Logger()

@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    document_id = event["pathParameters"]["documentid"]

    try:
        # Delete the document item from the DynamoDB table
        response = document_table.delete_item(
            Key={"userid": user_id, "documentid": document_id},
            ConditionExpression="attribute_exists(documentid)"
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
            },
            "body": json.dumps({"message": "Document deleted successfully"}),
        }
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
            },
            "body": json.dumps({"message": "Failed to delete document", "error": str(e)}),
        }
