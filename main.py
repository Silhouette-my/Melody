import pygame       # 导入 Pygame 库，用于图形界面、音频播放、键盘事件等
import time         # 导入 time 库，用于计时，控制音符出现时间
import json         # 导入 json 库，用于读取谱面文件（JSON 格式）

# ======================
# 1. 初始化模块
# ======================
def init_game(meta):
    """
    初始化游戏窗口和基本参数
    meta: JSON 文件中的 meta 字段，包含背景、轨道数等信息
    """
    pygame.init()   # 初始化 Pygame 所有模块
    screen = pygame.display.set_mode((800, 600))  # 创建游戏窗口，大小为 800x600
    pygame.display.set_caption("Rhythm Game - " + meta["song"]["title"])  # 设置窗口标题为歌曲名

    # 尝试加载背景图（如果 meta 中有 background 字段）
    background = None
    if "background" in meta:
        try:
            background = pygame.image.load(meta["background"])  # 加载背景图
        except:
            print("背景图加载失败，使用默认背景")  # 如果加载失败，打印提示

    return screen, background  # 返回窗口对象和背景图

# ======================
# 2. 主菜单与 UI 模块
# ======================
def show_main_menu(screen):
    """
    显示主菜单界面，包括开始游戏、选择歌曲、设置、退出等选项
    """
    # TODO: 绘制菜单界面，监听用户选择
    pass

def show_song_select(screen):
    """
    显示歌曲选择界面
    """
    # TODO: 列出可选歌曲，返回用户选择
    pass

def show_settings(screen):
    """
    显示设置界面（音量、难度等）
    """
    # TODO: 绘制设置界面并更新配置
    pass

# ======================
# 3. 曲谱读取模块（JSON）
# ======================
def load_notes_from_json(file_path):
    """
    从 JSON 文件读取谱面数据，并转换为游戏可用的格式
    """
    with open(file_path, "r", encoding="utf-8") as f:  # 打开 JSON 文件
        data = json.load(f)  # 解析 JSON 数据

    meta = data["meta"]       # 曲目信息（标题、作者、轨道数等）
    bpm = data["time"][0]["bpm"]  # 获取 BPM（节奏速度）
    notes_raw = data["note"]  # 原始音符数据

    # 找到音频文件（在 note 中带 sound 的条目）
    song_file = None
    for n in notes_raw:
        if "sound" in n:
            song_file = n["sound"]
            break

    # 转换 note 列表
    notes = []
    for n in notes_raw:
        if "beat" in n and "column" in n:
            beat = n["beat"]   # 例如 [6,0,4] 表示第6小节、第0拍、分母4
            column = n["column"]  # 轨道编号
            endbeat = n.get("endbeat", None)  # 长按音符的结束节拍（可选）

            # 将 beat 转换为时间（秒）
            measure, beat_num, denominator = beat
            time_sec = (measure + beat_num/denominator) * (60.0 / bpm) * 4

            note_data = {
                "time": time_sec,   # 音符出现时间
                "track": column,    # 音符轨道编号
                "end_time": None    # 长按音符结束时间（默认 None）
            }

            if endbeat:  # 如果是长按音符
                m2, b2, d2 = endbeat
                end_time_sec = (m2 + b2/d2) * (60.0 / bpm) * 4
                note_data["end_time"] = end_time_sec

            notes.append(note_data)  # 加入音符列表

    return meta, song_file, bpm, notes  # 返回谱面信息、音频文件、BPM、音符列表

# ======================
# 4. 游戏逻辑模块（四轨道）
# ======================
def update_notes(notes, current_time):
    """
    根据当前时间更新音符状态（位置、是否判定）
    """
    # TODO: 根据时间计算音符在屏幕上的位置
    pass

def check_input(event, notes, current_time):
    """
    检查玩家输入是否与音符匹配
    四条轨道对应按键：A, S, J, K
    """
    key_map = {
        pygame.K_a: 0,   # A 键对应轨道 0
        pygame.K_s: 1,   # S 键对应轨道 1
        pygame.K_j: 2,   # J 键对应轨道 2
        pygame.K_k: 3    # K 键对应轨道 3
    }
    if event.key in key_map:  # 如果按下的键在映射表中
        track = key_map[event.key]  # 获取轨道编号
        # TODO: 遍历 notes，查找匹配轨道和时间的音符，进行判定
        pass

def calculate_score(note, current_time):
    """
    根据时间差计算判定结果（Perfect / Good / Miss）
    """
    # TODO: 设定时间阈值，例如 ±50ms 为 Perfect，±100ms 为 Good
    pass

# ======================
# 5. 绘制模块
# ======================
def draw_game(screen, background, notes, score, combo):
    """
    绘制游戏界面，包括背景、轨道、音符、判定线、分数等
    """
    if background:
        screen.blit(background, (0, 0))  # 绘制背景图
    else:
        screen.fill((0, 0, 0))           # 默认黑色背景

    # TODO: 绘制轨道（根据 meta["mode_ext"]["column"] 确定轨道数）
    # TODO: 绘制下落的音符
    # TODO: 绘制判定线、分数、连击数等

    pygame.display.flip()  # 刷新屏幕，显示更新后的内容

# ======================
# 6. 主循环
# ======================
def main():
    # 读取谱面文件，获取 meta 信息、音频文件、BPM、音符列表
    meta, song_file, bpm, notes = load_notes_from_json("1709823572.json")

    # 初始化游戏窗口和背景图
    screen, background = init_game(meta)

    # 加载并播放音乐文件
    pygame.mixer.music.load(song_file)
    pygame.mixer.music.play()

    # 记录游戏开始时间，用于计算音符出现时间
    start_time = time.time()

    # 初始化分数和连击数
    score, combo = 0, 0

    # 设置游戏运行标志
    running = True

    # 游戏主循环
    while running:
        # 计算当前游戏时间（秒）
        current_time = time.time() - start_time

        # 遍历事件队列，处理用户输入和窗口事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:        # 如果点击关闭窗口
                running = False                  # 退出循环
            if event.type == pygame.KEYDOWN:     # 如果按下键盘
                check_input(event, notes, current_time)  # 检查输入是否匹配音符

        # 更新音符状态（位置、是否判定）
        update_notes(notes, current_time)

        # 绘制游戏界面（背景、轨道、音符、分数等）
        draw_game(screen, background, notes, score, combo)

    # 退出 Pygame
    pygame.quit()

# 程序入口
if __name__ == "__main__":
    main()  # 调用主函数，启动游戏
