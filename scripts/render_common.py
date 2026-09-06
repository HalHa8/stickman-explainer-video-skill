#!/usr/bin/env python3
"""Scalable primitives that keep content inside the platform-safe center region."""

import math
from PIL import Image, ImageDraw, ImageFont


class Canvas:
    def __init__(
        self,
        width=1440,
        height=2560,
        safe_top=0.10,
        background="#FFFFFF",
        safe_right=0.20,
        safe_bottom=0.20,
    ):
        self.width = int(width)
        self.height = int(height)
        self.safe_top = int(self.height * safe_top)
        self.safe_right = int(self.width * safe_right)
        self.safe_bottom = int(self.height * safe_bottom)
        self.safe_left = 0
        self.background = background
        self.content_left = self.safe_left
        self.content_top = self.safe_top
        self.content_right = self.width - self.safe_right
        self.content_bottom = self.height - self.safe_bottom
        self.content_width = self.content_right - self.content_left
        self.content_height = self.content_bottom - self.content_top
        if self.content_width <= 0 or self.content_height <= 0:
            raise ValueError("Platform safe areas leave no drawable content region")
        self.image = Image.new("RGB", (self.width, self.height), background)
        self.draw = ImageDraw.Draw(self.image)
        self.scale = min(self.content_width / 720, self.content_height / 1280)
        self.offset_x = self.content_left + (self.content_width - 720 * self.scale) / 2
        self.offset_y = self.content_top + (self.content_height - 1280 * self.scale) / 2

    @property
    def content_bounds(self):
        """Physical pixel bounds available for animation and on-screen text."""
        return (self.content_left, self.content_top, self.content_right, self.content_bottom)

    @classmethod
    def from_video_config(cls, video):
        """Create a canvas that applies every configured platform-safe boundary."""
        return cls(
            video["width"],
            video["height"],
            video.get("safe_area_top", 0.10),
            video.get("background", "#FFFFFF"),
            video.get("safe_area_right", 0.20),
            video.get("safe_area_bottom", 0.20),
        )

    def point(self, x, y):
        return self.offset_x + x * self.scale, self.offset_y + y * self.scale

    def length(self, value):
        return max(1, round(value * self.scale))

    def line(self, points, fill, width=6):
        mapped = [self.point(x, y) for x, y in points]
        self.draw.line(mapped, fill=fill, width=self.length(width), joint="curve")

    def ellipse(self, box, fill=None, outline=None, width=4):
        x0, y0 = self.point(box[0], box[1])
        x1, y1 = self.point(box[2], box[3])
        self.draw.ellipse((x0, y0, x1, y1), fill=fill, outline=outline, width=self.length(width))

    def rounded_rectangle(self, box, radius=20, fill=None, outline=None, width=4):
        x0, y0 = self.point(box[0], box[1])
        x1, y1 = self.point(box[2], box[3])
        self.draw.rounded_rectangle(
            (x0, y0, x1, y1), radius=self.length(radius), fill=fill,
            outline=outline, width=self.length(width),
        )

    def arrow(self, start, end, color="#1296A5", width=6):
        self.line((start, end), color, width)
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        head = 16
        p1 = (end[0] - head * math.cos(angle - 0.55), end[1] - head * math.sin(angle - 0.55))
        p2 = (end[0] - head * math.cos(angle + 0.55), end[1] - head * math.sin(angle + 0.55))
        self.draw.polygon([self.point(*end), self.point(*p1), self.point(*p2)], fill=color)

    def stickman(self, cx, base, color="#1658D8", scale=1.0, headband=False):
        s = scale
        head = (cx, base - 190 * s)
        shoulder = (cx, base - 145 * s)
        hip = (cx, base - 72 * s)
        joints = {
            "left_elbow": (cx - 34 * s, base - 116 * s),
            "left_hand": (cx - 42 * s, base - 78 * s),
            "right_elbow": (cx + 34 * s, base - 116 * s),
            "right_hand": (cx + 48 * s, base - 86 * s),
            "left_knee": (cx - 28 * s, base - 35 * s),
            "left_foot": (cx - 45 * s, base),
            "right_knee": (cx + 28 * s, base - 35 * s),
            "right_foot": (cx + 45 * s, base),
        }
        radius = 33 * s
        self.ellipse((head[0] - radius, head[1] - radius, head[0] + radius, head[1] + radius), self.background, color, 8 * s)
        self.line((shoulder, hip), color, 10 * s)
        self.line((shoulder, joints["left_elbow"], joints["left_hand"]), color, 10 * s)
        self.line((shoulder, joints["right_elbow"], joints["right_hand"]), color, 10 * s)
        self.line((hip, joints["left_knee"], joints["left_foot"]), color, 10 * s)
        self.line((hip, joints["right_knee"], joints["right_foot"]), color, 10 * s)
        if headband:
            self.line(((head[0] - 28 * s, head[1] - 15 * s), (head[0] + 28 * s, head[1] - 15 * s)), color, 7 * s)

    def text_pill(self, center, text, font_path, color="#1658D8", fill="#FFFFFF", font_size=44, max_width=620):
        size = font_size
        while size > 20:
            font = ImageFont.truetype(font_path, self.length(size))
            box = self.draw.textbbox((0, 0), text, font=font)
            if box[2] - box[0] <= self.length(max_width - 48):
                break
            size -= 1
        cx, cy = self.point(*center)
        padding_x = self.length(24)
        padding_y = self.length(14)
        width = box[2] - box[0] + 2 * padding_x
        height = box[3] - box[1] + 2 * padding_y
        self.draw.rounded_rectangle(
            (cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2),
            radius=self.length(20), fill=fill, outline=color, width=self.length(4),
        )
        self.draw.text((cx, cy), text, font=font, fill=color, anchor="mm")

    def save(self, path):
        self.image.save(path)
