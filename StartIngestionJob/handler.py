import json
import boto3
import uuid


def lambda_handler(event, context):
    # Bedrock 클라이언트 생성
    bedrock_client = boto3.client("bedrock")

    # 고유한 클라이언트 토큰 생성 (동일한 요청의 중복 실행 방지)
    client_token = str(uuid.uuid4())

    # 동기화 작업 시작
    try:
        response = bedrock_client.start_ingestion_job(
            clientToken=client_token,
            dataSourceId="EDFROV6GDY",
            description="knowledge-base-quick-start-ex6y2-data-source 데이터 소스 동기화",
            knowledgeBaseId="BMOJGLFWJF",
        )

        # 성공 응답 반환
        return {"statusCode": 200, "body": json.dumps(response)}
    except bedrock_client.exceptions.ThrottlingException:
        return {"statusCode": 429, "body": "Request was throttled."}
    except bedrock_client.exceptions.AccessDeniedException:
        return {"statusCode": 403, "body": "Access denied."}
    except bedrock_client.exceptions.ValidationException:
        return {"statusCode": 400, "body": "Validation error."}
    except bedrock_client.exceptions.InternalServerException:
        return {"statusCode": 500, "body": "Internal server error."}
    except bedrock_client.exceptions.ResourceNotFoundException:
        return {"statusCode": 404, "body": "Resource not found."}
    except bedrock_client.exceptions.ConflictException:
        return {"statusCode": 409, "body": "Conflict."}
    except bedrock_client.exceptions.ServiceQuotaExceededException:
        return {"statusCode": 503, "body": "Service quota exceeded."}
