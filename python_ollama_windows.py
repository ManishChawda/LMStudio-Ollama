from ollama import Client

client = Client(
    host="http://172.16.2.53:11434"
)

response = client.chat(
    model="llama3",
    messages=[
        {
            "role": "user",
            "content": "What is Active Directory?"
        }
    ]
)

print(response["message"]["content"])
