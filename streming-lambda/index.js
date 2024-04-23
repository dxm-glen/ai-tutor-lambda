import { Writable } from "stream";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { AmazonKnowledgeBaseRetriever } from "@langchain/community/retrievers/amazon_knowledge_base";
import {
  BedrockRuntimeClient,
  InvokeModelWithResponseStreamCommand,
} from "@aws-sdk/client-bedrock-runtime";

const modelId = "anthropic.claude-3-sonnet-20240229-v1:0";
const bedrockRuntime = new BedrockRuntimeClient({ region: "us-east-1" });
const retriever = new AmazonKnowledgeBaseRetriever({
  topK: 5, // in python, retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 5}}
  knowledgeBaseId: "XPMNH9ZTJI",
  region: "us-east-1",
});

import { BedrockChat } from "@langchain/community/chat_models/bedrock";

const model = new BedrockChat({
  model: modelId,
  region: "us-east-1",
  streaming: true,
  modelKwargs: {
    anthropic_version: "bedrock-2023-05-31",
  },
  temperature: 0.01,
});

const invokeModelWithResponseStream = async (
  prompt,
  responseStream,
  purpose = "PRODUCTION"
) => {
  const body = {
    anthropic_version: "bedrock-2023-05-31",
    max_tokens: 1000,
    messages: [
      {
        role: "user",
        content: [{ type: "text", text: prompt }],
      },
    ],
  };

  // Stream Response 호출을 위한 명령어 생성
  const command = new InvokeModelWithResponseStreamCommand({
    contentType: "application/json",
    body: JSON.stringify(body),
    modelId: modelId,
  });
  // 명령어 전송을 통해 FM 호출
  const apiResponse = await bedrockRuntime.send(command);

  let completeMessage = "";
  // Decode and process the response stream
  for await (const item of apiResponse.body) {
    const chunk = JSON.parse(new TextDecoder().decode(item.chunk.bytes));
    const chunk_type = chunk.type;

    if (chunk_type === "content_block_delta") {
      const text = chunk.delta.text;
      completeMessage = completeMessage + text;
      responseStream.write(text);
      if (purpose === "PRODUCTION") console.log(text);
    }
  }

  // Return the final response
  return completeMessage;
};

const Test_SimpleStreaming = async () => {
  const promptTemplate = ChatPromptTemplate.fromMessages([
    [
      "system",
      "Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.\n\nContext: {context}",
    ],
    ["human", "{question}"],
  ]);
  console.log(promptTemplate);

  const outStream = new Writable({
    write(chunk, encodeing, callback) {
      process.stdout.write(chunk.toString());
      callback();
    },
  });

  const prompt = "대한민국의 수도에 대해 설명해";
  await invokeModelWithResponseStream(prompt, outStream, "TEST");
};

const Test_RagStreaming = async () => {
  const prompt = "대한민국의 수도에 대해 설명해";

  const outStream = new Writable({
    write(chunk, encodeing, callback) {
      process.stdout.write(chunk.toString());
      callback();
    },
  });

  const docs = await retriever.getRelevantDocuments(prompt);
  console.log(docs[0]);
  const context = docs.map((doc) => doc.pageContent).join("\n\n");

  const promptTemplate = ChatPromptTemplate.fromMessages([
    [
      "system",
      "Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.\n\nContext: {context}",
    ],
    ["human", "{prompt}"],
  ]);
  const formattedChatPrompt = await promptTemplate.invoke({ context, prompt });
  console.log(formattedChatPrompt);

  const stream = await model.stream(formattedChatPrompt);
  console.log(stream);
  for await (const chunk of stream) {
    outStream.write(chunk.content);
  }
};

// await Test_SimpleStreaming();
// await Test_RagStreaming();
// process.exit(1);

export const handler = awslambda.streamifyResponse(
  async (event, responseStream, context) => {
    console.log(`event: ${JSON.stringify(event)}`);

    const { method, path } = event.requestContext.http;
    if (method !== "POST" || path !== "/") responseStream.end();

    const body = JSON.parse(event.body);
    const prompt = body.prompt;
    console.log(">>>>>>>>>>>> prompt: ", prompt);

    const docs = await retriever.getRelevantDocuments(prompt);
    console.log(docs[0]);
    const modelContext = docs.map((doc) => doc.pageContent).join("\n\n");

    const promptTemplate = ChatPromptTemplate.fromMessages([
      [
        "system",
        "Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.\n\nContext: {context}",
      ],
      ["human", "{prompt}"],
    ]);
    const formattedChatPrompt = await promptTemplate.invoke({
      context: modelContext,
      prompt,
    });
    console.log(formattedChatPrompt);

    const stream = await model.stream(formattedChatPrompt);
    for await (const chunk of stream) {
      responseStream.write(chunk.content)
      console.log(chunk.content);
      
      const metadata = chunk.response_metadata;
      if (metadata['amazon-bedrock-invocationMetrics'] !== undefined) {
        const { inputTokenCount, outputTokenCount } = metadata['amazon-bedrock-invocationMetrics'];
        const intputPrice = inputTokenCount / 1000 * 0.003;
        const outputPrice = outputTokenCount / 1000 * 0.015;

        const metrics = [
          '\n',
          `total: ${intputPrice + outputPrice} USD`,
          `input: ${intputPrice} USD (${inputTokenCount} tokens)`,
          `output: ${outputPrice} USD (${outputTokenCount} tokens)`,
          ].join('\n')
          
        responseStream.write(metrics)
        console.log(metrics);
        
      }
    }
    responseStream.end();
  }
);