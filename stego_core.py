# stego_core.py - LSB steganography functions for embedding and extracting files

import os
import struct
import zlib
import numpy as np
from PIL import Image

MAGIC_HEADER = b"STEG"


def get_image_capacity(image_path_or_img, bits_per_channel=1):
    # calculate how many bytes can be hidden in the cover image
    if isinstance(image_path_or_img, (str, os.PathLike)):
        img = Image.open(image_path_or_img).convert("RGB")
    else:
        img = image_path_or_img.convert("RGB")
        
    width, height = img.size
    total_pixels = width * height
    total_carrier_bits = total_pixels * 3 * bits_per_channel
    total_carrier_bytes = total_carrier_bits // 8

    # reserve space for header (magic, ext, length, crc)
    overhead = 32
    max_payload = max(0, total_carrier_bytes - overhead)

    return {
        "width": width,
        "height": height,
        "total_pixels": total_pixels,
        "total_capacity_bytes": total_carrier_bytes,
        "max_payload_bytes": max_payload,
        "max_payload_kb": max_payload / 1024,
    }


def bytes_to_bits(data):
    # convert bytes to array of 0s and 1s
    byte_arr = np.frombuffer(data, dtype=np.uint8)
    return np.unpackbits(byte_arr)


def bits_to_bytes(bits):
    # convert array of 0s and 1s back to bytes
    packed = np.packbits(bits)
    return packed.tobytes()


def build_packet(secret_bytes, file_extension):
    # packet format: [STEG (4B)] + [ext len (1B)] + [ext] + [file size (4B)] + [payload] + [crc32 (4B)]
    ext = file_extension.lower().strip()
    if not ext.startswith("."):
        ext = "." + ext
    ext_bytes = ext.encode("utf-8")
    
    if len(ext_bytes) > 255:
        raise ValueError("File extension is too long.")

    payload_len = len(secret_bytes)
    crc = zlib.crc32(secret_bytes) & 0xFFFFFFFF

    header = MAGIC_HEADER
    header += struct.pack("!B", len(ext_bytes))
    header += ext_bytes
    header += struct.pack("!I", payload_len)
    
    return header + secret_bytes + struct.pack("!I", crc)


def hide_data(cover_image_path, secret_file_path_or_bytes, output_stego_path, file_extension=None):
    # load cover image
    if not os.path.exists(cover_image_path):
        raise FileNotFoundError(f"Cover image not found: {cover_image_path}")
    
    with Image.open(cover_image_path) as img:
        img_rgb = img.convert("RGB")
        width, height = img_rgb.size
        pixel_array = np.array(img_rgb, dtype=np.uint8)

    # read secret file
    if isinstance(secret_file_path_or_bytes, (str, os.PathLike)):
        secret_path = str(secret_file_path_or_bytes)
        if not os.path.exists(secret_path):
            raise FileNotFoundError(f"Secret file not found: {secret_path}")
        with open(secret_path, "rb") as f:
            secret_bytes = f.read()
        if file_extension is None:
            _, ext = os.path.splitext(secret_path)
            file_extension = ext if ext else ".bin"
    elif isinstance(secret_file_path_or_bytes, bytes):
        secret_bytes = secret_file_path_or_bytes
        if file_extension is None:
            file_extension = ".bin"
    else:
        raise TypeError("secret_file_path_or_bytes must be a file path or bytes.")

    # create header and data packet
    packet = build_packet(secret_bytes, file_extension)
    packet_bits = bytes_to_bits(packet)
    total_bits_needed = len(packet_bits)

    # check if cover image has enough capacity
    flat_pixels = pixel_array.reshape(-1)
    available_bits = len(flat_pixels)

    if total_bits_needed > available_bits:
        raise ValueError(
            f"File too large ({len(secret_bytes):,} bytes). "
            f"Needs {total_bits_needed:,} bits, but cover image capacity is {available_bits:,} bits."
        )

    # replace least significant bit (LSB) of each pixel byte
    flat_copy = flat_pixels.copy()
    flat_copy[:total_bits_needed] = (flat_copy[:total_bits_needed] & 0xFE) | packet_bits

    # reconstruct image and save as PNG
    stego_array = flat_copy.reshape((height, width, 3))
    stego_img = Image.fromarray(stego_array, mode="RGB")
    
    out_dir = os.path.dirname(os.path.abspath(output_stego_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    base, ext = os.path.splitext(output_stego_path)
    if ext.lower() != ".png":
        output_stego_path = base + ".png"

    stego_img.save(output_stego_path, format="PNG", compress_level=6)

    cover_size = os.path.getsize(cover_image_path)
    stego_size = os.path.getsize(output_stego_path)

    return {
        "status": "success",
        "output_path": output_stego_path,
        "payload_bytes": len(secret_bytes),
        "file_extension": file_extension,
        "image_width": width,
        "image_height": height,
        "cover_file_size": cover_size,
        "stego_file_size": stego_size,
        "size_change_bytes": stego_size - cover_size,
        "bits_modified": int(np.sum(flat_pixels[:total_bits_needed] != flat_copy[:total_bits_needed])),
    }


def extract_data(stego_image_path, output_dir_or_file=None):
    # load stego image
    if not os.path.exists(stego_image_path):
        raise FileNotFoundError(f"Stego image not found: {stego_image_path}")

    with Image.open(stego_image_path) as img:
        img_rgb = img.convert("RGB")
        pixel_array = np.array(img_rgb, dtype=np.uint8)

    flat_pixels = pixel_array.reshape(-1)
    
    # check magic header (first 32 bits = 4 bytes)
    if len(flat_pixels) < 32:
        raise ValueError("Image is too small to contain secret data.")

    magic_bits = flat_pixels[:32] & 1
    magic_bytes = bits_to_bytes(magic_bits)
    if magic_bytes != MAGIC_HEADER:
        raise ValueError("No secret data found in this image (header mismatch).")

    cursor = 32
    
    # read extension length
    ext_len_bits = flat_pixels[cursor:cursor+8] & 1
    cursor += 8
    ext_len = struct.unpack("!B", bits_to_bytes(ext_len_bits))[0]

    # read file extension
    ext_bits_len = ext_len * 8
    ext_bits = flat_pixels[cursor:cursor+ext_bits_len] & 1
    cursor += ext_bits_len
    ext_str = bits_to_bytes(ext_bits).decode("utf-8", errors="replace")

    # read payload size
    size_bits = flat_pixels[cursor:cursor+32] & 1
    cursor += 32
    payload_size = struct.unpack("!I", bits_to_bytes(size_bits))[0]

    available_bits = len(flat_pixels) - cursor
    needed_bits = (payload_size + 4) * 8
    if needed_bits > available_bits:
        raise ValueError("Corrupted data: payload size exceeds image capacity.")

    # extract payload bytes
    payload_bits_len = payload_size * 8
    payload_bits = flat_pixels[cursor:cursor+payload_bits_len] & 1
    cursor += payload_bits_len
    payload = bits_to_bytes(payload_bits)

    # read crc32 checksum
    crc_bits = flat_pixels[cursor:cursor+32] & 1
    cursor += 32
    expected_crc = struct.unpack("!I", bits_to_bytes(crc_bits))[0]

    # verify crc32
    computed_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if computed_crc != expected_crc:
        raise ValueError(
            f"CRC32 mismatch! Expected 0x{expected_crc:08X}, but got 0x{computed_crc:08X}."
        )

    # save file if destination specified
    saved_path = None
    if output_dir_or_file is not None:
        if os.path.isdir(output_dir_or_file):
            saved_path = os.path.join(output_dir_or_file, f"extracted_secret{ext_str}")
        else:
            saved_path = output_dir_or_file
            _, existing_ext = os.path.splitext(saved_path)
            if not existing_ext:
                saved_path += ext_str
        
        save_parent = os.path.dirname(os.path.abspath(saved_path))
        if save_parent:
            os.makedirs(save_parent, exist_ok=True)
        with open(saved_path, "wb") as f:
            f.write(payload)

    return {
        "status": "success",
        "file_extension": ext_str,
        "payload_size": payload_size,
        "crc32": f"0x{computed_crc:08X}",
        "saved_path": saved_path,
        "payload_bytes": payload,
    }
