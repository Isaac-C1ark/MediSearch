from PIL import Image

path = r"Path to your folder"

img = Image.open(path).convert("RGBA")

small_img = img.resize((40, 40), Image.LANCZOS)

small_img.save(r"Path of your destination folder")
