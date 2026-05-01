import subprocess
import os
import sys

def merge_audio_video(video_file, audio_file, output_file="merged_output.mp4"):
    """
    Merge audio track with video file using ffmpeg
    
    Args:
        video_file (str): Path to the video file
        audio_file (str): Path to the audio file
        output_file (str): Name of the output file (default: merged_output.mp4)
    """
    
    # Check if input files exist
    if not os.path.exists(video_file):
        print(f"Error: Video file '{video_file}' not found")
        return False
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found")
        return False
    
    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-i", video_file,
        "-i", audio_file,
        "-c:v", "copy",           # Copy video stream without re-encoding
        "-c:a", "aac",            # Encode audio as AAC
        "-map", "0:v:0",          # Map video from first input
        "-map", "1:a:0",          # Map audio from second input
        output_file
    ]
    
    print(f"Merging {video_file} with {audio_file}...")
    print(f"Output file: {output_file}")
    print()
    
    try:
        # Run ffmpeg command
        subprocess.run(cmd, check=True)
        print(f"\n✓ Successfully created {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg and add it to PATH")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Default usage with existing files
        video = "output.mp4"
        audio = "audio.mp3"
        output = "merged_output.mp4"
        
        if len(sys.argv) == 2:
            output = sys.argv[1]
    else:
        video = sys.argv[1]
        audio = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else "merged_output.mp4"
    
    merge_audio_video(video, audio, output)
