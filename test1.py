import pytesseract
from PIL import Image
from PIL import ImageFilter

# Tesseract Setup
pytesseract.pytesseract.tesseract_cmd = 'tesseract.exe'

# Image Path
image_path = r'cropped_text_area.png'
#image_path = r'assets\img\confirmselection.png'

try:
    # Open the image
    image = Image.open(image_path)
    
    # Extract text from the image
    denoised_image = image.filter(ImageFilter.MedianFilter(size=3))
    text = pytesseract.image_to_string(denoised_image)
    
    # Print the extracted text
    print("Detected Text:")
    print("-" * 50)
    print(text)
    print("-" * 50)

except FileNotFoundError:
    print(f"Error: The file '{image_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")
