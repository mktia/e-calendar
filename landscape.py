# -*- coding: utf-8 -*-

import calendar as cal
from datetime import date, datetime
import itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from connect_calendar import Calendar


def get_calendar(year: int, month: int):
    calendar_eu = cal.monthcalendar(year, month)
    formatted = [0]+list(itertools.chain.from_iterable(calendar_eu))[:-1]
    return np.array(formatted).reshape(-1, 7).tolist()


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


font_files = dict(
    en='./Fonts/Marcellus-Regular.ttf',
    ja='./Fonts/NotoSansJP-Regular.otf',
    num='./Fonts/Cardo-Regular.ttf',
    title='./Fonts/PinyonScript-Regular.ttf'
)
# color scale
COLOR = dict(
    black=(0, 0, 0),
    red=(256, 0, 0),
    white=(255, 255, 255)
)
# image size
SIZE = (880, 528)
MAIN_WIDTH = 560
# create a new image
img = Image.new('RGB', SIZE, COLOR['white'])

today = date.today()
year = today.year
month = today.month

# get my schedule and holidays
events, event_days, holidays = Calendar.get_events(today)

draw = ImageDraw.Draw(img)

# show year
draw.multiline_text(
    (10, 10), str(year), fill=COLOR['black'], font=get_font('num', 24)
)
# show month
draw.multiline_text(
    (padding_width(MAIN_WIDTH, today.strftime("%B"), 'title', 60), 20),
    today.strftime("%B"),
    fill=COLOR['black'],
    font=get_font('title', 60)
)

draw.line(((10, 110), (MAIN_WIDTH - 10, 110)),
          fill=COLOR['black'], width=2)

# labels of weekday
weekday = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
weekday_s = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

# this month
# get the calendar of this month
calendar = get_calendar(year, month)

w_day = MAIN_WIDTH // 7
x_start = np.arange(7) * w_day

# show the label of weekday
for i, text in enumerate(weekday):
    w_pad = padding_width(w_day, text, 'en', 20)
    color = COLOR['red'] if i == 0 else COLOR['black']
    draw.multiline_text((x_start[i] + w_pad, 120),
                        text, font=get_font('en', 20), fill=color)

draw.line(((10, 150), (MAIN_WIDTH - 10, 150)), fill=COLOR['black'], width=1)

# show the dates
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            continue
        w_pad = padding_width(w_day, str(text), 'num', 30)
        color = COLOR['red'] if i == 0 or text in holidays else COLOR['black']
        draw.multiline_text((x_start[i] + w_pad, 170 + 52 * h),
                            str(text), font=get_font('num', 30), fill=color)
        if text in event_days:
            draw.line(((x_start[i] + (w_day - 12) // 2, 204 + 52 * h),
                       (x_start[i] + (w_day - 12) // 2 + 12, 204 + 52 * h)), fill=COLOR['black'])

# a boundary between calendar and schedule
draw.line(
    ((MAIN_WIDTH, 0), (MAIN_WIDTH, SIZE[1])),
    fill=COLOR['black'],
    width=1
)
draw.line(
    ((MAIN_WIDTH + 2, 0), (MAIN_WIDTH + 2, SIZE[1])),
    fill=COLOR['black'],
    width=1
)

# show the schedule
event_count = 8
for h, event in enumerate(events[:event_count]):
    dt = "/".join([str(int(i)) for i in event[1][0].split("-")[1:]])
    text = f'{dt + "  " * ( 5 - len(dt))}' \
        + f'{f" {event[1][1][:5]}" if len(event[1]) != 1 else ""}' \
        + f' {event[0] if len(event[0]) < 14 else event[0][:10] + "…"}'
    draw.multiline_text((MAIN_WIDTH + 10, 6 + 30 * h),
                        text, font=get_font('ja', 18), fill=COLOR['black'])
    if 0 < h < 8:
        draw.line(
            ((MAIN_WIDTH + 16, 6 + 30 * h), (SIZE[0] - 16, 6 + 30 * h)),
            fill=COLOR['black'],
            width=1
        )

# a boundary between schedule and sub calendar
# draw.line(
#     ((MAIN_WIDTH, 6 + 30 * 8), (SIZE[0], 6 + 30 * 8)),
#     fill=COLOR['black'],
#     width=1
# )
# draw.line(
#     ((MAIN_WIDTH, 8 + 30 * 8), (SIZE[0], 8 + 30 * 8)),
#     fill=COLOR['black'],
#     width=1
# )

dt = datetime.now().isoformat(sep=' ')[:16].replace('-', '.')
draw.multiline_text((10, SIZE[1] - 30), f'Updated at {dt}',
                    font=get_font('en', 16), fill=COLOR['black'])

# next month
# get the calendar of next month
year, month = [year, month + 1] if month < 12 else [year + 1, 1]
calendar = get_calendar(year, month)
_, _, holidays = Calendar.get_events(date(year, month, 1))

w_day = (SIZE[0] - MAIN_WIDTH) // 7
x_start = np.arange(7) * w_day + MAIN_WIDTH


draw.multiline_text(
    (padding_width(SIZE[0] - MAIN_WIDTH,
                   str(month), 'title', 30) + MAIN_WIDTH, 270),
    str(month),
    fill=COLOR['black'],
    font=get_font('title', 30)
)

for i, text in enumerate(weekday_s):
    w_pad = padding_width(w_day, text, 'en', 16)
    color = COLOR['red'] if i == 0 else COLOR['black']
    draw.multiline_text((x_start[i] + w_pad, 310),
                        text, font=get_font('en', 16), fill=color)

# show the dates
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            continue
        w_pad = padding_width(w_day, str(text), 'num', 24)
        color = COLOR['red'] if i == 0 or text in holidays else COLOR['black']
        draw.multiline_text((x_start[i] + w_pad, 340 + 30 * h),
                            str(text), font=get_font('num', 24), fill=color)

# to bmp
file_name = './demo_880x528.bmp'
img.save(file_name, 'bmp')
