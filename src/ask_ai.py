import requests
import json

def ask_medical_ai(question, model_name="llama2:7b"):
    payload = {
        "model": model_name,
        "prompt": question, 
        "stream": False,
        "options": {
            "temperature": 0.1 
        }
    }

    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            return f"Error: HTTP {response.status_code}"
    except requests.ConnectionError:
        return "Cannot connect to Ollama"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    question = "What is pneumonia? Give a brief definition."
    answer = ask_medical_ai(question)
    print(f"Question: {question}")
    print(f"AI Answer: {answer}")
