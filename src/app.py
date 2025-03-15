import argparse
import threading
import time
from datetime import datetime
from typing import List
from src.logger import logger
from src.energy_data_image import EnergyDataImage
from src.data.models import EnergyData, GenerationMix, valid_fuel_types
from src.data.energy_data_client import EnergyDataClient
from src.server.image_server import serve_image
from pytz import timezone
import schedule

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Start the Inky UK Energy image generator.')
parser.add_argument('--server', action='store_true',
                    help='Hosts the generated image')
parser.add_argument('--port', type=int)

args = parser.parse_args()


def try_generate_energy_data_image():
  try:
    generate_energy_data_image()
  except Exception as err:
    logger.exception(err)
    logger.error(f"Error generating image: ${err}")


def generate_energy_data_image():
  now = datetime.now(timezone("Europe/London")).strftime('%Y-%m-%dT%H:%MZ')
  logger.info(f"Running image generation at {now}")

  latest_energy_data: EnergyData = EnergyDataClient.current_energy_data(sort_generation_mix=True)
  generation_mix: List[GenerationMix] = latest_energy_data.get('generationmix')

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
  previous_energy_data = EnergyDataClient.previous_energy_data(from_datetime, to_datetime, sort_generation_mix=False)
  previous_generation_mix = previous_energy_data.get('generationmix')
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


if __name__ == "__main__":
  if args.server:
    threading.Thread(target=lambda: serve_image(args.port), daemon=None).start()

  # Generate the energy data image and then schedule it to be updated every fifteen minutes from the hour
  try_generate_energy_data_image()
  schedule.every().hour.at(":00", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":15", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":30", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":45", timezone("Europe/London")).do(try_generate_energy_data_image)
  while True:
    schedule.run_pending()
    time.sleep(1)
