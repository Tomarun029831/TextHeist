---
# 📄 OCR Automation Tool with Python

このプロジェクトは、Webページ上のドキュメントから画面キャプチャを行い、OCR（光学文字認識）でテキストを抽出する自動化ツールです。

---

## ✅ 主な機能

- Microsoft Edge で指定URLを自動で開く
- マウスクリックでキャプチャ範囲を指定
- ページ番号を自動入力してページ遷移
- 白文字や光る文字に対応した画像前処理
- Tesseract OCR によるテキスト抽出
- 結果を `output.txt` に保存

---

## 🧰 必要環境

- Windows OS（`ImageGrab` と `pyautogui` のため）
- Python 3.7 以上
- Tesseract OCR（別途インストールが必要）

---

## 📦 インストール手順

### 1. Python パッケージのインストール

PowerShell またはターミナルで以下を実行：

```powershell
pip install opencv-python numpy pillow pyautogui pytesseract pynput
```

### 2. Tesseract OCR のインストール（Windows）

以下のコマンドで Tesseract をインストール：

```powershell
winget install --id tesseract-ocr.tesseract -e
```

インストール後、Python スクリプト内で以下のようにパスを設定してください：

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
日本語対応の場合、公式からテザラクトの日本語データをc:program/tessarctocr/tessdate/にお入れ願います。
---

## 🚀 使い方

1. スクリプトを実行：

```bash
python textheist.py
```

2. 指示に従って以下を入力：
   - URLとページ範囲（例：`https://example.com 2 44`）
   - キャプチャ範囲の左上・右下をクリック
   - ページ番号入力欄をクリック

3. 自動でページを切り替えながらOCRを実行し、結果を `output.txt` に保存します。

---

## ⚠️ 注意点（OCR精度について）
- 黒板風背景(茶色枠に緑の背景)に、緑色に縁(ふち)取られた白い文字と黄色い文字のみを対象にしています。
- OCRの精度は **そこそこ** です。
- 特に日本語や光る文字などは誤認識されることがあります。
- **手動での誤字修正が前提** となります。

---

## 📄 ライセンス

MIT License
