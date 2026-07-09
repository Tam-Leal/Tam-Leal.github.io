"""Generate og-image.png — light card style, LED pattern without text."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630

BG = (245, 243, 239)
GRID = (210, 216, 222, 40)
FRAME_FILL = (232, 238, 244, 255)
FRAME_LINE = (143, 176, 198, 120)
INK = (14, 34, 51)
INK_DIM = (86, 120, 143)
LED = (212, 146, 32)
LED_HOT = (255, 179, 64)
LED_DIM = (200, 208, 216)

COLS = 36
ROWS = 11
DOT = 12
GAP = 5
SWEEP_X = 0.46


def load_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf" if mono else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def led_level(col: int, row: int, cols: int, rows: int) -> float:
    """Frozen radar sweep + soft wave — no letters, matches site hero feel."""
    nx = col / max(cols - 1, 1)
    ny = row / max(rows - 1, 1)
    sweep = math.exp(-((nx - SWEEP_X) ** 2) / 0.018) * 0.92
    wave = (math.sin(col * 0.55 + row * 0.9) * 0.5 + 0.5) * 0.18
    rim = math.exp(-((nx - 0.5) ** 2 + (ny - 0.5) ** 2) / 0.35) * 0.08
    return min(1.0, sweep + wave + rim + 0.05)


def draw_background(img: Image.Image) -> None:
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W, H], fill=BG)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    step = 24
    for x in range(0, W, step):
        odraw.line([(x, 0), (x, H)], fill=GRID, width=1)
    for y in range(0, H, step):
        odraw.line([(0, y), (W, y)], fill=GRID, width=1)
    img.paste(overlay, (0, 0), overlay)


def draw_matrix(img: Image.Image, cx: int, cy: int) -> None:
    matrix_w = COLS * DOT + (COLS - 1) * GAP
    matrix_h = ROWS * DOT + (ROWS - 1) * GAP
    pad = 26
    x0 = cx - matrix_w // 2
    y0 = cy - matrix_h // 2

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(frame)
    fdraw.rectangle(
        [x0 - pad, y0 - pad, x0 + matrix_w + pad, y0 + matrix_h + pad],
        fill=FRAME_FILL,
        outline=FRAME_LINE,
        width=1,
    )
    img.alpha_composite(frame)

    draw = ImageDraw.Draw(img)
    sweep_px = x0 + SWEEP_X * matrix_w

    for r in range(ROWS):
        for c in range(COLS):
            px = x0 + c * (DOT + GAP)
            py = y0 + r * (DOT + GAP)
            level = led_level(c, r, COLS, ROWS)
            center_x = px + DOT / 2

            if level > 0.35:
                glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                gdraw = ImageDraw.Draw(glow)
                alpha = int(28 + level * 55)
                gdraw.ellipse(
                    [px - 3, py - 3, px + DOT + 3, py + DOT + 3],
                    fill=(255, 179, 64, alpha),
                )
                img.alpha_composite(glow)

            t = level
            color = (
                int(LED_DIM[0] + (LED_HOT[0] - LED_DIM[0]) * t),
                int(LED_DIM[1] + (LED_HOT[1] - LED_DIM[1]) * t),
                int(LED_DIM[2] + (LED_HOT[2] - LED_DIM[2]) * t),
            )
            rad = DOT / 2 * (0.72 + t * 0.28)
            draw.ellipse(
                [center_x - rad, py + DOT / 2 - rad, center_x + rad, py + DOT / 2 + rad],
                fill=color,
            )

    sweep_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sweep_overlay)
    sdraw.rectangle(
        [sweep_px - 40, y0 - pad, sweep_px, y0 + matrix_h + pad],
        fill=(255, 210, 122, 22),
    )
    sdraw.line(
        [(sweep_px, y0 - pad), (sweep_px, y0 + matrix_h + pad)],
        fill=(255, 210, 122, 70),
        width=1,
    )
    img.alpha_composite(sweep_overlay)


def main() -> None:
    img = Image.new("RGBA", (W, H), BG)
    draw_background(img)
    draw_matrix(img, W // 2, 248)

    draw = ImageDraw.Draw(img)
    title_font = load_font(54, mono=False)
    sub_font = load_font(22, mono=True)

    title = "Tam Leal"
    sub = "AI ENGINEER"

    tb = draw.textbbox((0, 0), title, font=title_font)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, 392), title, fill=INK, font=title_font)

    sb = draw.textbbox((0, 0), sub, font=sub_font)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) // 2, 460), sub, fill=INK_DIM, font=sub_font)

    out = Path(__file__).resolve().parents[1] / "og-image.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
