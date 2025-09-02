import requests

try:
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        print("Ollama is running")
        models = response.json()
        print(f"Available models: {[m['name'] for m in models['models']]}")
    else:
        print("Ollama responded with an error")
except:
    print("Cannot connect to Ollama. make sure 'ollama serve' is running")


