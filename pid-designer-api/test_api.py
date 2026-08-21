import requests

url = "http://127.0.0.1:8000/simulate"

payload = {
    "R5": "10k",
    "R6": "10k",
    "R7": "10k",
    "R10": "10k",
    "C1": "100n",
    "C2": "100n",
    "Gnum": [50],
    "Gden": [1, 4, 0],
    "Hnum": [1],
    "Hden": [1],
    "P_enabled": True,
    "I_enabled": True,
    "D_enabled": True,
    "mode": 0
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.json())
