from ollama import chat

print("Type 'exit' to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    response = chat(
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
