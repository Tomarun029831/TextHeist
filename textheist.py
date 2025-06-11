import cv2
import numpy as np
from PIL import Image
import pyautogui
import pytesseract
from PIL import ImageGrab
import subprocess
import time
import sys
from pynput import mouse

# Tesseractのパスを適宜設定
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ocr_lang = "jpn+eng"


def get_position_by_click():
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
    print(f"Opening browser for: {url}")
    subprocess.Popen(["start", "msedge", url], shell=True)
    # time.sleep(7)  # Edge起動待ち


def capture_area(pos1, pos2):
    left = min(pos1[0], pos2[0])
    top = min(pos1[1], pos2[1])
    right = max(pos1[0], pos2[0])
    bottom = max(pos1[1], pos2[1])
    img = ImageGrab.grab(bbox=(left, top, right, bottom))
    return img


def preprocess_glow_text_pil(pil_img):
    # PIL → OpenCV形式に変換
    img = np.array(pil_img.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # グレー変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # しきい値処理（白背景・黒文字 → 白文字を抽出）
    _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    # ↑ ここで黒文字を白に反転（白文字として扱う）

    invertedmask = cv2.bitwise_not(mask)

    # 白文字を膨張（＝黒文字を太くする）
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(invertedmask, kernel, iterations=0)

    invertedmask = cv2.bitwise_not(dilated)

    # 結果をPILに戻す
    final = Image.fromarray(invertedmask)
    return final


def process_pages(pos1, pos2, pos3, start_page, end_page):
    text_result = ""
    for page in range(start_page, end_page + 1):
        print(f"Processing page {page}")

        # ページ番号入力
        pyautogui.click(pos3, clicks=2)
        time.sleep(0.3)
        pyautogui.typewrite(str(page))
        pyautogui.press("enter")
        time.sleep(3)

        # キャプチャとOCR
        img = capture_area(pos1, pos2)
        img = preprocess_glow_text_pil(img)
        # img.show()

        text = pytesseract.image_to_string(img, lang=ocr_lang, config="--oem 3 --psm 6")
        text_result += f"\n--- Page {page} ---\n{text}\n"
    return text_result


def main():
    url_ranges = get_url_page_ranges()
    if not url_ranges:
        print("URLの入力がありません。終了します。")
        sys.exit(0)

    pos1, pos2, pos3 = None, None, None
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

        with open("output.txt", "a", encoding="utf-8") as f:
            f.write(f"\n=== URL: {url} ===\n{result_text}\n")

    print("すべてのURLの処理が完了しました。output.txtを確認してください。")


if __name__ == "__main__":
    main()
