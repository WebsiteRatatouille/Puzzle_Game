from PIL import Image
import os



image_path = "assets/img/cat.png"

def slice_image(image_path, output_folder, rows=4, cols=4):
    
    img = Image.open(image_path)
    width, height = img.size

    tile_width = width // cols
    tile_height = height // rows

    
    os.makedirs(output_folder, exist_ok=True)

    count = 1
    for row in range(rows):
        for col in range(cols):
            left = col * tile_width
            top = row * tile_height
            right = left + tile_width
            bottom = top + tile_height

            # cut tile
            tile = img.crop((left, top, right, bottom))

           
            if count < rows * cols:
                tile.save(os.path.join(output_folder, f"{count}.png"))
                print(f"Saved tile {count}")
            count += 1

if __name__ == "__main__":
    slice_image(image_path, "assets/tiles", rows=4, cols=4)





