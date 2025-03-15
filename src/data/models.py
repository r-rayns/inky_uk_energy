from typing import TypedDict, List


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
