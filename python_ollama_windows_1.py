from ollama import Client

client = Client(
    host="http://172.16.2.53:11434"
)

#model_name = "llama3"
model_name = "gemma"

response = client.chat(
    model=model_name,
    messages=[
        {
            "role": "user",
            "content": "What is Active Directory?"
        }
    ]
)

print(response["message"]["content"])
