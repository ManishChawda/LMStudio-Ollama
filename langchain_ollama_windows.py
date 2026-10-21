from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3",
    base_url="http://172.16.2.53:11434"
)

response = llm.invoke("What is Active Directory?")

print(response.content)