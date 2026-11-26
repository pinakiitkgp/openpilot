"""Unit and loopback tests for the sunnypilot StarPort port."""
from __future__ import annotations

import os
import stat
import tempfile
import unittest
from pathlib import Path

from openpilot.sunnypilot.system.starport import identity, settings, wire
from openpilot.sunnypilot.system.starport.session import ProjectionSession


class FakeParams:
  def __init__(self, data=None):
    self._data = dict(data or {})

  def get_bool(self, key: str) -> bool:
    val = self._data.get(key)
    if isinstance(val, bool):
      return val
    return str(val).lower() in ("1", "true")

  def get(self, key: str):
    return self._data.get(key)


class TestStarPortSunnypilot(unittest.TestCase):
  def test_ensure_identity_generates_secure_cert_and_key(self):
    with tempfile.TemporaryDirectory() as tmp:
      ident = identity.ensure_identity(Path(tmp))
      self.assertTrue(Path(ident.cert).is_file())
      self.assertTrue(Path(ident.key).is_file())
      self.assertEqual(stat.S_IMODE(os.stat(ident.key).st_mode), 0o600)
      self.assertGreater(ident.days_left, 3000)
      # Subsequent call reuses existing identity without error
      ident2 = identity.ensure_identity(Path(tmp))
      self.assertEqual(ident.cert, ident2.cert)

  def test_read_config_defaults_and_overrides(self):
    cfg = settings.read_config(FakeParams({}))
    self.assertFalse(cfg.enabled)
    self.assertFalse(cfg.headunitpad_mode)
    self.assertFalse(cfg.allow_offroad)
    self.assertEqual(cfg.port, 5277)
    self.assertEqual(cfg.cereal_service, "livestreamNarrowRoadEncodeData")

    cfg2 = settings.read_config(FakeParams({
      "StarPortEnabled": "1",
      "StarPortHeadunitPadMode": "1",
      "StarPortAllowOffroad": "1",
      "StarPortVideoSource": "1",
      "StarPortPort": "5278",
    }))
    self.assertTrue(cfg2.enabled)
    self.assertTrue(cfg2.headunitpad_mode)
    self.assertTrue(cfg2.allow_offroad)
    self.assertEqual(cfg2.port, 5278)
    self.assertEqual(cfg2.cereal_service, "livestreamWideRoadEncodeData")

  def test_wire_roundtrip(self):
    encoded = wire.field(1, 5277) + wire.field(2, "sunnypilot")
    parsed = wire.parse_fields(encoded)
    self.assertEqual(wire.one(parsed, 1), 5277)
    self.assertEqual(wire.one(parsed, 2), b"sunnypilot")

  def test_projection_session_importable(self):
    self.assertTrue(callable(ProjectionSession))


if __name__ == "__main__":
  unittest.main()
