import cv2
import os
import time
import ffmpeg
import numpy as np
from colorama import init, Fore
from concurrent.futures import ThreadPoolExecutor, as_completed


init()

def print_banner(banner, color=None):
    if color is not None:
        print("\033[{}m{}\033[0m".format(color, banner))
    else:
        print(banner)

banner = r'''



__   ___    _ ___                  __  ___               _           
 \ \ / (_)__| | ___ _ __ _ _ __  ___\ \/ | |_ _ _ __ _ __| |_ ___ _ _ 
  \ V /| / _` | _| '_/ _` | '  \/ -_)>  <|  _| '_/ _` / _|  _/ _ | '_|
   \_/ |_\__,_|_||_| \__,_|_|_|_\___/_/\_\\__|_| \__,_\__|\__\___|_|  
                                                                       

                                                       - by vijay                                                          



'''
print_banner(banner, 93)



def get_video_info(video_path):
    try:
        probe = ffmpeg.probe(video_path)
        format_info = probe['format']
        streams_info = probe['streams']

        video_info = {
            'filename': os.path.basename(video_path),
            'size': format_info['size'],
            'duration': float(format_info['duration']),
            'bitrate': format_info['bit_rate'],
            'format': format_info['format_name'],
            'codec': format_info['codec_name'] if 'codec_name' in format_info else 'unknown',
            'streams': []
        }

        for stream in streams_info:
            stream_info = {
                'codec_type': stream['codec_type'],
                'codec_name': stream['codec_name'],
                'bit_rate': stream['bit_rate'] if 'bit_rate' in stream else 'unknown',
                'width': stream['width'] if 'width' in stream else 'unknown',
                'height': stream['height'] if 'height' in stream else 'unknown',
                'sample_rate': stream['sample_rate'] if 'sample_rate' in stream else 'unknown',
                'channels': stream['channels'] if 'channels' in stream else 'unknown'
            }
            video_info['streams'].append(stream_info)

        return video_info
    except ffmpeg.Error as e:
        print(f"Error extracting metadata for {video_path}: {e}")
        return None

def print_video_info(video_info):
    if video_info:
        print(f"Video: {video_info['filename']}")
        print(f"Size: {video_info['size']} bytes")
        print(f"Duration: {video_info['duration']} seconds")
        print(f"Bitrate: {video_info['bitrate']} bps")
        print(f"Format: {video_info['format']}")
        print(f"Codec: {video_info['codec']}")
        for i, stream in enumerate(video_info['streams']):
            print(f"Stream {i+1}:")
            print(f"  Type: {stream['codec_type']}")
            print(f"  Codec: {stream['codec_name']}")
            if stream['codec_type'] == 'video':
                print(f"  Resolution: {stream['width']}x{stream['height']}")
            elif stream['codec_type'] == 'audio':
                print(f"  Sample Rate: {stream['sample_rate']} Hz")
                print(f"  Channels: {stream['channels']}")
            print(f"  Bitrate: {stream['bit_rate']} bps")

def enhance_frame(frame, method='sharpen'):
    if method == 'sharpen':
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        enhanced_frame = cv2.filter2D(frame, -1, kernel)
    elif method == 'denoise':
        enhanced_frame = cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
    else:
        enhanced_frame = frame
    return enhanced_frame

def extract_frames(video_path, output_folder, frame_rate=None, image_format='jpg', quality=100, start_time=None, end_time=None, enhance=False, enhance_method='sharpen'):
    try:
        #github.com/VijayShankar22
        video_info = get_video_info(video_path)
        print_video_info(video_info)
        
        
        video_capture = cv2.VideoCapture(video_path)
        
        if not video_capture.isOpened():
            raise ValueError(f"Error opening video file: {video_path}")
        
        
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))
        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps
        
        
        if frame_rate is None:
            frame_rate = fps
        interval = max(1, fps // frame_rate)
        
        
        if start_time is not None:
            start_frame = int(start_time * fps)
        else:
            start_frame = 0
        if end_time is not None:
            end_frame = int(end_time * fps)
        else:
            end_frame = total_frames
        
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        frame_count = 0
        extracted_frame_count = 0
        total_extracted_frames = (end_frame - start_frame) // interval
        start_time = time.time()
        
        
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        while frame_count < (end_frame - start_frame):
            success, frame = video_capture.read()
            if not success:
                break
            
            if frame_count % interval == 0:
                if enhance:
                    frame = enhance_frame(frame, method=enhance_method)
                frame_filename = os.path.join(output_folder, f'frame_{extracted_frame_count:06d}.{image_format}')
                if image_format == 'jpg':
                    cv2.imwrite(frame_filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
                elif image_format == 'png':
                    cv2.imwrite(frame_filename, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                elif image_format == 'bmp':
                    cv2.imwrite(frame_filename, frame)
                extracted_frame_count += 1
            
            frame_count += 1
            
            
            if frame_count % (50 * interval) == 0:
                elapsed_time = time.time() - start_time
                estimated_total_time = (elapsed_time / extracted_frame_count) * total_extracted_frames
                estimated_time_remaining = estimated_total_time - elapsed_time
                print(f"Extracted {extracted_frame_count}/{total_extracted_frames} frames.")
                print(f"Elapsed time: {elapsed_time:.2f} seconds.")
                print(f"Estimated time remaining: {estimated_time_remaining:.2f} seconds.")
        
        video_capture.release()
        total_elapsed_time = time.time() - start_time
        print(f"Extraction complete. Extracted {extracted_frame_count} frames in {total_elapsed_time:.2f} seconds.")
    
    except Exception as e:
        print(f"Error processing video {video_path}: {e}")

def process_videos(path, output_base_folder, frame_rate=None, image_format='jpg', quality=100, start_time=None, end_time=None, enhance=False, enhance_method='sharpen'):
    
    if os.path.isdir(path):
        video_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    else:
        video_files = [path]
    
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for video_file in video_files:
            output_folder = os.path.join(output_base_folder, os.path.splitext(os.path.basename(video_file))[0])
            futures.append(executor.submit(extract_frames, video_file, output_folder, frame_rate, image_format, quality, start_time, end_time, enhance, enhance_method))
        
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    
    path = input(Fore.LIGHTMAGENTA_EX + "Enter the directory path containing videos or the path to a single video file: " + Fore.RESET).strip().strip('"')
    output_base_folder = input(Fore.LIGHTMAGENTA_EX + "Enter the output base folder: " + Fore.RESET).strip().strip('"')
    frame_rate = input(Fore.LIGHTMAGENTA_EX + "Enter the frame rate for extraction (leave blank for original rate): " + Fore.RESET).strip()
    frame_rate = int(frame_rate) if frame_rate else None
    image_format = input(Fore.LIGHTMAGENTA_EX + "Enter the image format (jpg, png, bmp): " + Fore.RESET).strip().lower()
    quality = input(Fore.LIGHTMAGENTA_EX + "Enter the quality for images (0-100 for jpg, 0-9 for png): " + Fore.RESET).strip()
    quality = int(quality) if quality else 100
    start_time = input(Fore.LIGHTMAGENTA_EX + "Enter the start time for extraction in seconds (leave blank to start from beginning): " + Fore.RESET).strip()
    start_time = float(start_time) if start_time else None
    end_time = input(Fore.LIGHTMAGENTA_EX + "Enter the end time for extraction in seconds (leave blank to extract till end): " + Fore.RESET).strip()
    end_time = float(end_time) if end_time else None

    
    enhance_choice = input(Fore.YELLOW + "Do you want to enhance the frames? (yes/no): " + Fore.RESET).strip().lower()


    if enhance_choice == 'yes':
        confirm = input(Fore.RED + "Caution: Enabling frame enhancement will significantly increase processing time and CPU usage. Do you want to proceed? (yes/no): " + Fore.RESET).strip().lower()
        enhance = (confirm == 'yes')
    else:
        enhance = False


    enhance_method = 'sharpen'
    if enhance:
        enhance_method = input("Choose enhancement method (sharpen/denoise): ").strip().lower()

    
    process_videos(path, output_base_folder, frame_rate, image_format, quality, start_time, end_time, enhance, enhance_method)