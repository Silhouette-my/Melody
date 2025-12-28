import pygame as pg


def _draw_text_centered(screen, font, text, center):
    text_image = font.render(text, True, "white")
    text_rect = text_image.get_rect(center=center)
    screen.blit(text_image, text_rect)
    return text_rect


def _button_border_draw(screen, text_rect, select_flag):
    border_x = text_rect[select_flag].x - 5
    border_y = text_rect[select_flag].y - 5
    border_width = text_rect[select_flag].width + 10
    border_height = text_rect[select_flag].height + 10
    last_rect = pg.Rect(border_x, border_y, border_width, border_height)
    pg.draw.rect(screen, "white", last_rect, 1)
    return last_rect


def _render_menu(screen, font, small_font, volume, latency_ms, selected_index):
    screen.fill((0, 0, 0))
    width, height = screen.get_size()
    _draw_text_centered(screen, font, "Settings", (width // 2, height // 6))

    items = [
        f"Master Volume: {int(volume * 100)}%",
        f"Latency Calibration: {latency_ms} ms",
        "Back",
    ]
    rects = []
    base_y = height // 2
    for i, text in enumerate(items):
        rects.append(_draw_text_centered(screen, font, text, (width // 2, base_y + i * 60)))
    _draw_text_centered(
        screen,
        small_font,
        "Use Up/Down to select, Left/Right to adjust volume, Enter to confirm",
        (width // 2, height - 40),
    )
    _button_border_draw(screen, rects, selected_index)
    return rects


def _run_latency_calibration(screen, font, small_font, clock, current_latency):
    width, height = screen.get_size()
    start_y = -30
    target_y = height - 140
    travel_time = 1200
    beat_interval = 600
    num_beats = 6

    start_time = pg.time.get_ticks() + 1000
    beat_times = [start_time + i * beat_interval for i in range(num_beats)]
    speed = (target_y - start_y) / float(travel_time)

    hits = []
    beat_index = 0
    waiting_for_result = False

    while True:
        now = pg.time.get_ticks()
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                return current_latency
            if ev.type == pg.KEYDOWN:
                if waiting_for_result and ev.key == pg.K_RETURN:
                    return current_latency
                if ev.key == pg.K_ESCAPE:
                    return current_latency
                if ev.key == pg.K_SPACE and beat_index < num_beats and not waiting_for_result:
                    offset = now - beat_times[beat_index]
                    hits.append(offset)
                    beat_index += 1

        screen.fill((0, 0, 0))
        _draw_text_centered(screen, font, "Latency Calibration", (width // 2, height // 8))
        _draw_text_centered(
            screen, small_font, "Press Space on the beat (Esc to cancel)", (width // 2, height // 8 + 40)
        )

        pg.draw.line(screen, "white", (width // 2 - 60, target_y), (width // 2 + 60, target_y), 2)

        for beat_time in beat_times:
            dt = beat_time - now
            if -200 <= dt <= travel_time:
                y = target_y - dt * speed
                pg.draw.circle(screen, "white", (width // 2, int(y)), 12, 2)

        if beat_index >= num_beats and not waiting_for_result:
            avg = sum(hits) / float(len(hits)) if hits else 0.0
            current_latency = int(round(avg))
            waiting_for_result = True

        if waiting_for_result:
            _draw_text_centered(
                screen,
                small_font,
                f"Measured latency: {current_latency} ms. Press Enter to return.",
                (width // 2, height - 60),
            )

        pg.display.update()
        clock.tick(60)


def run_settings():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 50)
    small_font = pg.font.SysFont(None, 26)

    selected_index = 0
    master_volume = 1.0
    latency_ms = 0

    if pg.mixer.get_init():
        pg.mixer.music.set_volume(master_volume)

    running = True
    while running:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
                break
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_DOWN:
                    selected_index = min(selected_index + 1, 2)
                elif ev.key == pg.K_UP:
                    selected_index = max(selected_index - 1, 0)
                elif ev.key == pg.K_LEFT and selected_index == 0:
                    master_volume = max(0.0, master_volume - 0.05)
                    if pg.mixer.get_init():
                        pg.mixer.music.set_volume(master_volume)
                elif ev.key == pg.K_RIGHT and selected_index == 0:
                    master_volume = min(1.0, master_volume + 0.05)
                    if pg.mixer.get_init():
                        pg.mixer.music.set_volume(master_volume)
                elif ev.key == pg.K_RETURN:
                    if selected_index == 1:
                        latency_ms = _run_latency_calibration(screen, font, small_font, clock, latency_ms)
                    elif selected_index == 2:
                        running = False
                        break

        _render_menu(screen, font, small_font, master_volume, latency_ms, selected_index)
        pg.display.update()
        clock.tick(60)

    return {"master_volume": master_volume, "latency_ms": latency_ms}


if __name__ == "__main__":
    run_settings()
