"""测试 ModelClient."""
from src.model_client import ModelClient

if __name__ == "__main__":
    client = ModelClient()

    messages = [{"role": "user", "content": "你好，请介绍一下自己"}]

    print("=== 测试 think (非流式) ===")
    content = client.think(messages)
    print(content)

    print("\n=== 测试 think (stream=True 流式) ===")
    content = client.think(messages, stream=True)
    print(content)
