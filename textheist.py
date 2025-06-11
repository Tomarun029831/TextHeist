import cv2
import numpy as np
from PIL import Image, ImageGrab
import pyautogui
import pytesseract
import subprocess
import time
import sys
from pynput import mouse

# ===== 設定 =====
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
OCR_LANG = "jpn+eng"
OUTPUT_FILE = "output.txt"


# ===== ユーティリティ関数 =====
def get_position_by_click():
    """マウスクリックで座標を取得"""
    pos = []

    def on_click(x, y, button, pressed):
        if pressed:
            pos.append((x, y))
            print(f"取得した座標: {x}, {y}")
            return False

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    return pos[0]


def get_url_page_ranges():
    """URLとページ範囲の入力を受け取る"""
    print("URLとページ範囲を入力してください（例：https://〜 2 44）。ENDで終了：")
    result = []
    while True:
        line = input().strip()
        if line.upper() == "END":
            break
        parts = line.split()
        if len(parts) != 3:
            print("無効な形式です。URL 開始ページ 終了ページの順で入力してください。")
            continue
        url, start, end = parts
        result.append((url, int(start), int(end)))
    return result


def open_browser(url):
    """指定URLをブラウザで開く"""
    print(f"Opening browser for: {url}")
    subprocess.Popen(["start", "msedge", url], shell=True)


def capture_area(pos1, pos2):
    """指定範囲をキャプチャ"""
    left, top = min(pos1[0], pos2[0]), min(pos1[1], pos2[1])
    right, bottom = max(pos1[0], pos2[0]), max(pos1[1], pos2[1])
    return ImageGrab.grab(bbox=(left, top, right, bottom))


def preprocess_glow_text_pil(pil_img):
    """OCR用に画像を前処理（白文字抽出）"""
    img = np.array(pil_img.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    inverted = cv2.bitwise_not(mask)
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(inverted, kernel, iterations=0)
    final_mask = cv2.bitwise_not(dilated)
    return Image.fromarray(final_mask)


def process_pages(pos1, pos2, pos3, start_page, end_page):
    """指定ページ範囲を処理してOCR結果を返す"""
    text_result = ""
    for page in range(start_page, end_page + 1):
        print(f"Processing page {page}")
        pyautogui.click(pos3, clicks=2)
        time.sleep(0.3)
        pyautogui.typewrite(str(page))
        pyautogui.press("enter")
        time.sleep(3)

        img = capture_area(pos1, pos2)
        processed_img = preprocess_glow_text_pil(img)
        text = pytesseract.image_to_string(
            processed_img, lang=OCR_LANG, config="--oem 3 --psm 6"
        )
        text_result += f"\n--- Page {page} ---\n{text}\n"
    return text_result


# ===== メイン処理 =====
def main():
    url_ranges = get_url_page_ranges()
    if not url_ranges:
        print("URLの入力がありません。終了します。")
        sys.exit(0)

    pos1 = pos2 = pos3 = None

    for url, begin, end in url_ranges:
        open_browser(url)

        if pos1 is None:
            print("キャプチャ範囲の左上をクリックしてください")
            pos1 = get_position_by_click()

        if pos2 is None:
            print("キャプチャ範囲の右下をクリックしてください")
            pos2 = get_position_by_click()

        if pos3 is None:
            print("ページ番号を入力する場所をダブルクリックしてください")
            pos3 = get_position_by_click()

        result_text = process_pages(pos1, pos2, pos3, begin, end)

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n=== URL: {url} ===\n{result_text}\n")

    print("すべてのURLの処理が完了しました。output.txtを確認してください。")


if __name__ == "__main__":
    main()
