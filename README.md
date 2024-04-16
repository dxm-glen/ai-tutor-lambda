# ai-tutor-lambda

# 1. 레이어용 ZIP 파일 준비

1. 배포할 람다 함수 경로로 이동 : bedrock-chat 또는 bedrock-quiz
2. `layer` 디렉토리를 생성하고, 그 안에 `python` 디렉토리를 만듭니다.
3. 필요한 의존성을 `layer/python` 디렉토리 안에 설치합니다.
   `pip install -t ./layer/python/ langchain_community langchain`
4. `layer` 디렉토리 내에서 ZIP 파일을 생성합니다.
5. cd layer
6. zip -r ../bedrock-chat/layer.zip .
   퀴즈의 경우 zip -r ../bedrock-quiz/layer.zip .

# 2. 람다 함수 배포

1. sls deploy로 배포
2. 람다에 권한 설정 : bedrock 권한 설정

# chat 테스트

### 테스트

`{   "body": {"user_message": "과제제출에 대해서 알려주세요"} }`

### 응답 예시

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"response\": {\"content\": \"본 대학교에서 수업을 위해 제출되는 과제나 리포트는 교과목 성격에 따라 다음과 같이 나누어집니다.\\n\\n1. 콘텐츠 강의 내에서 제출하는 과제:\\n- 주관식 과제, 객관식 과제, 공개첨삭게시판 등\\n- 해당 강의가 오픈되는 기간 동안만 제출 가능\\n\\n2. 강의실의 과제방에 직접 제출하는 과제: \\n- 교수님이 직접 출제하는 리포트 과제, 음성과제, 팀프로젝트 등\\n- 교수님이 지정한 기간 동안 제출\\n- 컴퓨터로 과제를 작성한 후, 해당 교과목의 과제방 메뉴로 들어가 제출\\n\\n제출된 리포트는 교수님께서 제출한 학생 순서대로 확인하며, 학생은 각 개인의 해당 과목 강의실 > 과제방에서 제출 여부를 직접 확인할 수 있습니다. 과제 및 리포트 미제출 시에는 담당 교과목 튜터에게 문의하시면 됩니다.\", \"response_metadata\": {\"model_id\": \"anthropic.claude-3-sonnet-20240229-v1:0\", \"usage\": {\"prompt_tokens\": 2760, \"completion_tokens\": 398, \"total_tokens\": 3158}}, \"id\": \"run-85646c23-5273-4f2c-8a69-fbd258e15255-0\"}}"
}
```

# 퀴즈 테스트

# 테스트1

`{   "body": {"topic": "wine"} }`

### 응답 예시1

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"response\": {\"questions\": [{\"question\": \"샤르도네 품종은 어느 지역에서 가장 대표적으로 재배되나요?\", \"answers\": [{\"answer\": \"보르도\", \"correct\": false}, {\"answer\": \"부르고뉴\", \"correct\": true}, {\"answer\": \"리오하\", \"correct\": false}, {\"answer\": \"토스카나\", \"correct\": false}]}, {\"question\": \"소비뇽 블랑 품종의 가장 특징적인 향은 무엇인가요?\", \"answers\": [{\"answer\": \"레몬\", \"correct\": false}, {\"answer\": \"자몽\", \"correct\": false}, {\"answer\": \"잔디\", \"correct\": true}, {\"answer\": \"망고\", \"correct\": false}]}, {\"question\": \"게부르츠트라미너 품종은 어떤 기후에서 잘 자라나요?\", \"answers\": [{\"answer\": \"온화한 기후\", \"correct\": false}, {\"answer\": \"서늘한 기후\", \"correct\": true}, {\"answer\": \"열대 기후\", \"correct\": false}, {\"answer\": \"지중해성 기후\", \"correct\": false}]}, {\"question\": \"보르도 지역의 고급 디저트 와인 소테른은 주로 어떤 품종으로 만들어지나요?\", \"answers\": [{\"answer\": \"리즐링\", \"correct\": false}, {\"answer\": \"세미옹\", \"correct\": true}, {\"answer\": \"샤르도네\", \"correct\": false}, {\"answer\": \"까베르네 소비뇽\", \"correct\": false}]}, {\"question\": \"샤르도네 와인의 향에는 어떤 과일 향이 나지 않나요?\", \"answers\": [{\"answer\": \"레몬\", \"correct\": false}, {\"answer\": \"라임\", \"correct\": false}, {\"answer\": \"사과\", \"correct\": false}, {\"answer\": \"파인애플\", \"correct\": true}]}]}}"
}
```

### 테스트2

`{   "body": {"topic": "미래반도체"} }`

응답 예시2

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json"
  },
  "body": "{\"response\": {\"questions\": [{\"question\": \"IRDS(International Roadmap for Devices and Systems)는 무엇에 대한 로드맵인가?\", \"answers\": [{\"answer\": \"반도체 공정 기술 패러다임\", \"correct\": true}, {\"answer\": \"반도체 제품 마케팅 전략\", \"correct\": false}, {\"answer\": \"반도체 기업 경영 방침\", \"correct\": false}, {\"answer\": \"반도체 인력 양성 계획\", \"correct\": false}]}, {\"question\": \"HIR(Heterogeneous Integration Roadmap)은 무엇에 대한 로드맵인가?\", \"answers\": [{\"answer\": \"반도체 전공정 기술\", \"correct\": false}, {\"answer\": \"반도체 패키징 방법\", \"correct\": true}, {\"answer\": \"반도체 설계 기술\", \"correct\": false}, {\"answer\": \"반도체 제조 장비\", \"correct\": false}]}, {\"question\": \"미래 반도체 핵심 아키텍처로 다루어지지 않는 것은?\", \"answers\": [{\"answer\": \"AI\", \"correct\": false}, {\"answer\": \"양자컴퓨팅\", \"correct\": false}, {\"answer\": \"병렬-직렬 연계\", \"correct\": false}, {\"answer\": \"반도체 소재 개발\", \"correct\": true}]}, {\"question\": \"미래 반도체 엔지니어링 아키텍처의 목표 중 하나가 아닌 것은?\", \"answers\": [{\"answer\": \"연산 속도 향상\", \"correct\": false}, {\"answer\": \"다양한 기능 통합\", \"correct\": false}, {\"answer\": \"전력 소모 최소화\", \"correct\": true}, {\"answer\": \"전자-광-방열 연계\", \"correct\": false}]}, {\"question\": \"강의에서 다루지 않는 내용은?\", \"answers\": [{\"answer\": \"양자정보처리\", \"correct\": false}, {\"answer\": \"고성능컴퓨팅/데이터센터\", \"correct\": false}, {\"answer\": \"집적광학\", \"correct\": false}, {\"answer\": \"반도체 마케팅 전략\", \"correct\": true}]}]}}"
}
```
