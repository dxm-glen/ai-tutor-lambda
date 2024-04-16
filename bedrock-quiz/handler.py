import json
import os
import boto3

from langchain_community.chat_models import BedrockChat
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseOutputParser


class JsonOutputParser(BaseOutputParser):
    def parse(self, text):
        cleaned_text = text.replace("```json", "").replace("```", "")
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            print("JSON 파싱 오류:", e)
            raise


output_parser = JsonOutputParser()


def bedrock_quiz_handler(event, context):
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

    body = event["body"]
    topic = json.loads(body)["body"]["topic"]
    docs = retriever.get_relevant_documents(query=topic)
    docs_content = "\n\n".join(document.page_content for document in docs)
    print("topic 관련 뽑아온 것")
    print(docs_content)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
    You are a helpful assistant that is role playing as a teacher.
         
    Based ONLY on the following context make 5 questions about {topic} to test the user's knowledge about the text.
    
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
            ),
            ("human", "topic is {topic}"),
        ]
    ).format_messages(context=docs_content, topic=topic)

    quiz = bedrock_chat.invoke(prompt)
    print(type(quiz))
    print(quiz)

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
    
    DONT MAKE "Expecting ',' " ERROR
    Your turn!
    Questions: {context}
""",
            ),
            ("human", "format exam questions into JSON format"),
        ]
    ).format_messages(context=quiz)
    formated_quiz = bedrock_chat.invoke(formatting_prompt)
    print("내용 뭐냐")
    print(formated_quiz.content)
    parsed_quiz = output_parser.parse(formated_quiz.content)
    print("포맷팅한 퀴즈")
    print(type(parsed_quiz))
    print(parsed_quiz)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": parsed_quiz}, ensure_ascii=False),
    }
