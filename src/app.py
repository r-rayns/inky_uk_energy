import argparse
import http.server
import logging
import socketserver
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, TypedDict, Literal

import requests
import schedule
from PIL import Image, ImageDraw, ImageFont
from pytz import timezone

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Start the Inky UK Energy image generator.')
parser.add_argument('--server', action='store_true',
                    help='Hosts the generated image')
parser.add_argument('--port', type=int)

args = parser.parse_args()


class GenerationMix(TypedDict):
  fuel: str
  perc: float


# Use functional syntax because "from" is a reserved keyword
EnergyData = TypedDict('EnergyData', {
  'from': str,
  'to': str,
  'generationmix': List[GenerationMix]
})

valid_fuel_types = ['gas', 'wind', 'solar', 'hydro', 'biomass', 'coal', 'nuclear', 'other', 'imports']
file_path = Path(__file__).resolve()
assets_path = file_path.parent / "assets"

# Setup the logger
logger = logging.getLogger('inky_uk_energy')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
  '[%(asctime)s +0000] [%(process)d] [%(filename)s] [%(levelname)s] - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class EnergyDataImage:
  image: Image
  drawing: ImageDraw
  roboto_font: ImageFont
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
    self.roboto_font = ImageFont.truetype(assets_path / 'Roboto-Medium.ttf', 28)

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
    icon = Image.open(assets_path / f"{icon_name}.png")
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
      trending_icon = Image.open(assets_path / "trending-up.png")
    else:
      trending_icon = Image.open(assets_path / "trending-down.png")

    self.image.paste(trending_icon, (trending_x, trending_y))


def try_generate_energy_data_image():
  try:
    generate_energy_data_image()
  except Exception as err:
    logger.exception(err)
    logger.error(f"Error generating image: ${err}")


def generate_energy_data_image():
  now = datetime.now(timezone("Europe/London")).strftime('%Y-%m-%dT%H:%MZ')
  logger.info(f"Running image generation at {now}")

  res = requests.get("https://api.carbonintensity.org.uk/generation").json()
  latest_energy_data: EnergyData = res.get('data')
  generation_mix: List[GenerationMix] = sort_generation_mix(latest_energy_data.get('generationmix'))

  # Initialise the image
  energy_data_image = EnergyDataImage()

  # Draw the title
  energy_data_image.draw_title()

  # Draw the time range
  from_datetime = datetime.strptime(latest_energy_data.get('from'), '%Y-%m-%dT%H:%MZ')
  to_datetime = datetime.strptime(latest_energy_data.get('to'), '%Y-%m-%dT%H:%MZ')
  logger.info(f"Retrieved energy data from {from_datetime} to {to_datetime}")
  energy_data_image.draw_time_range(from_datetime, to_datetime)

  # Get the previous generation mix and assign percentage data by the related fuel type
  previous_generation_mix = get_previous_generation_mix(from_datetime, to_datetime)
  previous_mix_by_fuel = {mix.get('fuel'): mix.get('perc') for mix in previous_generation_mix}

  # Increments to multiple with the row and column numbers
  x_increment = 210
  y_increment = 110

  # Loop over the current generation mix
  for index, generation in enumerate(generation_mix):
    fuel = generation.get('fuel')
    if fuel in valid_fuel_types:
      # Calculate row and column - zero-indexed
      (row, col) = (index // 3, index % 3)
      # Calculate the increment to be added to the x and y offsets
      row_increment = x_increment * row
      col_increment = y_increment * col

      fuel = generation.get('fuel')
      percentage = generation.get('perc')
      previous_percentage = previous_mix_by_fuel.get(fuel)

      # Draw icon, fuel text and percentage text
      energy_data_image.draw_icon(row_increment, col_increment, fuel)
      energy_data_image.draw_fuel_text(row_increment, col_increment, fuel.capitalize())
      energy_data_image.draw_percentage_text(row_increment, col_increment, percentage)

      # Draw trending arrow (if percentage has changed)
      if percentage > previous_percentage:
        energy_data_image.draw_trend_arrow(row_increment, col_increment, "up")
      elif percentage < previous_percentage:
        energy_data_image.draw_trend_arrow(row_increment, col_increment, "down")

  energy_data_image.image.save('energy_data.png', 'PNG')


def sort_generation_mix(generation_mix: List[GenerationMix]) -> List[GenerationMix]:
  # Sort by percentage (high to low and then fuel type alphabetically)
  generation_mix.sort(key=lambda gen: (-gen.get('perc'), gen.get('fuel')))

  # Move the "other" fuel to then end of the list so it is always displayed last
  other_fuel = next((mix for mix in generation_mix if mix.get('fuel') == 'other'), None)
  if other_fuel:
    generation_mix.remove(other_fuel)
    generation_mix.append(other_fuel)

  return generation_mix


def get_previous_generation_mix(from_datetime: datetime, to_datetime: datetime) -> List[GenerationMix]:
  # Calculate the time range to retrieve the previous data
  # The API returns data in 30 minute intervals.
  # Subtract 29 minutes from "from" else the API will return data overlapping into an earlier interval.
  previous_from = (from_datetime - timedelta(minutes=29)).strftime('%Y-%m-%dT%H:%MZ')
  previous_to = (to_datetime - timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%MZ')
  res = requests.get(f"https://api.carbonintensity.org.uk/generation/{previous_from}/{previous_to}").json()
  logger.info(f"Retrieved previous energy data from {previous_from} to {previous_to}")

  previous_energy_data: EnergyData = res.get('data')[0]
  return previous_energy_data.get('generationmix')


class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path == '/energy_data.png':
      with open("energy_data.png", "rb") as f:
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(f.read())
    else:
      self.send_error(403, 'Forbidden')


def serve_image():
  port = args.port or 9000
  logger.info(f"Running server on port {port}")
  with socketserver.TCPServer(("", port), ImageRequestHandler) as httpd:
    httpd.serve_forever()


if __name__ == "__main__":
  if args.server:
    threading.Thread(target=serve_image, daemon=None).start()

  # Generate the energy data image and then schedule it to be updated every fifteen minutes from the hour
  try_generate_energy_data_image()
  schedule.every().hour.at(":00", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":15", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":30", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":45", timezone("Europe/London")).do(try_generate_energy_data_image)
  while True:
    schedule.run_pending()
    time.sleep(1)
