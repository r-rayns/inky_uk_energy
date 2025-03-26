from abc import ABC
from enum import Enum
from typing import TypedDict, List, Union


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


class CarbonIntensityIndex(str, Enum):
  VERY_LOW = "very low"
  LOW = "low"
  MODERATE = "moderate"
  HIGH = "high"
  VERY_HIGH = "very high"


class PhatColourPalette(str, Enum):
  RED = "red"
  YELLOW = "yellow"
  BLACK = "black"


class DisplayRange(str, Enum):
  PHAT = "pHAT"
  IMPRESSION = "Impression"


class DisplayType(str, Enum):
  PHAT_104_RED = "pHAT_104_red"
  PHAT_104_YELLOW = "pHAT_104_yellow"
  PHAT_104_BLACK = "pHAT_104_black"
  PHAT_122_RED = "pHAT_122_red"
  PHAT_122_YELLOW = "pHAT_122_yellow"
  PHAT_122_BLACK = "pHAT_122_black"
  IMPRESSION_4 = "IMPRESSION_4"
  IMPRESSION_5 = "IMPRESSION_5"
  IMPRESSION_7 = "IMPRESSION_7"


PHAT_104_DISPLAYS = Union[
  DisplayType.PHAT_104_RED,
  DisplayType.PHAT_104_YELLOW,
  DisplayType.PHAT_104_BLACK
]

PHAT_122_DISPLAYS = Union[
  DisplayType.PHAT_122_RED,
  DisplayType.PHAT_122_YELLOW,
  DisplayType.PHAT_122_BLACK
]


class InkyDisplay(ABC):
  range: DisplayRange
  type: DisplayType
  width: int
  height: int
  palette: None or PhatColourPalette


class PHAT104(InkyDisplay):
  range = DisplayRange.PHAT
  type: PHAT_104_DISPLAYS
  width: int = 212
  height: int = 104
  palette: PhatColourPalette

  def __init__(self, phat_104_type: PHAT_104_DISPLAYS):
    self.type = phat_104_type
    if phat_104_type == DisplayType.PHAT_104_RED:
      self.palette = PhatColourPalette.RED
    elif phat_104_type == DisplayType.PHAT_104_YELLOW:
      self.palette = PhatColourPalette.YELLOW
    elif phat_104_type == DisplayType.PHAT_104_BLACK:
      self.palette = PhatColourPalette.BLACK


class PHAT122(InkyDisplay):
  range = DisplayRange.PHAT
  type: PHAT_122_DISPLAYS
  width: int = 250
  height: int = 112
  palette: PhatColourPalette

  def __init__(self, phat_122_type: PHAT_122_DISPLAYS):
    self.type = phat_122_type
    if phat_122_type == DisplayType.PHAT_122_RED:
      self.palette = PhatColourPalette.RED
    elif phat_122_type == DisplayType.PHAT_122_YELLOW:
      self.palette = PhatColourPalette.YELLOW
    elif phat_122_type == DisplayType.PHAT_122_BLACK:
      self.palette = PhatColourPalette.BLACK


class IMPRESSION4(InkyDisplay):
  range = DisplayRange.IMPRESSION
  type: str = DisplayType.IMPRESSION_4
  width: int = 640
  height: int = 400
  palette = None


class IMPRESSION5(InkyDisplay):
  range = DisplayRange.IMPRESSION
  type: str = DisplayType.IMPRESSION_5
  width: int = 600
  height: int = 448
  palette = None


class IMPRESSION7(InkyDisplay):
  range = DisplayRange.IMPRESSION
  type: str = DisplayType.IMPRESSION_7
  width: int = 800
  height: int = 480
  palette = None
