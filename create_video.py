import os
import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips
from multiprocessing import Pool, cpu_count, freeze_support

# Function to get timestamp from filename
def extract_timestamp(filename):
    parts = filename.split('_')
    date_part, time_part = parts[0], parts[-1].split('.')[0]
    return date_part + time_part

# Function to crop the lower part of the video
def crop_bottom(clip, height_ratio=0.5):
    w, h = clip.size
    crop_height = int(h * height_ratio)
    return clip.crop(y1=0, y2=h - crop_height)

# Function to reduce resolution of the clip
def reduce_resolution(clip, target_resolution=(640, 360)):
    return clip.resize(newsize=target_resolution)

# Function to check if a folder has been processed by reading the log file
def is_folder_processed(log_file_path, folder_name):
    if not os.path.exists(log_file_path):
        return False
    with open(log_file_path, 'r') as log_file:
        log_content = log_file.read()
    return folder_name in log_content

# Function to process a single folder
def process_folder(folder_path, output_folder, log_file_path):
    folder_name = os.path.basename(folder_path)
    # Skip processing if folder is already logged as processed
    if is_folder_processed(log_file_path, folder_name):
        print(f"Skipping already processed folder: {folder_name}")
        return f"Skipped {folder_name}\n"

    files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    files.sort(key=extract_timestamp)
    
    final_clips = []

    for filename in files:
        clip = VideoFileClip(os.path.join(folder_path, filename)).subclip(0, 30)
        if "back" in filename.lower():
            clip = crop_bottom(clip)
        clip = reduce_resolution(clip)
        final_clips.append(clip)

    if final_clips:
        final_video = concatenate_videoclips(final_clips, method="chain")
        output_filename = os.path.join(output_folder, folder_name + '.mp4')
        final_video.write_videofile(output_filename, codec="libx264", fps=24, threads=cpu_count())
        return f"Processed {folder_name}\n"
    else:
        return f"No files to process in {folder_name}\n"

# Worker function for multiprocessing
def worker(args):
    folder_path, output_folder, log_file_path = args
    try:
        print(f"Processing folder: {folder_path}")
        log_entry = process_folder(folder_path, output_folder, log_file_path)
        print(f"Finished processing folder: {folder_path}")
        return log_entry
    except Exception as e:
        print(f"An error occurred while processing {folder_path}: {e}")
        return f"An error occurred while processing {folder_path}: {e}\n"

# Function to process all folders using multiprocessing
def process_all_folders(parent_folder, output_folder, log_file_path):
    all_folders = [os.path.join(parent_folder, f) for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]
    
    # Prepare arguments for the worker function
    worker_args = [(folder, output_folder, log_file_path) for folder in all_folders]

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a pool of workers
    with Pool(cpu_count()) as pool:
        log_entries = pool.map(worker, worker_args)

    # Write log entries to the log file
    with open(log_file_path, 'a') as log_file:
        for entry in log_entries:
            log_file.write(entry)

if __name__ == '__main__':
    freeze_support()  # Needed for Windows compatibility
    current_path = os.getcwd()
    output_folder = os.path.join(current_path, 'output')
    log_file_path = os.path.join(current_path, 'log_file.txt')
    process_all_folders('/Users/sauravsharma/Downloads/SavedClips2/', output_folder, log_file_path)
