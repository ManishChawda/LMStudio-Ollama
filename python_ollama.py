from ollama import chat

response = chat(
    model="llama3",
    messages=[
        {
            "role": "user",
            "content": "What is Active Directory?"
        }
    ]
)

print(response["message"]["content"])