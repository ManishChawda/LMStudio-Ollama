from ollama import Client

client = Client(
    host="http://172.16.2.53:11434"
)

print("Type 'exit' to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    response = client.chat(
        model="llama3",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    print("\nAI :", response["message"]["content"])
    print()