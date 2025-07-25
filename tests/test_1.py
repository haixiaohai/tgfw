import base64, pytesseract
from PIL import Image
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

data = "data:image/png;base64,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"



img_base64 = data.split(",")[1]

img_bytes = base64.b64decode(img_base64)

img = Image.open(BytesIO(img_bytes))

text = pytesseract.image_to_string(img)

print(text.strip().replace(" ", ""))