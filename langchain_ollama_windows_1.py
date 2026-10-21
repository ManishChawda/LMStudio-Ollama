from langchain_ollama import ChatOllama

#model_name="llama3"
model_name="gemma"

llm = ChatOllama(
    model=model_name,
    base_url="http://172.16.2.53:11434"
)

response = llm.invoke("What is Active Directory?")

print(response.content)