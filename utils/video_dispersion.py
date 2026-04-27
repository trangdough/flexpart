import argparse
import os
import glob
import imageio.v2 as imageio

def main():
    # =========================
    # Argument Parsing
    # =========================
    parser = argparse.ArgumentParser(description="Stitch dispersion frames into a video or GIF.")
    
    parser.add_argument("--dir-path", default="/scratch/scholar/do47/flexpart/output/2017v5/", type=str, help="Directory containing the PNG frames.")
    parser.add_argument("--site-code", default="70805FRMSPGULFS", type=str, help="TRI site code of the facility (used to find the files).")
    parser.add_argument("--release-date", required=True, type=str, help="Date of the release (used to find the files).")
    parser.add_argument("--fps", default=4, type=int, help="Frames per second for the video (default: 4).")
    
    args = parser.parse_args()

    image_dir = os.path.join(args.dir_path, args.site_code, args.release_date, "results")
    
    # Create the search pattern and sort the files so they play in chronological order
    search_pattern = os.path.join(image_dir, f"{args.site_code}_{args.release_date}_*h.png")
    image_files = sorted(glob.glob(search_pattern))
    
    if not image_files:
        print(f"Error: No images found matching pattern: {search_pattern}")
        print("Check that your --image-dir and --site-name match the plotting script outputs exactly.")
        return

    print(f"Found {len(image_files)} frames. Creating video at {args.fps} FPS...")

    output_name = f"{args.site_code}_{args.release_date}.mp4"
    output_path = os.path.join(image_dir, output_name)
    
    # =========================
    # Write the Video
    # =========================
    # If outputting an MP4, imageio will automatically use its ffmpeg backend
    with imageio.get_writer(output_path, fps=args.fps) as writer:
        for filename in image_files:
            print(f"Appending frame: {os.path.basename(filename)}")
            image = imageio.imread(filename)
            writer.append_data(image)
            
    print(f"\nSuccess! Video saved to: {output_path}")

if __name__ == "__main__":
    main()
