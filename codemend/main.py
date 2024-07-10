import requests
import os
import json
import subprocess
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーとURLを取得
API_KEY = os.getenv("DIFY_API_KEY")
API_URL = os.getenv("DIFY_API_URL")

def extract_answer(data_string):
    """
    APIから受け取ったデータ文字列から回答を抽出する。

    Args:
        data_string (str): JSONデータを含む文字列。

    Returns:
        str: 抽出された回答、または解析に失敗した場合は空文字列。
    """
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
    """
    プログラムとエラーの詳細をAPIに送信する。

    Args:
        program (str): エラーを引き起こしたプログラムコード。
        error (str): エラーメッセージ。
    """
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

    # POSTリクエストを送信し、レスポンスをストリーミングで受け取る
    with requests.post(url, headers=headers, json=data, stream=True) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                print(extract_answer(line.decode("utf-8")), end='', flush=True)

def main():
    """
    ユーザー入力を処理し、コマンドを実行するメイン関数。
    """
    while True:
        cmd = input("$ ")
        if cmd == "exit":
            break
        
        if cmd == "":
            continue
        
        cmds = cmd.split(" ")
        if cmds[0] == "python3":
            # スクリプトパスが絶対パスであることを確認
            if not cmds[1].startswith("/"):
                cmds[1] = os.getcwd() + "/" + cmds[1]
            
            # Pythonスクリプトを実行
            process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    print(output.strip())

            stderr = process.communicate()[1]
            if stderr:
                with open(cmds[1], "r") as r:
                    program = r.read()
                print("=====================================")
                print("エラーが発生しました。")
                
                # エラーを解析のためにAPIに送信
                send_chat_request(program, stderr.strip())
        else:
            try:
                # Python以外のコマンドを実行
                process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
            except FileNotFoundError:
                print(f"{cmds[0]}: command not found")

if __name__ == "__main__":
    main()
