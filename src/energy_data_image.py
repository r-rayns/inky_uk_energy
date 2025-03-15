from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from typing import Literal

class EnergyDataImage:
  image: Image
  drawing: ImageDraw
  roboto_font: ImageFont
  file_path = Path(__file__).resolve()
  assets_path = file_path.parent / "assets"
  # 0.5 saturation inky impression palette
  impression_palette = [
    28, 24, 28,  # black
    255, 255, 255,  # white
    29, 173, 35,  # green
    30, 29, 174,  # blue
    205, 36, 37,  # red
    231, 222, 35,  # yellow
    216, 123, 36,  # orange
    255, 255, 255  # white (clear)
  ]

  def __init__(self):
    self.image = Image.new('P', (640, 400), 1)  # (1 is white in our palette)
    self.image.putpalette(self.impression_palette)
    self.drawing = ImageDraw.Draw(self.image)
    self.roboto_font = ImageFont.truetype(self.assets_path / 'Roboto-Medium.ttf', 28)

  def draw_title(self):
    title = "UK Energy Mix"
    title_font = self.roboto_font.font_variant(size=30)
    self.drawing.text((223, 4), title, font=title_font)

  def draw_time_range(self, from_datetime: datetime, to_datetime: datetime):
    time_text = f"{from_datetime.strftime('%H:%M')}-{to_datetime.strftime('%H:%M')} {to_datetime.strftime('%d-%b-%Y')}"
    time_text_font = self.roboto_font.font_variant(size=24)
    self.drawing.text((167, 35), time_text, font=time_text_font)

  def draw_icon(self, row_increment: int, col_increment: int, icon_name: str):
    icon_x_offset = 30
    icon_y_offset = 80
    icon = Image.open(self.assets_path / f"{icon_name}.png")
    icon_x = icon_x_offset + row_increment
    icon_y = icon_y_offset + col_increment
    self.image.paste(icon, (icon_x, icon_y))

  def draw_fuel_text(self, row_increment: int, col_increment: int, fuel: str):
    fuel_text_x_offset = 90
    fuel_text_y_offset = 75
    fuel_text_x = fuel_text_x_offset + row_increment
    fuel_text_y = fuel_text_y_offset + col_increment
    self.drawing.text((fuel_text_x, fuel_text_y), fuel.capitalize(), font=self.roboto_font)

  def draw_percentage_text(self, row_increment: int, col_increment: int, percentage: float):
    percentage_text_x_offset = 90
    percentage_text_y_offset = 105
    percentage = f"{percentage}%"
    percentage_text_x = percentage_text_x_offset + row_increment
    percentage_text_y = percentage_text_y_offset + col_increment
    self.drawing.text((percentage_text_x, percentage_text_y), percentage, font=self.roboto_font)

  def draw_trend_arrow(self, row_increment: int, col_increment: int, trend: Literal["up", "down"]):
    trending_x_offset = 170
    trending_y_offset = 108
    trending_x = trending_x_offset + row_increment
    trending_y = trending_y_offset + col_increment
    if trend == "up":
      trending_icon = Image.open(self.assets_path / "trending-up.png")
    else:
      trending_icon = Image.open(self.assets_path / "trending-down.png")

    self.image.paste(trending_icon, (trending_x, trending_y))
