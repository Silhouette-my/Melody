import pygame as pg
import sys


def _draw_text_centered(screen, font, text, center):
    image = font.render(text, True, "white")
    rect = image.get_rect(center=center)
    screen.blit(image, rect)
    return rect


def _draw_option_border(screen, rects, index):
    border_x = rects[index].x - 6
    border_y = rects[index].y - 4
    border_w = rects[index].width + 12
    border_h = rects[index].height + 8
    pg.draw.rect(screen, "white", pg.Rect(border_x, border_y, border_w, border_h), 1)


def run_result(result_data, screen_size):
    pg.init()
    screen = pg.display.set_mode(screen_size)
    title_font = pg.font.SysFont(None, 60)
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

    options = ["Retry", "Back"]
    selected_index = 0
    esc_hold_start = None

    while True:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                pg.quit()
                sys.exit()
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

        screen.fill((0, 0, 0))
        width, height = screen.get_size()
        _draw_text_centered(screen, title_font, "Result", (width // 2, height // 6))
        _draw_text_centered(screen, font, title, (width // 2, height // 6 + 50))

        line_y = height // 2 - 80
        _draw_text_centered(screen, font, f"Score: {score}", (width // 2, line_y))
        _draw_text_centered(screen, font, f"Accuracy: {accuracy:.2f}%", (width // 2, line_y + 50))
        _draw_text_centered(screen, font, f"Max Combo: {max_combo}", (width // 2, line_y + 100))
        _draw_text_centered(
            screen,
            font,
            f"P:{perfect}  G:{good}  B:{bad}  M:{miss}",
            (width // 2, line_y + 150),
        )

        option_rects = []
        option_y = height - 120
        for i, text in enumerate(options):
            option_rects.append(_draw_text_centered(screen, font, text, (width // 2, option_y + i * 50)))
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
    run_result({}, (800, 600))
