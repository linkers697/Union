# FINAL UPDATED thumbnail.py WITH AURA EFFECT
# (Professional color grading + subtle lighting + glow + no over-saturation)

# --- NOTE ---
# Your main logic, caching, API usage, layout, fonts — NOTHING changed.
# Only visual rendering upgraded to AURA style.
# This code is safe to replace directly.

import random
import logging
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch

logging.basicConfig(level= logging.INFO)

# -----------------------------------------------------
# SAME FUNCTIONS — NO CHANGE
# -----------------------------------------------------
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generate_gradient(width, height, start_color, end_color):
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(60 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def add_border(image, border_width, border_color):
    width, height = image.size
    new_width = width + 2 * border_width
    new_height = height + 2 * border_width
    new_image = Image.new("RGBA", (new_width, new_height), border_color)
    new_image.paste(image, (border_width, border_width))
    return new_image

def crop_center_circle(img, output_size, border, border_color, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    img = img.resize((output_size - 2*border, output_size - 2*border))
    final_img = Image.new("RGBA", (output_size, output_size), border_color)

    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    final_img.paste(img, (border, border), mask_main)

    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)

    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    return result

def draw_text_with_shadow(background, draw, position, text, font, fill, shadow_offset=(3, 3), shadow_blur=5):
    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text(position, text, font=font, fill="black")
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    background.paste(shadow, shadow_offset, shadow)
    draw.text(position, text, font=font, fill=fill)


# -----------------------------------------------------
# MAIN THUMBNAIL GENERATOR (UPGRADED VISUALS)
# -----------------------------------------------------
async def gen_thumb(videoid: str):
    try:
        if os.path.isfile(f"cache/{videoid}_v4.png"):
            return f"cache/{videoid}_v4.png"

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = result.get("title")
            if title:
                title = re.sub("\W+", " ", title).title()
            else:
                title = "Unsupported Title"
            duration = result.get("duration") or "Live"
            thumbnail_data = result.get("thumbnails")
            thumbnail = thumbnail_data[0]["url"].split("?")[0] if thumbnail_data else None
            views_data = result.get("viewCount")
            views = views_data.get("short") if views_data else "Unknown Views"
            channel_data = result.get("channel")
            channel = channel_data.get("name") if channel_data else "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                content = await resp.read()
                if resp.status == 200:
                    content_type = resp.headers.get('Content-Type')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        extension = 'jpg'
                    elif 'png' in content_type:
                        extension = 'png'
                    else:
                        return None

                    filepath = f"cache/thumb{videoid}.png"
                    f = await aiofiles.open(filepath, mode="wb")
                    await f.write(content)
                    await f.close()

        image_path = f"cache/thumb{videoid}.png"
        youtube = Image.open(image_path)
        image1 = changeImageSize(1280, 720, youtube)

        # --------------------------------------------------
        # BACKGROUND BASE (BLUR + DARKEN + COLOR GRADING)
        # --------------------------------------------------
        image2 = image1.convert("RGBA")
        background = image2.filter(ImageFilter.GaussianBlur(22))

        # Mild professional color grading
        background = ImageEnhance.Color(background).enhance(1.25)
        background = ImageEnhance.Brightness(background).enhance(0.60)
        background = ImageEnhance.Contrast(background).enhance(1.15)

        # Slight cool filter (blue aura tone)
        blue_layer = Image.new("RGBA", background.size, (0, 120, 255, 35))
        background = Image.alpha_composite(background, blue_layer)

        draw = ImageDraw.Draw(background)

        # --------------------------------------------------
        # AURA BIG LETTERS IN BACKGROUND
        # --------------------------------------------------
        aura_font = ImageFont.truetype("AviaxMusic/assets/font3.ttf", 260)
        aura_fill = (255, 255, 255, 55)
        letters = ["A", "U", "R", "A"]
        aura_positions = [(60, 120), (340, 120), (620, 120), (900, 120)]

        for pos, letter in zip(aura_positions, letters):
            draw.text(pos, letter, font=aura_font, fill=aura_fill)

        # Glow layer
        glow_layer = Image.new("RGBA", background.size, (0,0,0,0))
        glow_draw = ImageDraw.Draw(glow_layer)
        for pos, letter in zip(aura_positions, letters):
            glow_draw.text(pos, letter, font=aura_font, fill=(0, 180, 255, 200))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(32))
        background = Image.alpha_composite(background, glow_layer)

        # --------------------------------------------------
        # CIRCLE THUMBNAIL + AURA GLOW
        # --------------------------------------------------
        circle_thumbnail = crop_center_circle(youtube, 400, 20, (0, 180, 255))
        circle_thumbnail = circle_thumbnail.resize((400, 400))
        circle_position = (120, 160)

        # Glow behind circle
        glow_circle = Image.new("RGBA", (440, 440), (0,0,0,0))
        glow_draw2 = ImageDraw.Draw(glow_circle)
        glow_draw2.ellipse((0,0,440,440), fill=(0,160,255,180))
        glow_circle = glow_circle.filter(ImageFilter.GaussianBlur(40))
        background.paste(glow_circle, (circle_position[0]-20, circle_position[1]-20), glow_circle)

        # Paste actual circle
        background.paste(circle_thumbnail, circle_position, circle_thumbnail)

        # --------------------------------------------------
        # TEXT SECTION (Same logic, cleaner glow)
        # --------------------------------------------------
        arial = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 30)
        title_font = ImageFont.truetype("AviaxMusic/assets/font3.ttf", 45)

        text_x_position = 565
        title1 = truncate(title)

        draw_text_with_shadow(background, draw, (text_x_position, 180), title1[0], title_font, (255,255,255))
        draw_text_with_shadow(background, draw, (text_x_position, 230), title1[1], title_font, (255,255,255))
        draw_text_with_shadow(background, draw, (text_x_position, 320), f"{channel}  |  {views[:23]}", arial, (255,255,255))

        # --------------------------------------------------
        # PROGRESS BAR
        # --------------------------------------------------
        line_length = 580
        line_color = (0, 180, 255)

        if duration != "Live":
            color_line_percentage = random.uniform(0.15, 0.85)
            color_line_length = int(line_length * color_line_percentage)

            start_point_color = (text_x_position, 380)
            end_point_color = (text_x_position + color_line_length, 380)
            draw.line([start_point_color, end_point_color], fill=line_color, width=9)

            start_point_white = (text_x_position + color_line_length, 380)
            end_point_white = (text_x_position + line_length, 380)
            draw.line([start_point_white, end_point_white], fill="white", width=8)

            draw.ellipse([
                end_point_color[0]-10, 370,
                end_point_color[0]+10, 390
            ], fill=line_color)
        else:
            draw.line([(text_x_position, 380), (text_x_position + line_length, 380)], fill=(255,0,0), width=9)
            draw.ellipse([
                text_x_position + line_length - 10, 370,
                text_x_position + line_length + 10, 390
            ], fill=(255,0,0))

        draw_text_with_shadow(background, draw, (text_x_position, 400), "00:00", arial, (255,255,255))
        draw_text_with_shadow(background, draw, (1080, 400), duration, arial, (255,255,255))

        # PLAY ICONS
        play_icons = Image.open("AviaxMusic/assets/play_icons.png").resize((580, 62))
        background.paste(play_icons, (text_x_position, 450), play_icons)

        os.remove(f"cache/thumb{videoid}.png")

        background_path = f"cache/{videoid}_v4.png"
        background.save(background_path)
        return background_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        return None
