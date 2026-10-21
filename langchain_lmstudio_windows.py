from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://172.16.2.53:1234/v1",
    api_key="lm-studio",
    model="ministral-3-3b-instruct-2512:3",
)

response = llm.invoke("Explain LangChain in simple words.")

print(response.content)
