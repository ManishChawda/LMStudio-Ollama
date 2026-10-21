from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3"
)

print("Type exit to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    response = llm.invoke(question)

    print("\nAI :", response.content)
    print()
