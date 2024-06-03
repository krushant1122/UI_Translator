import cv2
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from googletrans import Translator

# Path to tesseract executable
pytesseract.pytesseract_cmd = '/opt/homebrew/bin/tesseract'

def translate_text(text, dest_lang):
    try:
        translator = Translator()
        translated_text = translator.translate(text, dest=dest_lang).text
        return translated_text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def draw_translated_text(draw, text, position, box_size, font_path, fill=(0, 0, 0)):
    # Start with a large font size and reduce until the text fits in the box
    font_size = box_size[1]
    font = ImageFont.truetype(font_path, font_size)
    
    # Reduce the font size until the text fits within the box
    while True:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        if text_width <= box_size[0] or font_size <= 1:
            break
        font_size -= 1
        font = ImageFont.truetype(font_path, font_size)
    
    draw.text(position, text, font=font, fill=fill)

def translate_image(image_path, dest_lang='hi'):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not open or find the image '{image_path}'. Please check the path and try again.")
        return

    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Use pytesseract to do OCR on the image
    text_data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)
    
    # Initialize the translator
    translator = Translator()
    
    # Copy the image to modify it
    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)
    # Use a Unicode font that supports Hindi and Gujarati
    font_path = "NotoSans-Regular.ttf"  # Adjust the path to your font file

    for i, word in enumerate(text_data['text']):
        if word.strip():  # Skip empty strings
            x, y, w, h = text_data['left'][i], text_data['top'][i], text_data['width'][i], text_data['height'][i]
            translated_word = translate_text(word, dest_lang)
            draw.rectangle([(x, y), (x + w, y + h)], fill=(255, 255, 255))  # White out the original text
            draw_translated_text(draw, translated_word, (x, y), (w, h), font_path)  # Draw the translated text
    
    # Save the modified image
    translated_image_path = 'translated_image.png'
    img_pil.save(translated_image_path)
    print(f"Translated image saved as {translated_image_path}")

# Example usage
translate_image('/Users/krushant/UI_Translator/img1.jpg', 'hi')  # 'hi' for Hindi, 'gu' for Gujarati
