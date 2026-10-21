from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3",
    base_url="http://172.16.2.53:11434"
    )

print("Type exit to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    response = llm.invoke(question)

    print("\nAI :", response.content)
    print()
