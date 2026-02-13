"""测试 ModelClient."""
from src.model_client import ModelClient

if __name__ == "__main__":
    client = ModelClient()

    messages = [{"role": "user", "content": "你好，请介绍一下自己"}]

    print("=== 测试 think ===")
    content = client.think(messages)
    print(content)

    print("\n=== 测试 think_stream ===")
    content = client.think_stream(messages)
    print(content)
