import ollama

# Chat với Qwen3-8B
response = ollama.chat(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": "Bạn là một Robot thú cưng trông nhà."},
        {"role": "user", "content": "bạn bao nhiêu tuổi."}
    ],
    think=False
)

print(response['message']['content'])
