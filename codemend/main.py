import requests
import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DIFY_API_KEY")
API_URL = os.getenv("DIFY_API_URL")

def extract_answer(data_string):
    # 'data: ' プレフィックスを削除
    json_string = data_string.replace('data: ', '')
    
    # JSON文字列をPythonオブジェクトに変換
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        return ""
    
    # 'answer' キーの値を取得
    answer = data.get('answer', '')
    
    return answer

def send_chat_request(program, error):
    url = API_URL
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "inputs": {
            "program": program,
            "error": error
        },
        "response_mode": "streaming",
        "user": "Master",
    }

    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                print(extract_answer(line.decode("utf-8")), end='', flush=True)

def safe_encode(input_string):
    try:
        encoded_string = input_string.encode('utf-8')
        return encoded_string
    except UnicodeEncodeError as e:
        print(f"UnicodeEncodeError: {e}")
        encoded_string = input_string.encode('utf-8', errors='ignore')
        return encoded_string

def main():
    while True:
        cmd = input("$ ")
        if cmd == "exit":
            break
        cmd = "python3 /Users/sakabekazune/prg/python/AI/CodeMendtest/a.py"
        
        cmds = cmd.split(" ")
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        stderr = process.communicate()[1]
        if stderr and cmds[0] == "python3":
            with open(cmds[1], "r") as r:
                program = r.read()
            print("=====================================")
            print("エラーが発生しました。")
            
            send_chat_request(program, stderr.strip())
            # for chunk in send_chat_request(program, stderr.strip()):
            #     if 'answer' in chunk:
            #         response_text = safe_encode(chunk['answer'])
            #         print(response_text.decode("utf-8"), end='', flush=True)
            print()

if __name__ == "__main__":
    main()