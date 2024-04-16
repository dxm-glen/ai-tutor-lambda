# handler.py
import json
import os
import boto3

from langchain_community.chat_models import BedrockChat
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.prompts import ChatPromptTemplate

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


def serialize_response(response):
    return {
        "content": response.content,
        "response_metadata": response.response_metadata,
        "id": response.id,
    }


def bedrock_chat_handler(event, context):
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name="us-east-1",
    )

    bedrock_client = session.client("bedrock-runtime", "us-east-1")

    bedrock_chat = BedrockChat(
        client=bedrock_client,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        #
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
        #
        model_kwargs={
            "temperature": 0.1,
        },
    )

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="XPMNH9ZTJI",
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

    body = event["body"]
    user_message = json.loads(body)["body"]["user_message"]

    print(user_message)

    docs = retriever.get_relevant_documents(query=user_message)
    docs_content = "\n\n".join(document.page_content for document in docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.\n\nContext: {context}",
            ),
            ("human", "{question}"),
        ]
    ).format_messages(context=docs_content, question=user_message)

    response = bedrock_chat.invoke(prompt)
    print(type(response))
    print(response)
    response_data = serialize_response(response)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": response_data}, ensure_ascii=False),
    }
