import requests

def test_stream():
    url = "http://localhost:18780/api/chat/stream"
    params = {
        "content": "<script>alert(1)</script>",
        "turn_id": "test_123"
    }

    try:
        response = requests.get(url, params=params, stream=True)
        print(f"Status Code: {response.status_code}")

        chunks_read = 0
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                print(chunk.decode('utf-8'))
                chunks_read += 1
                if chunks_read > 5:
                    break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_stream()
