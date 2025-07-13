import cv2
import numpy as np
import math

input_path = 'input.jpg'
output_path = 'output.mp4'
width, height = 512, 512
duration = 10  # seconds
fps = 30
total_frames = duration * fps
zoom_cycles = 3
zoom_strength = 0.05

# Vertical movement settings
vertical_move_amplitude = 100  # pixels to move up/down
vertical_move_cycles = 2  # how many full up/down cycles in total duration

# Load input image
img = cv2.imread(input_path)
ih, iw = img.shape[:2]

# Prepare VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

for frame_num in range(total_frames):
    progress = (zoom_cycles * frame_num) / total_frames
    mod = progress % 1
    zoom_factor = 1 + zoom_strength * (1 - 2 * abs(mod - 0.5))

    # Calculate new size
    new_w = int(iw * zoom_factor)
    new_h = int(ih * zoom_factor)

    # Resize image
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Pad if smaller than output
    if new_w < width or new_h < height:
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        x_offset = (width - new_w) // 2
        y_offset = (height - new_h) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        resized = canvas
        new_w, new_h = width, height

    # Calculate fractional crop offsets (center crop)
    x_start = (new_w - width) / 2
    y_start = (new_h - height) / 2

    # Calculate vertical movement offset (sinusoidal)
    vertical_progress = (vertical_move_cycles * frame_num) / total_frames
    vertical_offset = vertical_move_amplitude * math.sin(2 * math.pi * vertical_progress)

    # Combine crop offset and vertical movement
    M = np.float32([
        [1, 0, -x_start],
        [0, 1, -y_start + vertical_offset]
    ])

    # Apply affine transform
    frame = cv2.warpAffine(resized, M, (width, height))

    out.write(frame)

out.release()
print("Done! Smooth zoom + vertical movement video saved to", output_path)
