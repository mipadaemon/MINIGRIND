from PIL import Image

# Load your PNG file
img = Image.open("minigrind_icon.png")

# Resize to 256x256
img = img.resize((256, 256), Image.LANCZOS)

# Save as .ico
img.save("output.ico", format="ICO")
