import cv2


def resize_image (input_image, resize_factor):
    height = input_image.shape[0]
    width = input_image.shape[1]

    resized_height = int(height / resize_factor)
    resized_width = int(width / resize_factor)
    resized_shape = (resized_width, resized_height)

    output_image = cv2.resize(input_image, resized_shape, interpolation=cv2.INTER_LINEAR)

    return output_image
