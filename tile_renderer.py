from PIL import Image, ImageDraw, ImageFont
import io

COLORS = {
    "🔴": (220, 50, 50),
    "🔵": (50, 100, 220),
    "⚫": (40, 40, 40),
    "🟡": (220, 180, 0),
}

TILE_W = 60
TILE_H = 80
PADDING = 8
BG_COLOR = (34, 34, 34)
JOKER_COLOR = (150, 0, 200)

def draw_hand(hand, joker_tile=None):
    # Taşları renge göre sırala
    sorted_hand = sorted(
        hand,
        key=lambda t: (list(COLORS.keys()).index(t.color) if t.color in COLORS else 99, t.number or 0)
    )

    cols = len(sorted_hand)
    img_w = cols * (TILE_W + PADDING) + PADDING
    img_h = TILE_H + PADDING * 2

    img = Image.new("RGB", (img_w, img_h), BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/system/fonts/DroidSans.ttf", 22)
        small_font = ImageFont.truetype("/system/fonts/DroidSans.ttf", 14)
    except:
        font = ImageFont.load_default()
        small_font = font

    for i, tile in enumerate(sorted_hand):
        x = PADDING + i * (TILE_W + PADDING)
        y = PADDING

        # Taş arka planı
        is_joker = tile.is_joker or (
            joker_tile and not tile.is_joker and
            tile.color == joker_tile.color and
            tile.number == joker_tile.number
        )

        bg = (255, 245, 220) if not is_joker else (240, 200, 255)
        draw.rounded_rectangle([x, y, x+TILE_W, y+TILE_H], radius=8, fill=bg, outline=(180,180,180), width=2)

        if tile.is_joker:
            color = JOKER_COLOR
            text = "J"
            draw.text((x + TILE_W//2, y + TILE_H//2), text, fill=color, font=font, anchor="mm")
        else:
            color = COLORS.get(tile.color, (0, 0, 0))
            number = str(tile.number)
            # Sayıyı ortaya yaz
            draw.text((x + TILE_W//2, y + TILE_H//2), number, fill=color, font=font, anchor="mm")
            # Renk noktası üste
            draw.ellipse([x+TILE_W//2-6, y+10, x+TILE_W//2+6, y+22], fill=color)
            # Sıra numarası alta
            draw.text((x + TILE_W//2, y + TILE_H - 12), str(i+1), fill=(150,150,150), font=small_font, anchor="mm")

        # Joker işareti
        if is_joker and not tile.is_joker:
            draw.rectangle([x, y, x+16, y+16], fill=JOKER_COLOR)
            draw.text((x+8, y+8), "J", fill=(255,255,255), font=small_font, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
