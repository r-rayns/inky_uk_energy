from typing import List

import requests
from datetime import datetime, timedelta
from pytz import timezone

from src.data.models import EnergyData, GenerationMix, CarbonIntensityIndex
from src.logger import logger


class EnergyDataClient:
  def __init__(self):
    pass

  @staticmethod
  def current_energy_data(sort_generation_mix=True) -> EnergyData:
    res = requests.get("https://api.carbonintensity.org.uk/generation").json()
    latest_energy_data: EnergyData = res.get('data')
    if sort_generation_mix:
      latest_energy_data['generationmix'] = EnergyDataClient.sort_generation_mix(
        latest_energy_data.get('generationmix'))

    return latest_energy_data

  @staticmethod
  def previous_energy_data(from_datetime: datetime, to_datetime: datetime, sort_generation_mix=True) -> EnergyData:
    # Calculate the time range to retrieve the previous data
    # The API returns data in 30 minute intervals.
    # Subtract 29 minutes from "from" else the API will return data overlapping into an earlier interval.
    previous_from = (from_datetime - timedelta(minutes=29)).strftime('%Y-%m-%dT%H:%MZ')
    previous_to = (to_datetime - timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%MZ')
    res = requests.get(f"https://api.carbonintensity.org.uk/generation/{previous_from}/{previous_to}").json()
    logger.info(f"Retrieved previous energy data from {previous_from} to {previous_to}")
    previous_energy_data: EnergyData = res.get('data')[0]
    if sort_generation_mix:
      previous_energy_data['generationmix'] = EnergyDataClient.sort_generation_mix(
        previous_energy_data.get('generationmix'))

    return previous_energy_data

  @staticmethod
  def sort_generation_mix(generation_mix: List[GenerationMix]) -> List[GenerationMix]:
    # Sort by percentage (high to low and then fuel type alphabetically)
    generation_mix.sort(key=lambda gen: (-gen.get('perc'), gen.get('fuel')))

    # Move the "other" fuel to then end of the list so it is always displayed last
    other_fuel = next((mix for mix in generation_mix if mix.get('fuel') == 'other'), None)
    if other_fuel:
      generation_mix.remove(other_fuel)
      generation_mix.append(other_fuel)

    return generation_mix

  @staticmethod
  def current_carbon_intensity_index() -> CarbonIntensityIndex:
    res = requests.get("https://api.carbonintensity.org.uk/intensity").json()
    intensity_data = res.get('data')[0]
    return intensity_data.get('intensity').get('index')

  @staticmethod
  def past_24h_energy_data() -> List[EnergyData]:
    now = datetime.now(timezone("Europe/London")).strftime('%Y-%m-%dT%H:%MZ')
    res = requests.get(f"https://api.carbonintensity.org.uk/generation/{now}/pt24h").json()
    past_energy_data = res.get('data')

    return past_energy_data


  # TODO expand with retrieval of past 24h energy intensity data: https://api.carbonintensity.org.uk/intensity/2025-03-19T08:33Z/pt24h
