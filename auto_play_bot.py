import time
import keyboard
import mss
import numpy as np
from colorama import Fore, Style, init

# 初始化彩色输出
init()

print(Fore.CYAN + "=== 下落式音游自动脚本 ===" + Style.RESET_ALL)
print("功能：自动检测白色音符并点击 A/S/K/L")
print("要求：请将游戏窗口置于屏幕【左上角】，并保持截图中的分辨率或全屏。")
print("提示：按 'q' 键退出脚本。")
print("--------------------------------")

# ================= 配置区域 =================
# 基于提供的截图分析出的坐标 (1926x1197)
# 如果你的游戏分辨率不同，请相应调整以下数值

# 判定线的 Y 坐标 (截图分析为 1042，稍微提前一点以保证 Perfect)
CHECK_Y = 1040 

# 四个轨道的 X 坐标
# 轨道 1 (A): 738
# 轨道 2 (S): 888
# 轨道 3 (K): 1038
# 轨道 4 (L): 1188
TRACK_X = [738, 888, 1038, 1188]

# 对应的按键
KEYS = ['a', 's', 'k', 'l']

# 颜色阈值：RGB中任意一个分量大于此值即认为是白色音符
# 截图中的音符是纯白 (255, 255, 255)，背景很暗
WHITE_THRESHOLD = 230
# ===========================================

def main():
    # 记录每个轨道的按键状态 (False: 未按下, True: 已按下)
    key_states = [False] * 4
    
    # 实例化屏幕截取对象
    with mss.mss() as sct:
        # 定义截取区域：只截取判定线这一行像素
        # region = {"top": y, "left": 0, "width": 屏幕宽度, "height": 1}
        # 为了兼容性，宽度设为最大可能的 1926 (或检测屏幕宽度)
        monitor_width = sct.monitors[1]['width']
        region = {"top": CHECK_Y, "left": 0, "width": monitor_width, "height": 1}
        
        print(Fore.GREEN + f"[*] 开始监听... 截取行: {CHECK_Y}" + Style.RESET_ALL)
        
        try:
            while True:
                if keyboard.is_pressed('q'):
                    print("\n退出脚本。")
                    break

                # 1. 极速截屏 (返回的是 BGRA 格式的 numpy 数组)
                # output shape: (1, width, 4)
                img = np.array(sct.grab(region))
                
                # 2. 遍历 4 个轨道
                for i, x in enumerate(TRACK_X):
                    if x >= monitor_width:
                        continue # 防止越界

                    # 获取像素颜色 (B, G, R, A)
                    # img[0, x] 是第 0 行，第 x 列的像素
                    pixel = img[0, x]
                    
                    # 判断是否为白色 (音符)
                    # 只要 B, G, R 都很高，就是白色
                    # 也可以简单判断 Blue 分量，因为黄色(判定线)的 Blue 分量很低(0)，而白色是 255
                    # 这样可以防止误触黄线
                    blue_val = pixel[0]
                    green_val = pixel[1]
                    red_val = pixel[2]
                    
                    # 逻辑：如果是白色 (音符)，则按下；否则松开
                    # 注意：判定线是黄色的 (R=255, G=255, B=0)，所以检测 Blue > 200 可以完美区分音符和判定线
                    is_note = (blue_val > WHITE_THRESHOLD) and (green_val > WHITE_THRESHOLD) and (red_val > WHITE_THRESHOLD)

                    if is_note:
                        if not key_states[i]:
                            keyboard.press(KEYS[i])
                            key_states[i] = True
                            # print(f"Press {KEYS[i]}") # 调试用，为了性能建议注释
                    else:
                        if key_states[i]:
                            keyboard.release(KEYS[i])
                            key_states[i] = False
                            # print(f"Release {KEYS[i]}")

                # 极短的休眠防止 CPU 占用过高，但对于音游，建议保持尽可能低的 sleep 或不 sleep
                # time.sleep(0.001) 
                
        except KeyboardInterrupt:
            pass
        finally:
            # 确保退出时释放所有按键
            for k in KEYS:
                keyboard.release(k)

if __name__ == "__main__":
    main()
