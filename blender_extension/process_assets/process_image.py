import numpy as np
import struct

def process_image(image, send_images):
    width, height = tuple(image.size)
    if width == 0 and height == 0:
        return None
    
    pixels = np.empty(width * height * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    np.multiply(pixels, 255, out=pixels)
    image_bytes = struct.pack("<2H", width, height) + pixels.astype(np.uint8).data

    image_hash = hash(image_bytes)
    if not image_hash in send_images:
        send_images[image_hash] = image_bytes
    return image_hash