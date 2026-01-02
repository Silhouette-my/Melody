import pygame as pg
import shared_state
import sys


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


def _draw_volume_row(screen, font, label, volume, center):
    width, _ = screen.get_size()
    value = max(0, min(100, int(round(volume * 100))))
    label_image = font.render(label, True, "white")
    value_image = font.render(str(value), True, "white")
    gap_label_slider = 20
    gap_slider_value = 12
    min_slider_width = 160
    max_slider_width = max(160, width // 3)
    slider_width = max(min_slider_width, min(max_slider_width, width - 120 - label_image.get_width() - value_image.get_width()))
    total_width = label_image.get_width() + gap_label_slider + slider_width + gap_slider_value + value_image.get_width()
    start_x = int(center[0] - total_width / 2)
    label_rect = label_image.get_rect()
    label_rect.left = start_x
    label_rect.centery = center[1]
    slider_rect = pg.Rect(label_rect.right + gap_label_slider, label_rect.y, slider_width * value // 100, label_rect.height)
    value_rect = value_image.get_rect()
    value_rect.left = label_rect.right + gap_label_slider + slider_width + gap_slider_value
    value_rect.centery = center[1]
    screen.blit(label_image, label_rect)
    pg.draw.rect(screen, "white", slider_rect)
    screen.blit(value_image, value_rect)
    return pg.Rect(start_x, label_rect.y, total_width, label_rect.height)


def _render_menu(screen, font, small_font, volume, latency_ms, size_label, selected_index):
    screen.fill((0, 0, 0))
    width, height = screen.get_size()
    _draw_text_centered(screen, font, "Settings", (width // 2, height // 6))

    items = [
        f"Latency Calibration: {latency_ms} ms",
        f"Screen Size: {size_label}",
        "Back",
    ]
    rects = []
    base_y = height // 2
    rects.append(_draw_volume_row(screen, font, "Master Volume", volume, (width // 2, base_y)))
    for i, text in enumerate(items, start=1):
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
    travel_time = 900
    beat_interval = 450
    num_beats = 6
    beep = None
    if not pg.mixer.get_init():
        try:
            pg.mixer.init()
        except pg.error:
            pass
    if pg.mixer.get_init():
        sample_rate = 44100
        freq = 880
        duration = 0.08
        length = int(sample_rate * duration)
        buf = bytearray(length * 2)
        for i in range(length):
            sample = 16000 if (i * freq * 2 // sample_rate) % 2 == 0 else -16000
            buf[i * 2:i * 2 + 2] = int(sample).to_bytes(2, byteorder="little", signed=True)
        beep = pg.mixer.Sound(buffer=bytes(buf))

    pre_beats = 4
    pre_start = pg.time.get_ticks()
    start_time = pre_start + pre_beats * beat_interval
    pre_beat_times = [pre_start + i * beat_interval for i in range(pre_beats)]
    beat_times = [start_time + i * beat_interval for i in range(num_beats)]
    beat_played = [False] * num_beats
    pre_beat_played = [False] * pre_beats
    speed = (target_y - start_y) / float(travel_time)

    hits = []
    beat_index = 0
    waiting_for_result = False

    while True:
        now = pg.time.get_ticks()
        if beep is not None:
            for i, beat_time in enumerate(pre_beat_times):
                if not pre_beat_played[i] and now >= beat_time:
                    beep.play()
                    pre_beat_played[i] = True
            for i, beat_time in enumerate(beat_times):
                if not beat_played[i] and now >= beat_time:
                    beep.play()
                    beat_played[i] = True
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                return current_latency
            if ev.type == pg.KEYDOWN:
                if waiting_for_result and ev.key == pg.K_RETURN:
                    return current_latency
                if ev.key == pg.K_ESCAPE:
                    return current_latency
                if ev.key in (pg.K_SPACE, pg.K_RETURN) and beat_index < num_beats and not waiting_for_result:
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


def run_settings(master_volume=1.0, latency_ms=0, screen_size=None):
    pg.init()
    screen_sizes = [(800, 600), (1280, 760), (1920, 1080)]
    if screen_size in screen_sizes:
        size_select = screen_sizes.index(screen_size)
    else:
        size_select = 0
    screen = pg.display.set_mode(screen_sizes[size_select])
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 50)
    small_font = pg.font.SysFont(None, 26)

    selected_index = 0
    last_update_time = 0
    key_update_delay = 80
    esc_hold_start = None

    master_volume = shared_state.MASTER_VOLUME
    if pg.mixer.get_init():
        pg.mixer.music.set_volume(master_volume)

    running = True
    while running:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if ev.type == pg.KEYDOWN:
                if ev.key == pg.K_DOWN:
                    selected_index = min(selected_index + 1, 3)
                elif ev.key == pg.K_UP:
                    selected_index = max(selected_index - 1, 0)
                elif ev.key == pg.K_ESCAPE:
                    esc_hold_start = pg.time.get_ticks()
                elif ev.key == pg.K_LEFT and selected_index == 0:
                    master_volume = max(0.0, master_volume - 0.01)
                    if pg.mixer.get_init():
                        pg.mixer.music.set_volume(master_volume)
                    shared_state.MASTER_VOLUME = master_volume
                elif ev.key == pg.K_RIGHT and selected_index == 0:
                    master_volume = min(1.0, master_volume + 0.01)
                    if pg.mixer.get_init():
                        pg.mixer.music.set_volume(master_volume)
                    shared_state.MASTER_VOLUME = master_volume
                elif ev.key == pg.K_LEFT and selected_index == 2:
                    size_select = max(0, size_select - 1)
                    screen = pg.display.set_mode(screen_sizes[size_select])
                elif ev.key == pg.K_RIGHT and selected_index == 2:
                    size_select = min(len(screen_sizes) - 1, size_select + 1)
                    screen = pg.display.set_mode(screen_sizes[size_select])
                elif ev.key == pg.K_RETURN:
                    if selected_index == 1:
                        latency_ms = _run_latency_calibration(screen, font, small_font, clock, latency_ms)
                    elif selected_index == 3:
                        running = False
                        break
            if ev.type == pg.KEYUP and ev.key == pg.K_ESCAPE:
                if esc_hold_start is not None and pg.time.get_ticks() - esc_hold_start < 2000:
                    running = False
                    break
                esc_hold_start = None
        if pg.time.get_ticks() - last_update_time > key_update_delay:
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT] and selected_index == 0:
                master_volume = max(0.0, master_volume - 0.01)
                if pg.mixer.get_init():
                    pg.mixer.music.set_volume(master_volume)
                shared_state.MASTER_VOLUME = master_volume
            elif keys[pg.K_RIGHT] and selected_index == 0:
                master_volume = min(1.0, master_volume + 0.01)
                if pg.mixer.get_init():
                    pg.mixer.music.set_volume(master_volume)
                shared_state.MASTER_VOLUME = master_volume
            last_update_time = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE] and esc_hold_start is not None:
            if pg.time.get_ticks() - esc_hold_start >= 2000:
                pg.quit()
                sys.exit()
        elif not keys[pg.K_ESCAPE]:
            esc_hold_start = None

        size_label = f"{screen_sizes[size_select][0]}x{screen_sizes[size_select][1]}"
        _render_menu(screen, font, small_font, master_volume, latency_ms, size_label, selected_index)
        pg.display.update()
        clock.tick(60)

    return {
        "master_volume": master_volume,
        "latency_ms": latency_ms,
        "screen_size": screen_sizes[size_select],
    }


if __name__ == "__main__":
    run_settings()
