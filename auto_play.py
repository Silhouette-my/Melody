import time
import mss
import numpy as np
import keyboard
import os

# ================= 配置区域 =================
# 基于你的截图分辨率 2560x1600
# 如果你的游戏窗口不是全屏或分辨率不同，需要修改这些坐标
Y_SCAN = 1373  # 判定线的 Y 坐标

# 4个轨道的 X 坐标 (对应 a, s, k, l)
X_LANES = [1031, 1190, 1324, 1470]

# 对应的按键
KEYS = ['a', 's', 'k', 'l']

# 颜色阈值 (0-255)
# 音符是白色的 (Blue通道约255)，背景/判定线是黄/黑的 (Blue通道<50)
# 只要蓝色通道 > 100，我们就认为是音符
BLUE_THRESHOLD = 100

# 屏幕索引 (如果你有多个屏幕，可能需要修改为 2 或 3)
MONITOR_IDX = 1
# ===========================================

def main():
    print("=== 音游自动脚本启动 ===")
    print(f"监测分辨率: 2560x1600 (假设)")
    print(f"监测 Y 坐标: {Y_SCAN}")
    print(f"监测 X 轨道: {X_LANES}")
    print("按 'q' 键退出脚本...")

    # 初始化 mss 截图对象
    with mss.mss() as sct:
        # 定义监测区域
        # 我们只截取判定线那一行像素，宽度覆盖所有轨道
        # 这样截图速度极快，延迟最低
        monitor = {
            "top": Y_SCAN,
            "left": 0,
            "width": 2560, # 覆盖整个宽度
            "height": 1,
            "mon": MONITOR_IDX
        }

        # 记录每个按键的当前状态 (False=松开, True=按下)
        key_states = [False, False, False, False]

        try:
            while True:
                # 1. 退出检测
                if keyboard.is_pressed('q'):
                    print("\n脚本已停止。")
                    break

                # 2. 极速截图 (返回的是 BGRA 格式的 numpy 数组)
                img = np.array(sct.grab(monitor))

                # 3. 遍历4个轨道
                for i, x in enumerate(X_LANES):
                    # 获取该轨道中心点的像素颜色
                    # img 的形状是 (height, width, channels) -> (1, 2560, 4)
                    # 通道顺序是 B, G, R, A。我们取蓝色通道 (索引0)
                    blue_value = img[0, x, 0]

                    # 判断是否有音符 (白色音符的蓝色分量很高)
                    note_detected = blue_value > BLUE_THRESHOLD

                    # 4. 执行按键逻辑
                    if note_detected:
                        if not key_states[i]:
                            # 音符出现，且之前未按下 -> 按下
                            keyboard.press(KEYS[i])
                            key_states[i] = True
                            # print(f"Down: {KEYS[i]}") # 调试用，实际使用建议注释掉以减少延迟
                    else:
                        if key_states[i]:
                            # 音符消失，且之前是按下状态 -> 松开
                            keyboard.release(KEYS[i])
                            key_states[i] = False
                            # print(f"Up: {KEYS[i]}")

                # 极速循环，不加 sleep 以追求最高刷新率

        except KeyboardInterrupt:
            pass
        finally:
            # 确保脚本退出时释放所有按键
            for k in KEYS:
                keyboard.release(k)

if __name__ == "__main__":
    # Windows下可能需要管理员权限才能模拟按键到游戏中
    main()
