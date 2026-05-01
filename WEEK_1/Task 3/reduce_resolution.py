import subprocess
import os
import sys

def reduce_video_resolution(input_file, output_file="reduced_resolution.mp4", width=1280, height=720):
    """
    Reduce video resolution using ffmpeg
    
    Args:
        input_file (str): Path to the input video file
        output_file (str): Name of the output file (default: reduced_resolution.mp4)
        width (int): Target width in pixels (default: 1280)
        height (int): Target height in pixels (default: 720)
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Video file '{input_file}' not found")
        return False
    
    # Build ffmpeg command with scale filter
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vf", f"scale={width}:{height}",  # Scale filter
        "-c:a", "aac",                       # Audio codec
        output_file
    ]
    
    print(f"Reducing resolution of {input_file}...")
    print(f"Target resolution: {width}x{height}")
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
    if len(sys.argv) < 2:
        # Default usage
        input_file = "merged_output.mp4"
        output_file = "reduced_resolution.mp4"
        width = 1280
        height = 720
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "reduced_resolution.mp4"
        width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
        height = int(sys.argv[4]) if len(sys.argv) > 4 else 720
    
    reduce_video_resolution(input_file, output_file, width, height)
