from openai import OpenAI

client = OpenAI(
    base_url="http://172.16.2.53:1234/v1",
    api_key="lm-studio"
)

response = client.chat.completions.create(
    model="ministral-3-3b-instruct-2512:3",
    messages=[
        {
            "role": "user",
            "content": "What is LangChain?"
        }
    ]
)

print(response.choices[0].message.content)
