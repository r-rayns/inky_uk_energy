import argparse
import threading
import time
from pathlib import Path

import jinja2
import schedule
from pytz import timezone

from src.data.models import DisplayRange
from src.logger import logger
from src.server.image_server import serve_image
from src.services.energy_data_composer import EnergyDataComposer
from src.utils.env_loader import env
from src.utils.screenshot_capture import ScreenshotCapture

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Start the Inky UK Energy image generator.')
parser.add_argument('--server', action='store_true',
                    help='Hosts the generated image')
parser.add_argument('--port', type=int)

args = parser.parse_args()

# Form paths
root_dir = Path(__file__).resolve().parent.parent  # Root project directory
template_dir = root_dir / "src" / "templates"

# Setup Jinja2 environment
jinja_env: jinja2.Environment = jinja2.Environment(
  loader=jinja2.FileSystemLoader(template_dir),
  autoescape=jinja2.select_autoescape(['html', 'xml']),
)


def try_generate_energy_data_image(file_name: str = 'energy_data'):
  try:
    energy_data_composer = EnergyDataComposer(jinja_env)
    for display in env.active_displays:
      logger.info(f"Generating image for {display.type}")

      if display.range is DisplayRange.IMPRESSION:
        energy_data_html = energy_data_composer.generate_html_for_impression()
      else:
        energy_data_html = energy_data_composer.generate_html_for_phat(display.palette)
      # Save HTML content to a file
      with open(f'{root_dir}/generated_html/{file_name}_{display.type.lower()}.html', 'w') as f:
        f.write(energy_data_html)
      logger.info(f"HTML for {display.type} saved")

      ScreenshotCapture.take_screenshot(f'{root_dir}/generated_html/{file_name}_{display.type.lower()}.html',
                                        f'{root_dir}/screenshots/{file_name}_{display.type.lower()}.png',
                                        display.width, display.height)

  except Exception as err:
    logger.exception(err)
    logger.error(f"Error generating image: ${err}")


if __name__ == "__main__":
  if args.server:
    threading.Thread(target=lambda: serve_image(args.port), daemon=None).start()

  # Generate the energy data images and then schedule them to be updated every fifteen minutes from the hour
  try_generate_energy_data_image()
  schedule.every().hour.at(":00", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":15", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":30", timezone("Europe/London")).do(try_generate_energy_data_image)
  schedule.every().hour.at(":45", timezone("Europe/London")).do(try_generate_energy_data_image)
  while True:
    schedule.run_pending()
    time.sleep(1)
