# CodeMend
CodeMendはPython プログラムのエラーを自動的に診断し、改善のための提案を行うパッケージです。このパッケージは、リアルタイムでプログラムの標準出力とエラーをキャプチャし、エラーが発生した場合に外部APIを使用して詳細なエラー説明と修正提案を提供します。

## 主な機能
- プログラムの実行時にエラーが発生した場合、エラーの詳細な説明と修正提案を提供します。

## インストール
CodeMendはpipを使用してインストールできます。
```bash
pip install git+https://github.com/Accord33/CodeMend.git
```

## 使い方
CodeMendを使用するためには、```DIFY_API_URL```と```DIFY_API_KEY```という環境変数の追加が必要です。<br>
pipでインストールした後、```codemend```コマンドを使用してCodeMendを実行できます。<br>
現状python3コマンドを実行した時に、エラーを取得し提案を提供します。