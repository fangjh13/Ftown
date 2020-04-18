import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from io import BytesIO
from base64 import b64encode
from typing import List


def generate_captcha_image(code: List[str] = None):
    """ generate captcha image base64 """
    # 随机字母:
    def rndChar():
        return chr(random.randint(65, 90))

    # 随机颜色1:
    def rndColor():
        return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

    # 随机颜色2:
    def rndColor2():
        return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

    # 240 x 60:
    width = 60 * 4
    height = 60
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    font = ImageFont.truetype('app/static/font/arial.ttf', 36)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor())
    # 输出文字:
    if not code:
        code = [rndChar() for i in range(4)]
    for index, t in enumerate(code):
        draw.text((60 * index + 10, 10), t, font=font, fill=rndColor2())
    # 模糊:
    image = image.filter(ImageFilter.BLUR)
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return code, str(b64encode(buffer.getvalue()), 'utf-8')
