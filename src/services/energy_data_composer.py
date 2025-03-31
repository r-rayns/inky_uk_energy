import os
import jinja2
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

import pytz

from src.logger import logger
from src.data.energy_data_client import EnergyDataClient
from src.data.models import EnergyData, GenerationMix, valid_fuel_types, PhatColourPalette


class EnergyDataComposer:
  file_path = Path(__file__).resolve()
  assets_path = file_path.parent.parent / "assets"
  root_dir = file_path.parent.parent.parent  # Root project directory
  styles_dir = root_dir / "src" / "templates" / "styles"
  base_css_path = styles_dir / "base.css"

  jinja_env: jinja2.Environment = None

  def __init__(self, jinja_env: jinja2.Environment):
    self.jinja_env = jinja_env

  def generate_html_for_impression(self) -> str:
    template_name = 'impression_template.html'
    logger.info(f"Generating HTML using template: {template_name}")

    template = self.jinja_env.get_template(template_name)

    # Get current and previous generation mix data
    generation_mix, from_datetime, to_datetime, previous_mix_by_fuel = self._get_current_and_previous_generation_mix()

    # Get the current carbon intensity index
    intensity_index = EnergyDataClient.current_carbon_intensity_index()

    # Get the past 24h energy data for the chart
    past_24h_energy_data = EnergyDataClient.past_24h_energy_data()

    svg_files = self.collate_svg_files()

    # Prepare template context
    context = {
      # Convert times to Europe/London timezone, as data is representative of the UK
      'from_time': from_datetime.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M'),
      'to_time': to_datetime.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M'),
      'date': to_datetime.strftime('%d-%b-%Y'),
      'top_row_generation_mix': generation_mix[:3],
      'middle_row_generation_mix': generation_mix[3:6],
      'bottom_row_generation_mix': generation_mix[6:],
      'previous_mix_by_fuel': previous_mix_by_fuel,
      'valid_fuel_types': valid_fuel_types,
      'intensity_index': intensity_index.replace(" ", "-").lower(),
      'intensity_index_label': intensity_index,
      'svg_files': svg_files,
      'past_24h_energy_data': past_24h_energy_data,
      'base_css': self.base_css_path.read_text()
    }

    ## Pass unpacked context to rendered
    return template.render(**context)

  def generate_html_for_phat(self, colour_palette: PhatColourPalette) -> str:
    template_name = 'phat_template.html'
    logger.info(f"Generating HTML using template: {template_name}")

    template = self.jinja_env.get_template(template_name)

    # Get current and previous generation mix data
    generation_mix, from_datetime, to_datetime, previous_mix_by_fuel = self._get_current_and_previous_generation_mix()

    # Get the current carbon intensity index
    intensity_index = EnergyDataClient.current_carbon_intensity_index()

    svg_files = self.collate_svg_files()

    # Prepare template context
    context = {
      # Convert times to Europe/London timezone, as data is representative of the UK
      'from_time': from_datetime.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M'),
      'to_time': to_datetime.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M'),
      'date': to_datetime.strftime('%d-%b-%Y'),
      'top_row_generation_mix': generation_mix[:3],
      'middle_row_generation_mix': generation_mix[3:6],
      'bottom_row_generation_mix': generation_mix[6:],
      'previous_mix_by_fuel': previous_mix_by_fuel,
      'valid_fuel_types': valid_fuel_types,
      'intensity_index': intensity_index.replace(" ", "-").lower(),
      'intensity_index_label': intensity_index,
      'svg_files': svg_files,
      'base_css': self.base_css_path.read_text(),
      'colour_palette': colour_palette
    }

    ## Pass unpacked context to rendered
    return template.render(**context)

  @staticmethod
  def _get_current_and_previous_generation_mix() -> Tuple[List[GenerationMix], datetime, datetime, Dict[str, float]]:
    # Retrieve the latest energy data
    latest_energy_data: EnergyData = EnergyDataClient.current_energy_data(sort_generation_mix=True)

    # Extract the generation mix and time range
    generation_mix: List[GenerationMix] = latest_energy_data.get('generationmix')
    from_datetime_utc = (datetime
                         .strptime(latest_energy_data.get('from'), '%Y-%m-%dT%H:%MZ')
                         .replace(tzinfo=pytz.utc))  # ensure datetime is in UTC
    to_datetime_utc = (datetime
                       .strptime(latest_energy_data.get('to'), '%Y-%m-%dT%H:%MZ')
                       .replace(tzinfo=pytz.utc))  # ensure datetime is in UTC

    # Get the previous generation mix and assign percentage data by the related fuel type
    previous_energy_data = EnergyDataClient.previous_energy_data(from_datetime_utc, to_datetime_utc,
                                                                 sort_generation_mix=False)
    previous_generation_mix: List[GenerationMix] = previous_energy_data.get('generationmix')
    previous_mix_by_fuel = {mix.get('fuel'): mix.get('perc') for mix in previous_generation_mix}

    return generation_mix, from_datetime_utc, to_datetime_utc, previous_mix_by_fuel

  def collate_svg_files(self) -> dict:
    # Read all SVG files in the directory so they can be passed to the template in the context
    svg_path = self.assets_path / "svg"
    svg_files = {}
    for filename in os.listdir(svg_path):
      if filename.endswith('.svg'):
        svg_file_path = os.path.join(svg_path, filename)
        with open(svg_file_path, 'r') as svg:
          # Store the contents of each SVG file using its name as the key
          key = filename.replace('.svg', '')
          svg_files[key] = svg.read()

    return svg_files
