import cv2
import numpy as np
import math
import random

def draw_advanced_sparkle(img, center, size, brightness, rotation_deg):
    """
    Draws an 8-ray sparkle (starburst) with soft radial glow and rotation.
    - img: uint8 BGR image to draw on
    - center: (x,y) pixel coordinates
    - size: max ray length in pixels
    - brightness: 0-255 intensity of the sparkle center
    - rotation_deg: sparkle rotation angle in degrees (affects rays)
    Returns the image with the sparkle drawn (blended).
    """
    x, y = center
    overlay = np.zeros_like(img, dtype=np.float32)

    # Draw radial glow: concentric circles fading out
    max_radius = size
    for r in range(max_radius, 0, -1):
        alpha = (brightness / 255.0) * (r / max_radius) * 0.3  # glow less intense than rays
        color_val = int(255 * alpha)
        color = (color_val, color_val, color_val)
        cv2.circle(overlay, (x, y), r, color, 1, lineType=cv2.LINE_AA)

    # Draw 8 rays, spaced 45 degrees apart, rotated by rotation_deg
    num_rays = 8
    ray_lengths = [size * random.uniform(0.7, 1.0) for _ in range(num_rays)]
    ray_widths = [max(1, int(size * random.uniform(0.1, 0.25))) for _ in range(num_rays)]
    brightness_float = brightness / 255.0

    for i in range(num_rays):
        angle_deg = i * (360 / num_rays) + rotation_deg
        angle_rad = math.radians(angle_deg)
        length = ray_lengths[i]
        width = ray_widths[i]

        x_end = int(x + length * math.cos(angle_rad))
        y_end = int(y + length * math.sin(angle_rad))
        color_val = int(255 * brightness_float)
        color = (color_val, color_val, color_val)

        cv2.line(overlay, (x, y), (x_end, y_end), color, width, lineType=cv2.LINE_AA)

    # Blend overlay onto img with alpha
    img_f = img.astype(np.float32)
    # Simple additive blending with clipping
    img_f = np.clip(img_f + overlay, 0, 255)

    return img_f.astype(np.uint8)


input_path = 'input.jpg'
output_path = 'output_advanced_sparkles.mp4'
width, height = 512, 512
duration = 10  # seconds
fps = 30
total_frames = duration * fps
zoom_cycles = 3
zoom_strength = 0.05

vertical_move_amplitude = 100
vertical_move_cycles = 2

num_sparkles = 50
sparkle_size_min = 4
sparkle_size_max = 8
sparkle_max_brightness = 255
sparkle_life_min = 15
sparkle_life_max = 30

img = cv2.imread(input_path)
ih, iw = img.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

sparkles = []
for _ in range(num_sparkles):
    x = random.randint(0, width - 1)
    y = random.randint(0, height - 1)
    life = random.randint(sparkle_life_min, sparkle_life_max)
    start_frame = random.randint(0, total_frames - 1)
    size = random.randint(sparkle_size_min, sparkle_size_max)
    rotation_speed = random.uniform(-5, 5)  # degrees per frame
    sparkles.append({
        'x': x, 'y': y,
        'life': life,
        'start': start_frame,
        'size': size,
        'rotation_speed': rotation_speed,
        'current_rotation': random.uniform(0, 360)
    })

for frame_num in range(total_frames):
    progress = (zoom_cycles * frame_num) / total_frames
    mod = progress % 1
    zoom_factor = 1 + zoom_strength * (1 - 2 * abs(mod - 0.5))

    new_w = int(iw * zoom_factor)
    new_h = int(ih * zoom_factor)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    if new_w < width or new_h < height:
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        x_offset = (width - new_w) // 2
        y_offset = (height - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        resized = canvas
        new_w, new_h = width, height

    x_start = (new_w - width) / 2
    y_start = (new_h - height) / 2

    vertical_progress = (vertical_move_cycles * frame_num) / total_frames
    vertical_offset = vertical_move_amplitude * math.sin(2 * math.pi * vertical_progress)

    M = np.float32([
        [1, 0, -x_start],
        [0, 1, -y_start + vertical_offset]
    ])

    frame = cv2.warpAffine(resized, M, (width, height))

    for s in sparkles:
        age = (frame_num - s['start']) % total_frames
        if age < s['life']:
            half_life = s['life'] / 2
            if age < half_life:
                brightness = int((age / half_life) * sparkle_max_brightness)
            else:
                brightness = int(((s['life'] - age) / half_life) * sparkle_max_brightness)

            # Update rotation
            s['current_rotation'] = (s['current_rotation'] + s['rotation_speed']) % 360

            frame = draw_advanced_sparkle(
                frame,
                (s['x'], s['y']),
                s['size'],
                brightness,
                s['current_rotation']
            )

    out.write(frame)

out.release()
print("Done! Video with advanced rotating starburst sparkles saved to", output_path)
