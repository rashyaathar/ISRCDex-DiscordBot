import os
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

from settings.models import settings

if TYPE_CHECKING:
    from bd_models.models import BallInstance


SOURCES_PATH = Path(os.path.dirname(os.path.abspath(__file__)), "./src")
WIDTH = 1500
HEIGHT = 2000
RADIUS = 80          # Set radius for rounded rectangles

RECTANGLE_WIDTH = WIDTH - 40
RECTANGLE_HEIGHT = (HEIGHT // 5) * 2

CORNERS = ((35, 261), (1393, 992))
artwork_size = [b - a for a, b in zip(*CORNERS)]

# ===== TIP =====
#
# If you want to quickly test the image generation, there is a CLI tool to quickly generate
# test images locally, without the bot or the admin panel running:
#
# With Docker: "docker compose run admin-panel django-admin preview > image.png"
# Without: "DJANGO_SETTINGS_MODULE=admin_panel.settings python3 -m django preview"
#
# This will either create a file named "image.png" or directly display it using your system's
# image viewer. There are options available to specify the ball or the special background,
# use the "--help" flag to view all options.

title_font = ImageFont.truetype(str(SOURCES_PATH / "Outfit-VariableFont.ttf"), 170)
title_font.set_variation_by_name('SemiBold')
capacity_name_font = ImageFont.truetype(str(SOURCES_PATH / "Outfit-VariableFont.ttf"), 110)
capacity_name_font.set_variation_by_name('Medium')
capacity_description_font = ImageFont.truetype(str(SOURCES_PATH / "Outfit-VariableFont.ttf"), 75)
capacity_description_font.set_variation_by_name('Regular')
stats_font = ImageFont.truetype(str(SOURCES_PATH / "Outfit-VariableFont.ttf"), 130)
stats_font.set_variation_by_name('SemiBold')
rarity_font = ImageFont.truetype(str(SOURCES_PATH / "Outfit-VariableFont.ttf"), 50)
rarity_font.set_variation_by_name('Light')
credits_font = ImageFont.truetype(str(SOURCES_PATH / "Outfit-VariableFont.ttf"), 40)
credits_font.set_variation_by_name('Light')

credits_color_cache = {}

# Draw alpha layer (use for rounded rectangles)
def create_alpha_layer(image, radius) -> Image.Image:
    alpha = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.rounded_rectangle([0,0,image.width,image.height], radius=radius, fill=255)

    image.putalpha(alpha)
    return image


def get_credit_color(image: Image.Image, region: tuple) -> tuple:
    image = image.crop(region)
    brightness = sum(image.convert("L").getdata()) / image.width / image.height  # type: ignore
    return (0, 0, 0, 255) if brightness > 100 else (255, 255, 255, 255)


def draw_card(ball_instance: "BallInstance") -> tuple[Image.Image, dict[str, Any]]:
    ball = ball_instance.countryball
    ball_health = (237, 115, 101, 255)
    ball_credits = ball.credits
    special_credits = ""
    card_name = ball.cached_regime.name
    if special_image := ball_instance.special_card:
        card_name = getattr(ball_instance.specialcard, "name", card_name)
        image = Image.open(special_image)
        if ball_instance.specialcard and ball_instance.specialcard.credits:
            special_credits += f" • Special Author: {ball_instance.specialcard.credits}"
    else:
        image = Image.open(ball.cached_regime.background)
    image = image.convert('RGB')                            # Convert to RGB if capacity frame enabled, RGBA otherwise
    icon = Image.open(ball.cached_economy.icon).convert("RGBA") if ball.cached_economy else None

    draw = ImageDraw.Draw(image, 'RGBA')

    # Capacity Frame: draw rectangle behind capacity and stats (disable if baked into template)
    if not ball_instance.capacity_frame_drawn:
        draw.rectangle(((35, 1040), (1392, 1850)), fill=(0, 0, 0, 128), outline=(255, 255, 255, 255), width=5)
    #draw.text((50, 20), ball.short_name or ball.country, font=title_font, stroke_width=2, stroke_fill=(0, 0, 0, 255))
    # Draw name
    draw.text((40, 10), ball.short_name or ball.country, font=title_font, stroke_width=5,
              stroke_fill=(0, 0, 0, 255))

    # Draw capacity
    cap_name = textwrap.wrap(f"Ability: {ball.capacity_name}", width=26)

    for i, line in enumerate(cap_name):
        draw.text(
            (60, 1050 + 100 * i),
            line,
            font=capacity_name_font,
            fill=(230, 230, 230, 255),
            stroke_width=2,
            stroke_fill=(0, 0, 0, 255),
        )

    capacity_description_lines = (
        wrapped_line
        for newline in ball.capacity_description.splitlines()
        for wrapped_line in textwrap.wrap(newline, 40)
    )

    for i, line in enumerate(capacity_description_lines):
        draw.text(
            (60, 1100 + 100 * len(cap_name) + 80 * i),
            line,
            font=capacity_description_font,
            stroke_width=1,
            stroke_fill=(0, 0, 0, 255),
        )

    # Draw health and attack
    draw.text(
        (320, 1670),
        str(ball_instance.health),
        font=stats_font,
        fill=ball_health,
        stroke_width=1,
        stroke_fill=(0, 0, 0, 255),
    )
    draw.text(
        (1120, 1670),
        str(ball_instance.attack),
        font=stats_font,
        fill=(252, 194, 76, 255),
        stroke_width=1,
        stroke_fill=(0, 0, 0, 255),
        anchor="ra",
    )

    # Draw rarity and credits
    if settings.show_rarity:
        #draw.text((1200, 50), str(ball.rarity), font=stats_font, stroke_width=2, stroke_fill=(0, 0, 0, 255))
        draw.text((45, 190), f"Rarity: {str(ball.rarity)}", font=rarity_font,
                  stroke_width=2, stroke_fill=(0, 0, 0, 255))
    if card_name in credits_color_cache:
        credits_color = credits_color_cache[card_name]
    else:
        credits_color = get_credit_color(image, (0, int(image.height * 0.8), image.width, image.height))
        credits_color_cache[card_name] = credits_color
    draw.text(
        (31, 1870),
        # Modifying the line below is breaking the licence as you are removing credits
        # If you don't want to receive a DMCA, just don't
        f"Ballsdex created by El Laggron{special_credits}\nArtwork author: {ball_credits}",
        font=credits_font,
        fill=credits_color,
        stroke_width=0,
        stroke_fill=(255, 255, 255, 255),
    )

    # Open and place artwork
    artwork = Image.open(ball.collection_card).convert('RGBA')
    image.paste(ImageOps.fit(artwork, artwork_size), CORNERS[0])  # type: ignore

    # Disabled by default, enable if rounded rectangle used as background
    #create_alpha_layer(image=image, radius=RADIUS)

    if icon:
        icon = ImageOps.fit(icon, (192, 192))
        image.paste(icon, (1200, 30), mask=icon)
        icon.close()
    artwork.close()

    return image, {"format": 'WEBP'}
