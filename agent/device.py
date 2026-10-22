import struct
import zlib

import numpy as np
from maa.context import Context

from common import PACKAGE, screencap

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def shell(context: Context, cmd: str) -> str:
    return context.tasker.controller.post_shell(cmd).wait().get()


def su(context: Context, cmd: str) -> str:
    return shell(context, f"su -c '{cmd}'")


def launch_app(context: Context) -> bool:
    output = context.tasker.controller.post_shell(f"monkey -p {PACKAGE} 1", 10000).wait().get()
    return bool(output) and "Events injected" in output


def png_chunk(tag: bytes, data: bytes) -> bytes:
    body = tag + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def encode_png(image: np.ndarray) -> bytes:
    height, width = image.shape[:2]
    rgb = np.ascontiguousarray(image[:, :, 2::-1]).reshape(height, width * 3)
    rows = np.concatenate([np.zeros((height, 1), dtype=np.uint8), rgb], axis=1)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + png_chunk(b"IHDR", header)
        + png_chunk(b"IDAT", zlib.compress(rows.tobytes()))
        + png_chunk(b"IEND", b"")
    )


def screenshot_png(context: Context) -> bytes:
    return encode_png(screencap(context))
