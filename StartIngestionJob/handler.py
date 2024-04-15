import json
import requests
from requests_aws4auth import AWS4Auth
import boto3
import uuid


def lambda_handler(event, context):
    knowledgeBaseId = event["knowledgeBaseId"]
    dataSourceId = event["dataSourceId"]

    region = "us-east-1"
    host = "bedrock-agent.us-east-1.amazonaws.com"
    path = (
        f"/knowledgebases/{knowledgeBaseId}/datasources/{dataSourceId}/ingestionjobs/"
    )
    endpoint = f"https://{host}{path}"

    service = "bedrock"
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token,
    )

    client_token = str(uuid.uuid4()).replace("-", "")

    payload = {"clientToken": client_token, "description": "Ingestion job description"}

    response = requests.put(
        endpoint,
        auth=awsauth,
        json=payload,
        headers={"Content-type": "application/json"},
    )

    return {"statusCode": response.status_code, "body": response.text}
