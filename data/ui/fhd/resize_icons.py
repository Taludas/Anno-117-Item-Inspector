import os
from PIL import Image

def process_icons(target_size=(128, 128), delete_original=True):
    # Get the directory where the script is located
    root_dir = os.path.dirname(os.path.realpath(__file__))

    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".png"):
                png_path = os.path.join(subdir, file)
                # Create the new filename by swapping the extension
                webp_path = os.path.splitext(png_path)[0] + ".webp"

                try:
                    with Image.open(png_path) as img:
                        # 1. Resize
                        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)

                        # 2. Convert and Save as WebP
                        # 'lossless=True' is great for icons to keep them crisp
                        resized_img.save(webp_path, "WEBP", lossless=True)
                        print(f"Converted: {file} -> {os.path.basename(webp_path)}")

                    # 3. Optional: Remove the old PNG
                    if delete_original:
                        os.remove(png_path)

                except Exception as e:
                    print(f"Error processing {png_path}: {e}")

if __name__ == "__main__":
    # Change delete_original to True if you want to swap PNGs for WebPs entirely
    process_icons(delete_original=False)
    print("\nProcessing complete!")