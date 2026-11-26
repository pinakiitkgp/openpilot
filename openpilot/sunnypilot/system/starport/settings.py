"""Persistent settings helpers for StarPort & CarPlay Live View."""
from __future__ import annotations

from dataclasses import dataclass

PARAM_ENABLED = "StarPortEnabled"
PARAM_HEADUNITPAD_MODE = "StarPortHeadunitPadMode"
PARAM_ALLOW_OFFROAD = "StarPortAllowOffroad"
PARAM_VIDEO_SOURCE = "StarPortVideoSource"
PARAM_PORT = "StarPortPort"

DEFAULT_PORT = 5277
VIDEO_SOURCES = {
  0: "livestreamNarrowRoadEncodeData",
  1: "livestreamWideRoadEncodeData",
}


@dataclass(frozen=True)
class StarPortConfig:
  enabled: bool
  headunitpad_mode: bool
  allow_offroad: bool
  video_source: int
  port: int

  @property
  def cereal_service(self) -> str:
    return VIDEO_SOURCES.get(self.video_source, VIDEO_SOURCES[0])


def enabled(params) -> bool:
  return bool(params.get_bool(PARAM_ENABLED))


def allow_offroad(params) -> bool:
  return bool(params.get_bool(PARAM_ALLOW_OFFROAD))


def read_config(params) -> StarPortConfig:
  raw_source = params.get(PARAM_VIDEO_SOURCE)
  try:
    video_source = int(raw_source) if raw_source is not None else 0
  except (TypeError, ValueError):
    video_source = 0
  if video_source not in VIDEO_SOURCES:
    video_source = 0

  raw_port = params.get(PARAM_PORT)
  try:
    port = int(raw_port) if raw_port is not None else DEFAULT_PORT
  except (TypeError, ValueError):
    port = DEFAULT_PORT
  if not (1024 <= port <= 65535):
    port = DEFAULT_PORT

  return StarPortConfig(
    enabled=bool(params.get_bool(PARAM_ENABLED)),
    headunitpad_mode=bool(params.get_bool(PARAM_HEADUNITPAD_MODE)),
    allow_offroad=bool(params.get_bool(PARAM_ALLOW_OFFROAD)),
    video_source=video_source,
    port=port,
  )
