import os

from playwright.sync_api import sync_playwright

from src.logger import logger


class ScreenshotCapture:
  def __init__(self):
    pass

  @staticmethod
  def take_screenshot(html_file_path: str, output_path: str, viewport_width: int, viewport_height: int):
    with sync_playwright() as playwright:
      logger.info(f"Taking screenshot of {html_file_path} with viewport size {viewport_width}x{viewport_height}")
      # Launch the browser
      browser = playwright.chromium.launch(headless=True)
      page = browser.new_page()
      page.set_viewport_size({"width": viewport_width, "height": viewport_height})
      # Navigate to the HTML file
      page.goto(f'file://{os.path.abspath(html_file_path)}')
      # Take a screenshot
      page.screenshot(path=output_path)
      logger.info(f"Screenshot saved to {output_path}")
      # Close the browser
      browser.close()
