"""Generate og-image.png matching the portfolio LED matrix style."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630

BP = (14, 34, 51)
BP_DEEP = (10, 25, 38)
INK = (220, 233, 245)
INK_DIM = (143, 176, 198)
LED = (255, 179, 64)
LED_GLOW = (255, 210, 122)
HAIRLINE = (143, 176, 198, 56)

FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10011", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}

WORD = "BEYOND"
CHAR_W = 6
ROWS = 11


def cols_for(word: str) -> int:
    return len(word) * CHAR_W + 3


def build_target(word: str) -> list[list[int]]:
    cols = cols_for(word)
    grid = [[0 for _ in range(cols)] for _ in range(ROWS)]
    word_cols = len(word) * CHAR_W - 1
    start_c = (cols - word_cols) // 2
    start_r = 2
    for i, ch in enumerate(word):
        glyph = FONT.get(ch, FONT[" "])
        for r in range(7):
            for c in range(5):
                if glyph[r][c] == "1":
                    grid[start_r + r][start_c + i * CHAR_W + c] = 1
    return grid


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    for y in range(H):
        t = y / H
        r = int(BP[0] * (1 - t) + BP_DEEP[0] * t)
        g = int(BP[1] * (1 - t) + BP_DEEP[1] * t)
        b = int(BP[2] * (1 - t) + BP_DEEP[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    grid_color = (126, 178, 214, 18)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    step = 24
    for x in range(0, W, step):
        odraw.line([(x, 0), (x, H)], fill=grid_color, width=1)
    for y in range(0, H, step):
        odraw.line([(0, y), (W, y)], fill=grid_color, width=1)
    return overlay


def draw_matrix(img: Image.Image, draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    target = build_target(WORD)
    cols = cols_for(WORD)
    dot = 14
    gap = 5
    matrix_w = cols * dot + (cols - 1) * gap
    matrix_h = ROWS * dot + (ROWS - 1) * gap
    pad = 28
    frame_x0 = cx - matrix_w // 2 - pad
    frame_y0 = cy - matrix_h // 2 - pad
    frame_x1 = cx + matrix_w // 2 + pad
    frame_y1 = cy + matrix_h // 2 + pad

    frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(frame)
    fdraw.rectangle(
        [frame_x0, frame_y0, frame_x1, frame_y1],
        fill=(6, 15, 24, 140),
        outline=(143, 176, 198, 56),
        width=1,
    )
    img.alpha_composite(frame)

    x0 = cx - matrix_w // 2
    y0 = cy - matrix_h // 2

    for r in range(ROWS):
        for c in range(cols):
            lit = target[r][c]
            px = x0 + c * (dot + gap)
            py = y0 + r * (dot + gap)
            if lit:
                glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                gdraw = ImageDraw.Draw(glow)
                gdraw.ellipse(
                    [px - 4, py - 4, px + dot + 4, py + dot + 4],
                    fill=(255, 179, 64, 40),
                )
                img.alpha_composite(glow)
                color = LED
            else:
                color = (90, 60, 50, 70)
            draw.ellipse([px, py, px + dot, py + dot], fill=color)


def load_font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consola.ttf" if mono else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main() -> None:
    img = Image.new("RGBA", (W, H), BP)
    draw = ImageDraw.Draw(img)

    grid_overlay = draw_background(draw)
    img = Image.alpha_composite(img, grid_overlay)
    draw = ImageDraw.Draw(img)

    draw_matrix(img, draw, W // 2, 250)

    title_font = load_font(54, mono=False)
    sub_font = load_font(22, mono=True)

    title = "Tam Leal"
    sub = "AI ENGINEER"

    tb = draw.textbbox((0, 0), title, font=title_font)
    tw = tb[2] - tb[0]
    draw.text(((W - tw) // 2, 390), title, fill=INK, font=title_font)

    sb = draw.textbbox((0, 0), sub, font=sub_font)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) // 2, 458), sub, fill=INK_DIM, font=sub_font)

    out = Path(__file__).resolve().parents[1] / "og-image.png"
    img.convert("RGB").save(out, "PNG", optimize=True)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
