# -*- coding: utf-8 -*-

import calendar as cal
from datetime import date, datetime
import itertools
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import logging
from lib import epd7in5b_HD
from connect_calendar import Calendar


def get_calendar(year: int, month: int):
    calendar_eu = cal.monthcalendar(year, month)
    formatted = [0]+list(itertools.chain.from_iterable(calendar_eu))[:-1]
    return np.array(formatted).reshape(-1, 7).tolist()


def get_font(font_symbol: str, font_size: int):
    return ImageFont.truetype(font_files[font_symbol], font_size)


def get_width(text: str, font_symbol: str, font_size: int):
    bbox = draw_b.multiline_textbbox(
        (0, 0), text,
        font=get_font(font_symbol, font_size)
    )
    return bbox[2] - bbox[0]


def padding_width(width: int, text: str, font_symbol: str, font_size: int):
    return (width - get_width(text, font_symbol, font_size)) // 2


logging.basicConfig(level=logging.DEBUG)

epd = epd7in5b_HD.EPD()

logging.info('init and Clear')
epd.init()
epd.Clear()

font_files = dict(
    en='./Fonts/HindMadurai-SemiBold.ttf',
    ja='./Fonts/NotoSansJP-Medium.otf',
    num='./Fonts/Cardo-Bold.ttf',
    title='./Fonts/Tangerine-Bold.ttf'
)
# color scale
COLOR = dict(
    black=0,
    red=0,
    white=1
)
# image size
SIZE = (880, 528)
MAIN_WIDTH = 560
# create a new image
img_b = Image.new('1', SIZE, COLOR['white'])
img_r = Image.new('1', SIZE, COLOR['white'])

today = date.today()
year = today.year
month = today.month

# get my schedule and holidays
events, event_days, holidays = Calendar.get_events(today)

draw_b = ImageDraw.Draw(img_b)
draw_r = ImageDraw.Draw(img_r)

# show year
draw_b.multiline_text(
    (10, 10), str(year), fill=COLOR['black'], font=get_font('num', 26)
)
# show month
draw_b.multiline_text(
    (padding_width(MAIN_WIDTH, today.strftime("%B"), 'title', 68), 28),
    today.strftime("%B"),
    fill=COLOR['black'],
    font=get_font('title', 68)
)

draw_b.line(((10, 110), (MAIN_WIDTH - 10, 110)),
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
    if i == 0:
        draw_r.multiline_text((x_start[i] + w_pad, 120),
                              text, font=get_font('en', 20), fill=COLOR['red'])
    else:
        draw_b.multiline_text((x_start[i] + w_pad, 120),
                              text, font=get_font('en', 20), fill=COLOR['black'])


draw_b.line(((10, 150), (MAIN_WIDTH - 10, 150)), fill=COLOR['black'], width=1)

# show the dates
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            continue
        w_pad = padding_width(w_day, str(text), 'num', 30)
        if i == 0 or text in holidays:
            draw_r.multiline_text((x_start[i] + w_pad, 170 + 52 * h),
                                  str(text), font=get_font('num', 30), fill=COLOR['red'])
        else:
            draw_b.multiline_text((x_start[i] + w_pad, 170 + 52 * h),
                                  str(text), font=get_font('num', 30), fill=COLOR['black'])
        if text in event_days:
            draw_b.line(((x_start[i] + (w_day - 12) // 2, 204 + 52 * h),
                         (x_start[i] + (w_day - 12) // 2 + 12, 204 + 52 * h)), fill=COLOR['black'])

# a boundary between calendar and schedule
draw_b.line(
    ((MAIN_WIDTH, 0), (MAIN_WIDTH, SIZE[1])),
    fill=COLOR['black'],
    width=1
)
draw_b.line(
    ((MAIN_WIDTH + 2, 0), (MAIN_WIDTH + 2, SIZE[1])),
    fill=COLOR['black'],
    width=1
)

# show the schedule
event_count = 8
for h, event in enumerate(events[:event_count]):
    dt = ".".join([str(int(i)) for i in event[1][0].split("-")[1:]])
    # show the time of schedule
    if len(event[1]) != 1:
        content = event[0][:8] + ('' if len(event[0]) < 9 else "…")
    else:
        content = event[0][:11] + ('' if len(event[0]) < 12 else "…")
    text = f'{dt + "  " * ( 5 - len(dt))}' \
        + f'{f" {event[1][1][:5]}" if len(event[1]) != 1 else ""}' \
        + f' {content}'
    if 'TODO' in content:
        draw_r.multiline_text((MAIN_WIDTH + 10, 6 + 32 * h),
                            text, font=get_font('ja', 20), fill=COLOR['red'])
    else:
        draw_b.multiline_text((MAIN_WIDTH + 10, 6 + 32 * h),
                            text, font=get_font('ja', 20), fill=COLOR['black'])
    if 0 < h < 8:
        draw_b.line(
            ((MAIN_WIDTH + 16, 6 + 32 * h), (SIZE[0] - 16, 6 + 32 * h)),
            fill=COLOR['black'],
            width=1
        )

dt = datetime.now().isoformat(sep=' ')[:16].replace('-', '.')
draw_b.multiline_text((10, SIZE[1] - 30), f'Updated at {dt}',
                      font=get_font('en', 16), fill=COLOR['black'])

# next month
# get the calendar of next month
year, month = [year, month + 1] if month < 12 else [year + 1, 1]
calendar = get_calendar(year, month)

w_day = (SIZE[0] - MAIN_WIDTH - 2) // 7
x_start = np.arange(7) * w_day + MAIN_WIDTH + 2

draw_b.multiline_text(
    (padding_width(SIZE[0] - MAIN_WIDTH,
                   str(month), 'title', 40) + MAIN_WIDTH, 276),
    str(month),
    fill=COLOR['black'],
    font=get_font('title', 40)
)

for i, text in enumerate(weekday_s):
    w_pad = padding_width(w_day, text, 'en', 16)
    if i == 0:
        draw_r.multiline_text((x_start[i] + w_pad, 314),
                              text, font=get_font('en', 16), fill=COLOR['red'])
    else:
        draw_b.multiline_text((x_start[i] + w_pad, 314),
                              text, font=get_font('en', 16), fill=COLOR['black'])

# show the dates
for h, row in enumerate(calendar):
    for i, text in enumerate(row):
        if text == 0:
            continue
        w_pad = padding_width(w_day, str(text), 'num', 26)
        if i == 0 or text in holidays:
            draw_r.multiline_text((x_start[i] + w_pad, 340 + 30 * h),
                                  str(text), font=get_font('num', 26), fill=COLOR['red'])
        else:
            draw_b.multiline_text((x_start[i] + w_pad, 340 + 30 * h),
                                  str(text), font=get_font('num', 26), fill=COLOR['black'])

# show the calendar on e-paper
epd.display(epd.getbuffer(img_b), epd.getbuffer(img_r))
epd.sleep()

# save an image for test
img_b.save('image_b.bmp', 'bmp')
img_r.save('image_r.bmp', 'bmp')
