import requests
import os
import json
import subprocess
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("DIFY_API_KEY")
API_URL = os.getenv("DIFY_API_URL")

def send_chat_request(program, error):
    url = API_URL
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        "inputs": {
            "program":program,
            "error":error
        },
        "response_mode": "blocking",
        "user": "Master",
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    return response.status_code, response.text

def d(error_message):
    print(f"Error: {error_message}")
    
def safe_encode(input_string):
    try:
        # エンコードを試みる
        encoded_string = input_string.encode('utf-8')
        return encoded_string
    except UnicodeEncodeError as e:
        # エラーが発生した場合、無効な文字をスキップしてエンコードする
        print(f"UnicodeEncodeError: {e}")
        encoded_string = input_string.encode('utf-8', errors='ignore')
        return encoded_string


def main():
    while True:
        cmd = input("$ ")
        if cmd == "exit":
            break
        
        cmds = cmd.split(" ")
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # リアルタイムに標準出力を取得して表示
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # エラー出力も同様に表示し、エラーがあればd関数を実行
        stderr = process.communicate()[1]
        if stderr and cmds[0] == "python3":
            
            with open(cmds[1], "r") as r:
                program = r.read()
            print("=====================================")
            print("エラーが発生しました。")
            # print(program)
            # print(stderr.strip())
            _ , response_text = send_chat_request(program, stderr.strip())
            
            response_text = safe_encode(eval(response_text)["answer"])
            print()
            print(response_text.decode("utf-8"))

# 関数の使用例
if __name__ == "__main__":
    main()