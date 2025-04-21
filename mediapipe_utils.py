import math
import cv2

DIVIDING_LINE_LENGTH = 32


def get_distance(points, p_1_index, p_2_index, width, height):
    p_1 = points[p_1_index]
    p_1_x = p_1.x * width
    p_1_y = p_1.y * height

    p_2 = points[p_2_index]
    p_2_x = p_2.x * width
    p_2_y = p_2.y * height

    distance = math.sqrt((p_1_x - p_2_x) ** 2 + (p_1_y - p_2_y) ** 2)

    return distance


def get_horizontal_distance(points, p_1_index, p_2_index, width):
    p_1 = points[p_1_index]
    p_1_x = p_1.x * width

    p_2 = points[p_2_index]
    p_2_x = p_2.x * width

    distance = abs(p_1_x - p_2_x)

    return distance


def get_vertical_distance(points, p_1_index, p_2_index, height):
    p_1 = points[p_1_index]
    p_1_y = p_1.y * height

    p_2 = points[p_2_index]
    p_2_y = p_2.y * height

    distance = abs(p_1_y - p_2_y)

    return distance


def get_eyebrows_symmetry(points, image_height):
    # p_4   - nose tip
    # p_105 - right eyebrow midpoint
    # p_334 - left eyebrow midpoint

    right_eyebrow_dist = get_vertical_distance(points, 4, 105, image_height)
    left_eyebrow_dist = get_vertical_distance(points, 4, 334, image_height)

    if (left_eyebrow_dist > 0) and (right_eyebrow_dist > left_eyebrow_dist):
        eyebrows_symmetry = round(left_eyebrow_dist / right_eyebrow_dist, 2)
    elif (right_eyebrow_dist > 0) and (left_eyebrow_dist > right_eyebrow_dist):
        eyebrows_symmetry = round(right_eyebrow_dist / left_eyebrow_dist, 2)
    elif left_eyebrow_dist == right_eyebrow_dist:
        eyebrows_symmetry = 1
    else:
        eyebrows_symmetry = 'NaN'

    print('-' * DIVIDING_LINE_LENGTH)
    print(f'right eyebrow distance = {right_eyebrow_dist:.2f}')
    print(f'left  eyebrow distance = {left_eyebrow_dist:.2f}')
    print(f'eyebrows symmetry = {eyebrows_symmetry:.2f}')
    print('-' * DIVIDING_LINE_LENGTH)

    return eyebrows_symmetry


def get_eyes_symmetry(points, image_width, image_height):
    # p_4   - nose tip
    # p_159 - right upper eyelid midpoint
    # p_386 - left upper eyelid midpoint

    right_eyelid_dist = get_distance(points, 4, 159, image_width, image_height)
    left_eyelid_dist = get_distance(points, 4, 386, image_width, image_height)

    if (left_eyelid_dist > 0) and (right_eyelid_dist > left_eyelid_dist):
        eyes_symmetry = round(left_eyelid_dist / right_eyelid_dist, 2)
    elif (right_eyelid_dist > 0) and (left_eyelid_dist > right_eyelid_dist):
        eyes_symmetry = round(right_eyelid_dist / left_eyelid_dist, 2)
    elif left_eyelid_dist == right_eyelid_dist:
        eyes_symmetry = 1
    else:
        eyes_symmetry = 'NaN'

    print(f'right eyelid distance = {right_eyelid_dist:.2f}')
    print(f'left  eyelid distance = {left_eyelid_dist:.2f}')
    print(f'eyes symmetry = {eyes_symmetry:.2f}')
    print('-' * DIVIDING_LINE_LENGTH)

    return eyes_symmetry


def get_nose_symmetry(points, image_width, image_height):
    # p_33  - right eye outer corner
    # p_263 - left eye outer corner
    # p_64  - right nose wing
    # p_294 - left nose wing

    right_nose_wing_dist = get_distance(points, 33, 64, image_width, image_height)
    left_nose_wing_dist = get_distance(points, 263, 294, image_width, image_height)

    if (left_nose_wing_dist > 0) and (right_nose_wing_dist > left_nose_wing_dist):
        nose_symmetry = round(left_nose_wing_dist / right_nose_wing_dist, 2)
    elif (right_nose_wing_dist > 0) and (left_nose_wing_dist > right_nose_wing_dist):
        nose_symmetry = round(right_nose_wing_dist / left_nose_wing_dist, 2)
    elif left_nose_wing_dist == right_nose_wing_dist:
        nose_symmetry = 1
    else:
        nose_symmetry = 'NaN'

    print(f'right nose wing distance = {right_nose_wing_dist:.2f}')
    print(f'left  nose wing distance = {left_nose_wing_dist:.2f}')
    print(f'nose symmetry = {nose_symmetry:.2f}')
    print('-' * DIVIDING_LINE_LENGTH)

    return nose_symmetry


def get_mouth_symmetry(points, image_width, image_height):
    # p_33  - right eye outer corner
    # p_263 - left eye outer corner
    # p_61  - mouth right corner
    # p_291 - mouth left corner

    right_mouth_corner_dist = get_distance(points, 33, 61, image_width, image_height)
    left_mouth_corner_dist = get_distance(points, 291, 263, image_width, image_height)

    if (left_mouth_corner_dist > 0) and (right_mouth_corner_dist > left_mouth_corner_dist):
        mouth_symmetry = round(left_mouth_corner_dist / right_mouth_corner_dist, 2)
    elif (right_mouth_corner_dist > 0) and (left_mouth_corner_dist > right_mouth_corner_dist):
        mouth_symmetry = round(right_mouth_corner_dist / left_mouth_corner_dist, 2)
    elif left_mouth_corner_dist == right_mouth_corner_dist:
        mouth_symmetry = 1
    else:
        mouth_symmetry = 'NaN'

    print(f'right mouth corner distance = {right_mouth_corner_dist:.2f}')
    print(f'left  mouth corner distance = {left_mouth_corner_dist:.2f}')
    print(f'mouth symmetry = {mouth_symmetry:.2f}')
    print()

    return mouth_symmetry


def get_face_symmetries(points, image_width, image_height):
    eyebrows_symmetry = get_eyebrows_symmetry(points, image_height)
    eyes_symmetry = get_eyes_symmetry(points, image_width, image_height)
    nose_symmetry = get_nose_symmetry(points, image_width, image_height)
    mouth_symmetry = get_mouth_symmetry(points, image_width, image_height)

    return eyebrows_symmetry, eyes_symmetry, nose_symmetry, mouth_symmetry


def put_image_points(input_image, points,
                     regular_point_radius, interest_point_radius,
                     regular_point_color, interest_point_color, line_color):
    right_eyebrow = [70, 63, 105, 66, 107, 46, 53, 52, 65, 55]
    left_eyebrow = [336, 296, 334, 293, 300, 285, 295, 282, 283, 276]

    right_eye = [33, 7, 163, 144, 145, 153, 154, 155,
                 133, 246, 161, 160, 159, 158, 157, 173]
    left_eye = [263, 249, 390, 373, 374, 380, 381, 382,
                362, 466, 388, 387, 386, 385, 384, 398]

    nose = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97,
            326, 327, 294, 278, 344, 440, 275, 45, 220, 115, 48, 64]

    outer_lips = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375,
                  291, 185, 40, 39, 37, 0, 267, 269, 270, 409]

    contours = right_eyebrow + left_eyebrow + right_eye + left_eye + nose + outer_lips

    right_eyebrow_interest_points = [105]  # right eyebrow midpoint
    left_eyebrow_interest_points = [334]  # left eyebrow midpoint

    right_eye_interest_points = [33, 159]  # right eye outer corner and upper eyelid midpoint
    left_eye_interest_points = [263, 386]  # left eye outer corner and upper eyelid midpoint

    nose_interest_points = [4, 64, 294]  # nose tip, right and left nose wings
    mouth_interest_points = [61, 291]  # right and left mouth corners

    interest_points = right_eyebrow_interest_points + left_eyebrow_interest_points + \
                      right_eye_interest_points + left_eye_interest_points + \
                      nose_interest_points + mouth_interest_points

    height = input_image.shape[0]
    width = input_image.shape[1]

    output_image = input_image.copy()

    for i in contours:
        point = points[i]
        point_x = int(point.x * width)
        point_y = int(point.y * height)
        if i not in interest_points:
            cv2.circle(output_image, (point_x, point_y),
                       regular_point_radius, regular_point_color, -1)

    for i in interest_points:
        point = points[i]
        point_x = int(point.x * width)
        point_y = int(point.y * height)
        cv2.circle(output_image, (point_x, point_y),
                   interest_point_radius, interest_point_color, -1)

    # Nose to eyebrows lines
    cv2.line(output_image, (int(points[4].x * width), int(points[4].y * height)),
             (int(points[105].x * width), int(points[105].y * height)), line_color, 2)
    cv2.line(output_image, (int(points[4].x * width), int(points[4].y * height)),
             (int(points[334].x * width), int(points[334].y * height)), line_color, 2)

    # Nose to eyebrows lines
    cv2.line(output_image, (int(points[4].x * width), int(points[4].y * height)),
             (int(points[159].x * width), int(points[159].y * height)), line_color, 2)
    cv2.line(output_image, (int(points[4].x * width), int(points[4].y * height)),
             (int(points[386].x * width), int(points[386].y * height)), line_color, 2)

    # Eyes to nose lines
    cv2.line(output_image, (int(points[33].x * width), int(points[33].y * height)),
             (int(points[64].x * width), int(points[64].y * height)), line_color, 2)
    cv2.line(output_image, (int(points[263].x * width), int(points[263].y * height)),
             (int(points[294].x * width), int(points[294].y * height)), line_color, 2)

    # Eyes to mouth lines
    cv2.line(output_image, (int(points[33].x * width), int(points[33].y * height)),
             (int(points[61].x * width), int(points[61].y * height)), line_color, 2)
    cv2.line(output_image, (int(points[263].x * width), int(points[263].y * height)),
             (int(points[291].x * width), int(points[291].y * height)), line_color, 2)

    return output_image
