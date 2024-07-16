import os
import subprocess
from typing import Any, List, Optional
from langchain_core.language_models import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import google.generativeai as genai

# Google AI API keyを環境変数から設定
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "your-google-api-key-here"

# Gemini Flashの設定
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class GeminiFlashLLM(LLM):
    model: str = "gemini-1.5-flash"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(prompt)
        return response.text

    @property
    def _llm_type(self) -> str:
        return "gemini-flash"

# プロンプトテンプレートの定義
template = """
You are an AI.
Your role is to improve the programming experience for the user.
Your main job is to program and, when an error is given, to suggest the content of the error and how to improve the program.
Since the user is Japanese, please make all suggestions in Japanese.
If you ignore the above conditions, there will be a penalty.

This is a template. Please make suggestions based on this template.

エラーの名前: please tell us what error is occurring.
エラーの内容: please briefly explain the reason for the error.
修正箇所: please clarify which line is wrong and why the error occurred.
修正例: please tell us how to fix the problem.

このようにして、プログラムを正しく実行することができます。

プログラム:
{program}

エラー:
{error}
"""

# プロンプトテンプレートの作成
prompt = PromptTemplate(
    input_variables=["program", "error"],
    template=template
)

# LLMの作成
llm = GeminiFlashLLM()

# RunnableSequenceの作成
chain = RunnableSequence(prompt | llm)

def generate_suggestion(program, error):
    """
    プログラムとエラーメッセージを入力として受け取り、
    AIによる修正提案を生成して返す関数
    """
    return chain.invoke({"program": program, "error": error})



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
                suggestion = generate_suggestion(program, stderr.strip())
                print(suggestion)
                print("=====================================")
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
