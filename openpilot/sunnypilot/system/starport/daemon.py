"""StarPort & CarPlay Live View projection daemon (starportd).

Listens on the configured TCP port (default 5277 for HeadunitPad / CarPlay Live View
StarPortReceiver), runs the StarPort ProjectionSession TLS-in-AA handshake, and
streams live H.264 access units from stream_encoderd.
"""
from __future__ import annotations

import logging
import select
import signal
import socket
import time

from openpilot.sunnypilot.system.starport.identity import ensure_identity
from openpilot.sunnypilot.system.starport.session import (
  AuthenticationRejected,
  PeerRequestedStop,
  ProjectionSession,
)
from openpilot.sunnypilot.system.starport.settings import StarPortConfig, read_config

log = logging.getLogger("starportd")
V4L2_BUF_FLAG_KEYFRAME = 0x8


def _serve_client(peer: socket.socket, cert_path: str, key_path: str, config: StarPortConfig,
                  params, stop_requested) -> None:
  from openpilot.cereal import messaging

  peer.settimeout(15.0)
  session = ProjectionSession(peer, cert_path, key_path)
  session.fragment_acks = config.headunitpad_mode
  session.authenticate()
  mode = session.start("sunnypilot StarPort", "sunnypilot")
  log.info("StarPort client connected: %dx%d codec=%s fragment_acks=%s",
           mode.width, mode.height, mode.codec, session.fragment_acks)

  sock = messaging.sub_sock(config.cereal_service, conflate=True)
  params.put_bool("LivestreamRequestKeyframe", True)
  seen_keyframe = False
  t0_us = time.monotonic_ns() // 1000

  try:
    while not stop_requested():
      session.pump(0.01)
      if not session.focused:
        continue
      if not session.can_send:
        continue

      msg = messaging.recv_one_or_none(sock)
      if msg is None:
        continue

      encode_data = getattr(msg, msg.which())
      is_keyframe = bool(encode_data.idx.flags & V4L2_BUF_FLAG_KEYFRAME)
      if not seen_keyframe:
        if not is_keyframe:
          continue
        seen_keyframe = True
        params.put_bool("LivestreamRequestKeyframe", False)

      payload = bytes(encode_data.header) + bytes(encode_data.data)
      if not payload:
        continue
      pts_us = (time.monotonic_ns() // 1000) - t0_us
      session.send_frame(payload, pts_us, keyframe=is_keyframe)
  finally:
    try:
      session.shutdown()
    except Exception:
      pass


def main() -> None:
  from openpilot.common.params import Params

  logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
  params = Params()
  stopping = False

  def _handle_signal(_signum, _frame):
    nonlocal stopping
    stopping = True

  signal.signal(signal.SIGTERM, _handle_signal)
  signal.signal(signal.SIGINT, _handle_signal)

  identity = ensure_identity()
  config = read_config(params)
  if not config.enabled:
    log.info("StarPortEnabled is false; exiting starportd")
    return

  listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  listener.bind(("0.0.0.0", config.port))
  listener.listen(2)
  listener.setblocking(False)
  log.info("starportd listening on 0.0.0.0:%d (source=%s headunitpad=%s)",
           config.port, config.cereal_service, config.headunitpad_mode)

  try:
    while not stopping:
      if not read_config(params).enabled:
        log.info("StarPortEnabled turned off; stopping listener")
        break
      ready, _, _ = select.select([listener], [], [], 0.5)
      if not ready:
        continue
      peer, addr = listener.accept()
      log.info("Accepted StarPort connection from %s:%d", addr[0], addr[1])
      try:
        _serve_client(peer, identity.cert, identity.key, read_config(params), params, lambda: stopping)
      except (AuthenticationRejected, PeerRequestedStop, OSError) as exc:
        log.info("StarPort session ended (%s): %s", type(exc).__name__, exc)
      finally:
        try:
          peer.close()
        except OSError:
          pass
  finally:
    listener.close()


if __name__ == "__main__":
  main()
