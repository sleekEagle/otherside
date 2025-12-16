from llama_cpp import Llama

llm = Llama(
    model_path=r"C:\Users\lahir\llama\models\Qwen2.5-7B-Instruct-Q4_K_M.gguf",
    n_ctx=8192,
    n_gpu_layers=-1,   # use GPU fully
    temperature=0.2,
    chat_format="chatml"
)

response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "can you summerize the content of a youtube video? I can give you the transcript."}
    ],
    temperature=0.2,
    max_tokens=50
)

print("Response:", response["choices"][0]["message"]["content"])

pass
