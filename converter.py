from PIL import Image
import math
import os
from moviepy.editor import ImageSequenceClip
import imageio
import numpy as np
from PIL import Image
import io
from tqdm import tqdm


def file_to_binary(zip_input=""):
    file_size = os.path.getsize(zip_input)
    binary_string = ""
    with open(zip_input, "rb") as f:
        for chunk in tqdm(iterable=iter(lambda: f.read(1024), b""), total=math.ceil(file_size/1024), unit="KB"):
            binary_string += "".join(f"{byte:08b}" for byte in chunk)

    return binary_string

def binary_to_video(bin_string, width=1920, height=1080, pixel_size=4, fps=24, mp4_output="D:\\"):
    num_pixels = len(bin_string)
    pixels_per_image = (width // pixel_size) * (height // pixel_size)
    num_images = math.ceil(num_pixels / pixels_per_image)
    frames = []
    for i in tqdm(range(num_images)):
        start_index = i * pixels_per_image
        end_index = min(start_index + pixels_per_image, num_pixels)
        binary_digits = bin_string[start_index:end_index]
        img = Image.new('RGB', (width, height), color='white')
        for row_index in range(height // pixel_size):
            start_index = row_index * (width // pixel_size)
            end_index = start_index + (width // pixel_size)
            row = binary_digits[start_index:end_index]
            for col_index, digit in enumerate(row):
                if digit == '1':
                    color = (0, 0, 0)
                else:
                    color = (255, 255, 255) 
                x1 = col_index * pixel_size
                y1 = row_index * pixel_size
                x2 = x1 + pixel_size
                y2 = y1 + pixel_size
                img.paste(color, (x1, y1, x2, y2))
        with io.BytesIO() as f:
            img.save(f, format='PNG')
            frame = np.array(Image.open(f))
        frames.append(frame)

    clip = ImageSequenceClip(frames, fps=fps)

    clip.write_videofile(mp4_output + 'video.mp4', fps=fps)


def process_images(frames):
    threshold = 128
    binary_digits = ''
    for frame in tqdm(frames, desc="Processing frames"):
        gray_frame = np.mean(frame, axis=2).astype(np.uint8)
        pixel_size = 4
        for y in range(0, gray_frame.shape[0], pixel_size):
            for x in range(0, gray_frame.shape[1], pixel_size):
                color = gray_frame[y:y+pixel_size, x:x+pixel_size]
                if color.mean() < threshold:
                    binary_digits += '1'
                else:
                    binary_digits += '0'
    return binary_digits

def binaryToFile(binary_filename,zip_output = ""):
    binary_data = bytes(int(binary_filename[i:i+8], 2)
                        for i in range(0, len(binary_filename), 8))
    with open(zip_output + "reversed.zip", "wb") as f:
        with tqdm(total=len(binary_data), unit='B', unit_scale=True, desc="Writing binary data") as pbar:
            for chunk in range(0, len(binary_data), 1024):
                f.write(binary_data[chunk:chunk+1024])
                pbar.update(1024)


def ExtractFrames(zip_output = ""):
    am = []
    dir_path = zip_output
    files = [f for f in os.listdir(dir_path) if f.endswith('.webm')]
    files = [f for f in os.listdir(dir_path) if f.endswith('.mp4')]
    files = files[0]
    files = dir_path + files
    vid = imageio.get_reader(files, 'ffmpeg')
    fps = vid.get_meta_data()['fps']
    num_frames = vid.get_length()
    with tqdm(total=num_frames) as pbar:
        for i, frame in enumerate(vid):
            am.append(frame)
            pbar.update(1)
    return am
