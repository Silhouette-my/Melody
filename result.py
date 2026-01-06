import pygame as pg
import sys


def _get_scale_factor(screen_size):
    """获取相对于800x600基准分辨率的缩放因子"""
    base_width, base_height = 800, 600
    width, height = screen_size
    
    # 计算宽高两个方向的缩放比例，取较小值以保证整体适配
    scale_w = width / base_width
    scale_h = height / base_height
    return min(scale_w, scale_h)


def _draw_text_centered(screen, font, text, center, color="white"):
    image = font.render(text, True, color)
    rect = image.get_rect(center=center)
    screen.blit(image, rect)
    return rect


def _draw_option_border(screen, rects, index):
    border_x = rects[index].x - 6
    border_y = rects[index].y - 4
    border_w = rects[index].width + 12
    border_h = rects[index].height + 8
    pg.draw.rect(screen, "white", pg.Rect(border_x, border_y, border_w, border_h), 1)


def _grade_from_accuracy(accuracy):
    if accuracy == 100.0:
        return "SS"
    if accuracy >= 98.0:
        return "S"
    if accuracy >= 95.0:
        return "A"
    if accuracy >= 90.0:
        return "B"
    if accuracy >= 80.0:
        return "C"
    return "D"


def _grade_color(grade):
    if grade == "SS":
        return (255, 215, 0)
    if grade == "S":
        return (120, 220, 255)
    if grade == "A":
        return (120, 220, 120)
    if grade == "B":
        return (255, 210, 120)
    if grade == "C":
        return (255, 160, 120)
    return (255, 120, 120)


def _draw_vignette(screen, strength=110):
    width, height = screen.get_size()
    overlay = pg.Surface((width, height), pg.SRCALPHA)
    max_radius = int(max(width, height) * 0.75)
    center = (width // 2, height // 2)
    for r in range(max_radius, 0, -40):
        alpha = int(strength * (1 - r / max_radius))
        pg.draw.circle(overlay, (0, 0, 0, alpha), center, r)
    screen.blit(overlay, (0, 0))


def run_result(result_data, screen_size):
    pg.init()
    screen = pg.display.set_mode(screen_size, pg.RESIZABLE)
    
    # 计算缩放因子
    scale_factor = _get_scale_factor(screen_size)
    
    # 根据缩放因子动态计算字体大小
    title_font_size = int(72 * scale_factor)
    grade_font_size = int(120 * scale_factor)
    font_size = int(40 * scale_factor)
    small_font_size = int(24 * scale_factor)
    
    # 创建字体对象
    title_font = pg.font.SysFont(None, title_font_size)
    grade_font = pg.font.SysFont(None, grade_font_size)
    font = pg.font.SysFont(None, font_size)
    small_font = pg.font.SysFont(None, small_font_size)
    
    clock = pg.time.Clock()

    title = result_data.get("title", "Result")
    score = result_data.get("score", 0)
    max_combo = result_data.get("max_combo", 0)
    perfect = result_data.get("perfect", 0)
    good = result_data.get("good", 0)
    bad = result_data.get("bad", 0)
    miss = result_data.get("miss", 0)
    accuracy = result_data.get("accuracy", 0.0)
    grade = _grade_from_accuracy(accuracy)

    options = ["Retry", "Back"]
    selected_index = 0
    esc_hold_start = None

    while True:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if ev.type == pg.VIDEORESIZE:
                # 窗口大小改变时更新屏幕和字体
                screen = pg.display.set_mode(ev.size, pg.RESIZABLE)
                scale_factor = _get_scale_factor(ev.size)
                
                # 重新计算字体大小
                title_font_size = int(72 * scale_factor)
                grade_font_size = int(120 * scale_factor)
                font_size = int(40 * scale_factor)
                small_font_size = int(24 * scale_factor)
                
                # 重新创建字体对象
                title_font = pg.font.SysFont(None, title_font_size)
                grade_font = pg.font.SysFont(None, grade_font_size)
                font = pg.font.SysFont(None, font_size)
                small_font = pg.font.SysFont(None, small_font_size)
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_DOWN:
                    selected_index = min(len(options) - 1, selected_index + 1)
                elif ev.key == pg.K_UP:
                    selected_index = max(0, selected_index - 1)
                elif ev.key == pg.K_RETURN:
                    return "retry" if selected_index == 0 else "back"
                elif ev.key == pg.K_ESCAPE:
                    esc_hold_start = pg.time.get_ticks()
            elif ev.type == pg.KEYUP and ev.key == pg.K_ESCAPE:
                if esc_hold_start is not None and pg.time.get_ticks() - esc_hold_start < 2000:
                    return "back"
                esc_hold_start = None

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE] and esc_hold_start is not None:
            if pg.time.get_ticks() - esc_hold_start >= 2000:
                pg.quit()
                sys.exit()
        elif not keys[pg.K_ESCAPE]:
            esc_hold_start = None

        screen.fill((18, 18, 18))
        _draw_vignette(screen)
        width, height = screen.get_size()
        
        # 重新计算缩放因子（确保窗口大小变化时位置正确）
        current_scale = _get_scale_factor((width, height))
        
        # 根据800x600基准分辨率计算位置，然后乘以缩放因子
        # 基准位置 (800x600)
        base_positions = {
            'title_y': height // 7,  # RESULT标题位置
            'grade_y': height // 3,  # 等级位置
            'score_y': height // 3 + int(90 * current_scale),  # 分数位置
            'left_x': width // 2 - int(220 * current_scale),  # 左侧区域X坐标
            'right_x': width // 2 + int(180 * current_scale),  # 右侧区域X坐标
            'mid_y': height // 2 + int(30 * current_scale),  # 中间区域Y坐标
            'option_y': height - int(110 * current_scale),  # 选项区域Y坐标
            'song_y': height - int(160 * current_scale),  # 歌曲信息Y坐标
            'hint_y': height - int(30 * current_scale)  # 提示信息Y坐标
        }

        # 绘制RESULT标题
        _draw_text_centered(screen, title_font, "RESULT", (width // 2, base_positions['title_y']))
        
        # 绘制等级
        _draw_text_centered(screen, grade_font, grade, (width // 2, base_positions['grade_y']), _grade_color(grade))
        
        # 绘制分数
        _draw_text_centered(screen, font, f"SCORE: {score:,}", (width // 2, base_positions['score_y']))

        # 左侧数据：最大连击和准确率
        _draw_text_centered(screen, font, f"Max Combo: {max_combo}", 
                           (base_positions['left_x'], base_positions['mid_y'] + int(10 * current_scale)))
        _draw_text_centered(screen, font, f"Accuracy: {accuracy:.1f}%", 
                           (base_positions['left_x'], base_positions['mid_y'] + int(60 * current_scale)), 
                           (120, 220, 120))

        # 右侧数据：命中统计（使用小字体）
        stat_spacing = int(20 * current_scale)  # 行间距
        _draw_text_centered(screen, small_font, f"Perfect: {perfect}", 
                           (base_positions['right_x'], base_positions['mid_y'] + int(5 * current_scale)))
        _draw_text_centered(screen, small_font, f"Great: {good}", 
                           (base_positions['right_x'], base_positions['mid_y'] + int(25 * current_scale)))
        _draw_text_centered(screen, small_font, f"Bad: {bad}", 
                           (base_positions['right_x'], base_positions['mid_y'] + int(45 * current_scale)))
        _draw_text_centered(screen, small_font, f"Miss: {miss}", 
                           (base_positions['right_x'], base_positions['mid_y'] + int(65 * current_scale)))

        # 绘制歌曲信息
        _draw_text_centered(screen, font, f"Song: {title}", (width // 2, base_positions['song_y']))

        # 绘制选项按钮
        option_rects = []
        option_spacing = int(45 * current_scale)  # 选项间距
        for i, text in enumerate(options):
            option_y = base_positions['option_y'] + i * option_spacing
            option_rects.append(_draw_text_centered(screen, font, text, (width // 2, option_y)))
        
        # 绘制选项边框
        _draw_option_border(screen, option_rects, selected_index)

        # 绘制操作提示
        _draw_text_centered(
            screen,
            small_font,
            "Up/Down to choose, Enter to confirm, Esc to go back",
            (width // 2, base_positions['hint_y']),
        )

        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    run_result({}, (800,600))
