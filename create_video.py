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
# Function to crop the top half of the video
def crop_top_half(clip):
    w, h = clip.size
    return clip.crop(y1=0, y2=h/2)


# Function to reduce resolution of the clip
def reduce_resolution(clip, target_resolution=(640, 360)):
    return clip.resize(newsize=target_resolution)

# Function to process a single folder
def process_folder(folder_path):
    # List all MP4 files in the directory
    files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    
    # Sort files by timestamp
    files.sort(key=extract_timestamp)
    
    final_clips = []

    # Iterate over files and process them
    for filename in files:
        clip = VideoFileClip(os.path.join(folder_path, filename)).subclip(0, 30)  # Take the first 30 seconds
        if "back" in filename.lower():
            print(f"Cropping video: {filename}")  # Log cropping action
            clip = crop_top_half(clip)  # Crop the top half of the clip
        clip = reduce_resolution(clip)  # Reduce resolution
        final_clips.append(clip)

    # Concatenate all the clips together
    final_video = concatenate_videoclips(final_clips, method="chain")
    output_filename = os.path.join(folder_path, 'final_output.mp4')
    final_video.write_videofile(output_filename, codec="libx264", fps=24, threads=cpu_count())

# Worker function for multiprocessing
def worker(folder_path):
    try:
        print(f"Processing folder: {folder_path}")
        process_folder(folder_path)
        print(f"Finished processing folder: {folder_path}")
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'Processed {folder_path} at {timestamp}\n'
        return log_entry
    except Exception as e:
        print(f"An error occurred while processing {folder_path}: {e}")  # Log error
        return f"An error occurred while processing {folder_path}: {e}\n"

# Function to process all folders using multiprocessing
def process_all_folders(parent_folder, log_file_path):
    all_folders = [os.path.join(parent_folder, f) for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]
    
    # Create a pool of workers
    with Pool(cpu_count()) as pool:
        log_entries = pool.map(worker, all_folders)
    
    # Write log entries to the log file
    with open(log_file_path, 'a') as log_file:
        for entry in log_entries:
            log_file.write(entry)




if __name__ == '__main__':
    freeze_support()  # Needed for Windows compatibility
    process_all_folders('/Users/sauravsharma/Downloads/SavedClips2/', 'log_file.txt')
