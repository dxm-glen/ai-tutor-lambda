# handler.py
import json
import os
import boto3

from langchain_community.chat_models import BedrockChat
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser


class JsonOutputParser(BaseOutputParser):
    def parse(self, text):
        # 텍스트 양끝에 정리하고 json으로 변경해서 python 코드에 쓸 수 있도록 변경
        text = text.replace("```", "").replace("json", "")
        return json.loads(text)


output_parser = JsonOutputParser()


def serialize_response(response):
    return {
        "content": response.content,
        "response_metadata": response.response_metadata,
        "id": response.id,
    }


def bedrock_quiz_handler(event, context):
    # AWS 세션을 설정
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name="us-east-1",
    )

    bedrock_client = session.client("bedrock-runtime", "us-east-1")

    bedrock_chat = BedrockChat(
        client=bedrock_client,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        model_kwargs={
            "temperature": 0.1,
        },
    )

    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="XPMNH9ZTJI",
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

    # event에서 퀴즈 만들 주제에 대해서 추출
    body = json.loads(event["body"])
    topic = body["topic"]

    # 유저 메시지에 대해 검색
    docs = retriever.get_relevant_documents(query=topic)
    docs_content = "\n\n".join(document.page_content for document in docs)

    print("topic 관련 뽑아온 것")
    print(docs_content)

    def format_docs(docs_content):
        return "\n\n".join(document.page_content for document in docs_content)

    questions_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
        You are a helpful assistant that is role playing as a teacher.
            
        Based ONLY on the following context make 5 questions to test the user's knowledge about the text.
        
        Each question should have 4 answers, three of them must be incorrect and one should be correct.
            
        Use (o) to signal the correct answer.

        if context language is Korean, you MUST make it by Korean.
        
            
        Question examples:
            
        Question: What is the color of the ocean?
        Answers: Red|Yellow|Green|Blue(o)
            
        Question: What is the capital or Georgia?
        Answers: Baku|Tbilisi(o)|Manila|Beirut
            
        Question: When was Avatar released?
        Answers: 2007|2001|2009(o)|1998
            
        Question: Who was Julius Caesar?
        Answers: A Roman Emperor(o)|Painter|Actor|Model
            
        Your turn!
            
        Context: {context}
    """,
            )
        ]
    )

    questions_chain = {"context": format_docs} | questions_prompt | bedrock_chat

    formatting_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
        You are a powerful formatting algorithm.
        
        You format exam questions into JSON format.
        Answers with (o) are the correct ones.
        
        Example Input:
        Question: What is the color of the ocean?
        Answers: Red|Yellow|Green|Blue(o)
            
        Question: What is the capital or Georgia?
        Answers: Baku|Tbilisi(o)|Manila|Beirut
            
        Question: When was Avatar released?
        Answers: 2007|2001|2009(o)|1998
            
        Question: Who was Julius Caesar?
        Answers: A Roman Emperor(o)|Painter|Actor|Model
        
        
        Example Output:
        
        ```json
        {{ "questions": [
                {{
                    "question": "What is the color of the ocean?",
                    "answers": [
                            {{
                                "answer": "Red",
                                "correct": false
                            }},
                            {{
                                "answer": "Yellow",
                                "correct": false
                            }},
                            {{
                                "answer": "Green",
                                "correct": false
                            }},
                            {{
                                "answer": "Blue",
                                "correct": true
                            }},
                    ]
                }},
                            {{
                    "question": "What is the capital or Georgia?",
                    "answers": [
                            {{
                                "answer": "Baku",
                                "correct": false
                            }},
                            {{
                                "answer": "Tbilisi",
                                "correct": true
                            }},
                            {{
                                "answer": "Manila",
                                "correct": false
                            }},
                            {{
                                "answer": "Beirut",
                                "correct": false
                            }},
                    ]
                }},
                            {{
                    "question": "When was Avatar released?",
                    "answers": [
                            {{
                                "answer": "2007",
                                "correct": false
                            }},
                            {{
                                "answer": "2001",
                                "correct": false
                            }},
                            {{
                                "answer": "2009",
                                "correct": true
                            }},
                            {{
                                "answer": "1998",
                                "correct": false
                            }},
                    ]
                }},
                {{
                    "question": "Who was Julius Caesar?",
                    "answers": [
                            {{
                                "answer": "A Roman Emperor",
                                "correct": true
                            }},
                            {{
                                "answer": "Painter",
                                "correct": false
                            }},
                            {{
                                "answer": "Actor",
                                "correct": false
                            }},
                            {{
                                "answer": "Model",
                                "correct": false
                            }},
                    ]
                }}
            ]
        }}
        ```
        Your turn!
        Questions: {context}
    """,
            )
        ]
    )

    formatting_chain = formatting_prompt | bedrock_chat
    print("포맷팅한 퀴즈")
    print(type(formatting_chain))
    print(formatting_chain)
    # response_data = serialize_response(formatting_chain)

    def run_quiz_chain(docs_content):
        chain = {"context": questions_chain} | formatting_chain | output_parser
        print(chain)
        return chain.invoke(docs_content)

    response_data = run_quiz_chain(docs_content)
    # 답변을 리턴하는 부분
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": response_data}, ensure_ascii=False),
    }
