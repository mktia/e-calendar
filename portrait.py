# -*- coding: utf-8 -*-

import calendar
from datetime import date, datetime
import itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from connect_calendar import Calendar


def get_font(font_symbol: str, font_size: int):
    return ImageFont.truetype(font_files[font_symbol], font_size)


def get_width(text: str, font_symbol: str, font_size: int):
    bbox = draw.multiline_textbbox(
        (0, 0), text,
        font=get_font(font_symbol, font_size)
    )
    return bbox[2] - bbox[0]


def padding_width(width: int, text: str, font_symbol: str, font_size: int):
    return (width - get_width(text, font_symbol, font_size)) // 2


# for mac only
font_files = dict(
    en='/System/Library/Fonts/Optima.ttc',
    ja='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
    title='/System/Library/Fonts/Supplemental/Zapfino.ttf'
)
# grey scale
grey = np.arange(0, 255, 256 // 16).tolist()
# image size
SIZE = (600, 800)
# create a new image
img = Image.new('L', SIZE, '#FFF')

today = date.today()
today = date(2022, 2, 1)
year = today.year
month = today.month

# get my schedule and holidays
events, event_days, holidays = Calendar.get_events(today)

draw = ImageDraw.Draw(img)

# show year
draw.multiline_text(
    (10, 10),
    str(year),
    fill=grey[2],
    font=get_font('en', 24)
)
# show month
draw.multiline_text(
    (padding_width(SIZE[0], today.strftime("%B"), 'title', 30), 18),
    today.strftime("%B"),
    fill=grey[1],
    font=get_font('title', 30)
)

draw.line(((10, 110), (SIZE[0] - 10, 110)), fill=grey[0], width=2)

# labels of weekday
days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
# get the date of this month
calendar_eu = calendar.monthcalendar(year, month)
formatted = [0]+list(itertools.chain.from_iterable(calendar_eu))[:-1]
calendar = np.array(formatted).reshape(-1, 7).tolist()

w_day = 600 // 7
x_start = np.arange(7) * w_day

# calendar
# show the label of weekday
for i, text in enumerate(days):
    w_pad = padding_width(w_day, text, 'en', 20)
    color = grey[8] if i % 6 == 0 else grey[2]
    draw.multiline_text((x_start[i] + w_pad, 120),
                        text, font=get_font('en', 20), fill=color)

draw.line(((10, 150), (SIZE[0] - 10, 150)), fill=grey[10], width=1)

# show the dates
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            continue
        w_pad = padding_width(w_day, str(text), 'en', 30)
        color = grey[8] if i % 6 == 0 or text in holidays else grey[0]
        draw.multiline_text((x_start[i] + w_pad, 170 + 60 * h),
                            str(text), font=get_font('en', 30), fill=color)
        if text in event_days:
            draw.line(((x_start[i] + (w_day - 10) // 2, 204 + 60 * h),
                       (x_start[i] + (w_day - 10) // 2 + 10, 204 + 60 * h)), fill=grey[4])

draw.line(((10, 470), (SIZE[0] - 10, 470)), fill=grey[1], width=2)

# show the schedule
for h, event in enumerate(events[:8]):
    text = f'{"/".join(event[1][0].split("-")[1:])}' \
        + f'{f"  {event[1][1][:5]}" if len(event[1]) != 1 else ""}  {event[0]}'
    draw.multiline_text((30, 480 + 30 * h),
                        text, font=get_font('ja', 20), fill=grey[2])
    draw.line(
        ((16, 500 + 30 * h), (SIZE[0] - 16, 500 + 30 * h)), fill=grey[10], width=1)

dt = datetime.now().isoformat(sep=' ')[:16].replace('-', '.')
draw.multiline_text((10, SIZE[1] - 30), f'Updated at {dt}',
                    font=get_font('en', 16), fill=grey[8])

# to bmp
file_name = './image_600x800.bmp'
img.save(file_name, 'bmp')
