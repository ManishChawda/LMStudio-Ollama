from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3"
)

response = llm.invoke("What is Active Directory?")

print(response.content)
