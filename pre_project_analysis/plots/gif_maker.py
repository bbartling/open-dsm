from PIL import Image

# List of month names
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# Create a list to store frames
frames = []

# Load and add each month's image to the frames list
for month in months:
    image_path = f"{month}_avg_load_prof.png"
    try:
        image = Image.open(image_path)
        frames.append(image)
    except FileNotFoundError:
        print(f"Image not found for {month}")

# Save the frames as a GIF with looping and faster duration
frames[0].save('yearly_animation_slow.gif', save_all=True, append_images=frames[1:], loop=0, duration=500)
