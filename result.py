import pygame as pg
import sys


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
    title_font = pg.font.SysFont(None, 72)
    grade_font = pg.font.SysFont(None, 120)
    font = pg.font.SysFont(None, 40)
    small_font = pg.font.SysFont(None, 24)
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
                screen = pg.display.set_mode(ev.size, pg.RESIZABLE)
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

        _draw_text_centered(screen, title_font, "RESULT", (width // 2, height // 7))
        _draw_text_centered(screen, grade_font, grade, (width // 2, height // 3), _grade_color(grade))
        _draw_text_centered(screen, font, f"SCORE: {score:,}", (width // 2, height // 3 + 90))

        left_x = width // 2 - 220
        right_x = width // 2 + 220
        mid_y = height // 2 + 10

        _draw_text_centered(screen, font, f"Max Combo: {max_combo}", (left_x, mid_y))
        _draw_text_centered(screen, font, f"Accuracy: {accuracy:.1f}%", (left_x, mid_y + 50), (120, 220, 120))

        _draw_text_centered(screen, font, f"Perfect: {perfect}", (right_x, mid_y - 10))
        _draw_text_centered(screen, font, f"Great: {good}", (right_x, mid_y + 30))
        _draw_text_centered(screen, font, f"Bad: {bad}", (right_x, mid_y + 70))
        _draw_text_centered(screen, font, f"Miss: {miss}", (right_x, mid_y + 110))

        _draw_text_centered(screen, font, f"Song: {title}", (width // 2, height - 160))

        option_rects = []
        option_y = height - 110
        for i, text in enumerate(options):
            option_rects.append(_draw_text_centered(screen, font, text, (width // 2, option_y + i * 45)))
        _draw_option_border(screen, option_rects, selected_index)

        _draw_text_centered(
            screen,
            small_font,
            "Up/Down to choose, Enter to confirm, Esc to go back",
            (width // 2, height - 30),
        )

        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    run_result({}, (800,600))
