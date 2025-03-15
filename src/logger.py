import logging

# Setup the logger
logger = logging.getLogger('inky_uk_energy')
logger.setLevel(logging.INFO)
# Setup formatting
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
  '[%(asctime)s +0000] [%(process)d] [%(filename)s] [%(levelname)s] - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
