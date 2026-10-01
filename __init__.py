# -*- coding: utf-8 -*-
import time
from ascript.android import system, screen, plug
from ascript.android.screen import Ocr

# ============ 配置区 ============
APP_PACKAGE = "com.bbk.appstore"   # 改成你的目标App包名
TARGET_TEXT = "我的"               # 改成你要找的文字
# ================================


def main():
    plug.load("esp32")
    from esp32 import BleDevice
    ble = BleDevice()
    print(">>> HID连接状态:", ble.is_conncted()
          if hasattr(ble, "is_conncted") else "未知")

    print(">>> 启动App:", APP_PACKAGE)
    system.open(APP_PACKAGE)
    time.sleep(3)

    shot = screen.capture_bitmap()
    if shot is None:
        print("!!! 截图失败，检查录屏权限")
        return
    print(">>> 截图成功:", shot.getWidth(), "x", shot.getHeight())

    pos = None
    try:
        r = Ocr.find(TARGET_TEXT, image=shot, confidence=0.1)
        if r:
            if isinstance(r, dict):
                pos = (int(r.get("center_x", 0)), int(r.get("center_y", 0)))
            else:
                cx = getattr(r, "center_x", None)
                cy = getattr(r, "center_y", None)
                if cx is not None:
                    pos = (int(cx), int(cy))
    except Exception as e:
        print("OCR失败:", e)

    if not pos:
        print("!!! 没找到文字:", TARGET_TEXT)
        return
    print(">>> 找到文字:", TARGET_TEXT, "坐标:", pos)

    x, y = pos
    print(">>> HID点击:", x, y)
    ble.click(x, y)
    time.sleep(1.5)

    shot2 = screen.capture_bitmap()
    if shot2 is None:
        print("!!! 第二次截图失败")
        return

    pos2 = None
    try:
        r2 = Ocr.find(TARGET_TEXT, image=shot2, confidence=0.1)
        if r2:
            if isinstance(r2, dict):
                pos2 = (int(r2.get("center_x", 0)), int(r2.get("center_y", 0)))
            else:
                cx = getattr(r2, "center_x", None)
                cy = getattr(r2, "center_y", None)
                if cx is not None:
                    pos2 = (int(cx), int(cy))
    except Exception:
        pass

    if pos2 is None:
        print(">>> 验证通过：点击后文字消失")
    elif abs(pos2[0] - x) < 20 and abs(pos2[1] - y) < 20:
        print(">>> 验证失败：文字还在原位")
    else:
        print(">>> 验证通过：文字位置变化了")


main()
