from io import BytesIO

from PIL import Image, ImageOps


def main():

    # Open as PNG and apply white background
    image = Image.open("/images/Arrow_up_new.bmp").convert("RGBA")
    background = Image.new("RGB", image.size, (255, 255, 255))
    background.paste(image, mask=image.split()[3])

    # Convert to grayscale and apply threshold to convert grayscale to binary
    grayscale_image = background.convert("L")
    binary_img = grayscale_image.point(lambda p: 255 if p > 250 else 0)
    #inverted_img = Image.eval(binary_img, lambda x: 255 - x)

    # Convert to black/white BMP
    final_bmp = binary_img.convert("1")
    resized_image = final_bmp.resize((30, 30))
    flipped_image = ImageOps.flip(resized_image)

    flipped_image.save("/images/Arrow_up_new_new.bmp")

if __name__ == '__main__':
    main()
