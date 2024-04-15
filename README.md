# ai-tutor-lambda


# 레이어용 ZIP 파일 준비

1. `layer` 디렉토리를 생성하고, 그 안에 `python` 디렉토리를 만듭니다.
2. 필요한 의존성을 `layer/python` 디렉토리 안에 설치합니다.
   예: `pip install -t layer/python/ langchain_community langchain`
3. `layer` 디렉토리 내에서 ZIP 파일을 생성합니다.
4. cd layer
5. zip -r ../layer.zip .
6. 람다에 권한 설정 : bedrock
