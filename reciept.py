import cv2
import pytesseract
import csv
import re

def prune_after_cents(line):
    match = re.search(r'\.\d{2}', line)
    if match:
        end_position = match.end()
        return line[:end_position]
    else:
        return line

# Function to crop the white contour, assumed to be the receipt
def crop_receipt(image):
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define range for white color
    lower_white = (0, 0, 180)
    upper_white = (140, 255, 255)
    
    # Threshold the image to get only white regions
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return image
    
    # Assume the largest white contour is the receipt
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    return image[y:y+h, x:x+w]

# Read the image
img = cv2.imread('/Users/antonyrainchik/Desktop/A20AD90B-09CC-4D83-9DF9-B2DFF9D98FC8.JPG')

# Crop the receipt from the image
cropped_img = crop_receipt(img)

# Show the original image
cv2.imshow('Original Image', img)

# Show the cropped image
cv2.imshow('Cropped Image', cropped_img)

# Extract text using pytesseract
text = pytesseract.image_to_string(cropped_img)
#print("Extracted Text:")
#print("---------------")
#print(text)

# Initialize item and prices lists
items = []
prices = []

# Parse the text line by line
for line in text.split('\n'):
    if '$' in line:
        words = line.split('$')
        items.append(words[0])
        words[1] = words[1].replace(' ','.')
        words[1] = words[1].replace('..','.')
        words[1] = words[1].replace(',','.')
        words[1] = prune_after_cents(words[1])
        prices.append(words[1])
        

# Create a CSV file
with open('receipt_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Item", "Price"])
    for item, price in zip(items, prices):
        writer.writerow([item, price])

print('CSV file has been created.')

# Wait until a key is pressed
cv2.waitKey(0)

# Destroy all OpenCV windows
cv2.destroyAllWindows()
