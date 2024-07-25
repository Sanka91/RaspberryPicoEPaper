
def get_image_array(path, width, height):

    with open(path, "rb") as f:
        # adjust depending on pixel data offset (130 for example QR CODE)
        f.seek(62)

        bytes_per_row = (width + 7) // 8
        padded_row_size = (bytes_per_row + 3) & ~3
        pixel_data = bytearray()

        for _ in range(height):
            row_data = f.read(bytes_per_row)   # Read the actual pixel data
            pixel_data.extend(row_data)        # Append the pixel data to our bytearray
            f.seek(padded_row_size - bytes_per_row, 1)  # Skip the padding bytes

        return pixel_data
        #
        # header_field = f.read(2)  # Signature (BM)
        # file_size = int.from_bytes(f.read(4), byteorder='little')
        # reserved1 = f.read(2)
        # reserved2 = f.read(2)
        # pixel_array_offset = int.from_bytes(f.read(4), byteorder='little')
        #
        # # DIB Header (BITMAPINFOHEADER)
        # dib_header_size = int.from_bytes(f.read(4), byteorder='little')
        # width = int.from_bytes(f.read(4), byteorder='little')
        # height = int.from_bytes(f.read(4), byteorder='little')
        # planes = int.from_bytes(f.read(2), byteorder='little')
        # bits_per_pixel = int.from_bytes(f.read(2), byteorder='little')
        # compression = int.from_bytes(f.read(4), byteorder='little')
        # image_size = int.from_bytes(f.read(4), byteorder='little')
        # x_pixels_per_meter = int.from_bytes(f.read(4), byteorder='little')
        # y_pixels_per_meter = int.from_bytes(f.read(4), byteorder='little')
        # colors_in_color_table = int.from_bytes(f.read(4), byteorder='little')
        # important_color_count = int.from_bytes(f.read(4), byteorder='little')
        #
        # print("BMP Header:")
        # print(f"Signature: {header_field}")
        # print(f"File Size: {file_size}")
        # print(f"Pixel Data Offset: {pixel_array_offset}")
        #
        # print("DIB Header:")
        # print(f"DIB Header Size: {dib_header_size}")
        # print(f"Image Width: {width}")
        # print(f"Image Height: {height}")
        # print(f"Planes: {planes}")
        # print(f"Bits per Pixel: {bits_per_pixel}")
        # print(f"Compression: {compression}")
        # print(f"Image Size: {image_size}")
        # print(f"X Pixels per Meter: {x_pixels_per_meter}")
        # print(f"Y Pixels per Meter: {y_pixels_per_meter}")
        # print(f"Colors in Color Table: {colors_in_color_table}")
        # print(f"Important Color Count: {important_color_count}")
#
#
#
# #
#
# if __name__ == '__main__':
#     print("Bmp started")
#     get_image_array()