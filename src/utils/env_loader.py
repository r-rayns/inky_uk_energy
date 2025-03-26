import os

from dotenv import load_dotenv

from src.data.models import DisplayType, PHAT104, PHAT122, IMPRESSION4, IMPRESSION5, IMPRESSION7, \
  InkyDisplay
from src.logger import logger

# Load environment variables from the .env file
load_dotenv()


class EnvConfig:
  active_displays: list[InkyDisplay]

  def __init__(self, active_displays):
    self.active_displays = active_displays


def validate_env():
  displays = {
    DisplayType.PHAT_104_RED: os.getenv(DisplayType.PHAT_104_RED.value) == "true",
    DisplayType.PHAT_104_YELLOW: os.getenv(DisplayType.PHAT_104_YELLOW.value) == "true",
    DisplayType.PHAT_104_BLACK: os.getenv(DisplayType.PHAT_104_BLACK.value) == "true",
    DisplayType.PHAT_122_RED: os.getenv(DisplayType.PHAT_122_RED.value) == "true",
    DisplayType.PHAT_122_YELLOW: os.getenv(DisplayType.PHAT_122_YELLOW.value) == "true",
    DisplayType.PHAT_122_BLACK: os.getenv(DisplayType.PHAT_122_BLACK.value) == "true",
    DisplayType.IMPRESSION_4: os.getenv(DisplayType.IMPRESSION_4.value) == "true",
    DisplayType.IMPRESSION_5: os.getenv(DisplayType.IMPRESSION_5.value) == "true",
    DisplayType.IMPRESSION_7: os.getenv(DisplayType.IMPRESSION_7.value) == "true",
  }

  env_config = EnvConfig(
    active_displays=[]
  )

  toggled_display_types = [display.value for display, is_active in displays.items() if is_active == True]

  if not toggled_display_types:
    raise ValueError(
      f"You must set one of the following displays to true: {', '.join(displays.keys())} in your .env file.")

  logger.info(f"Toggled displays: {toggled_display_types}")

  # Instantiate the corresponding display class for each toggled display
  for display in toggled_display_types:
    if (display == DisplayType.PHAT_104_BLACK
      or display == DisplayType.PHAT_104_YELLOW
      or display == DisplayType.PHAT_104_RED):
      env_config.active_displays.append(PHAT104(display))
    elif (display == DisplayType.PHAT_122_BLACK
          or display == DisplayType.PHAT_122_YELLOW
          or display == DisplayType.PHAT_122_RED):
      env_config.active_displays.append(PHAT122(display))
    elif display == DisplayType.IMPRESSION_4:
      env_config.active_displays.append(IMPRESSION4())
    elif display == DisplayType.IMPRESSION_5:
      env_config.active_displays.append(IMPRESSION5())
    elif display == DisplayType.IMPRESSION_7:
      env_config.active_displays.append(IMPRESSION7())

  return env_config


try:
  env = validate_env()
except ValueError as e:
  logger.error(str(e))
  exit(1)
