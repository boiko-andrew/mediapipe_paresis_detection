import math
import cv2
import numpy as np


def get_distance(points, p_1_index, p_2_index, image_width, image_height):
    p_1 = points[p_1_index]
    p_1_x = p_1.x * image_width
    p_1_y = p_1.y * image_height

    p_2 = points[p_2_index]
    p_2_x = p_2.x * image_width
    p_2_y = p_2.y * image_height

    distance = math.sqrt((p_1_x - p_2_x) ** 2 + (p_1_y - p_2_y) ** 2)

    return distance


def get_eyes_symmetry(points, image_width, image_height):
    # Right EAR (Eye Aspect Ratio)
    dist_160_to_144 = get_distance(points, 160, 144, image_width, image_height)
    dist_158_to_153 = get_distance(points, 158, 153, image_width, image_height)
    dist_33_to_133 = get_distance(points, 33, 133, image_width, image_height)
    if dist_33_to_133 != 0:
        right_ear = (dist_160_to_144 + dist_158_to_153) / (2 * dist_33_to_133)
    else:
        right_ear = np.nan

    # Left EAR (Eye Aspect Ratio)
    dist_373_to_387 = get_distance(points, 373, 387, image_width, image_height)
    dist_380_to_385 = get_distance(points, 380, 385, image_width, image_height)
    dist_263_to_362 = get_distance(points, 263, 362, image_width, image_height)
    if dist_263_to_362 != 0:
        left_ear = (dist_373_to_387 + dist_380_to_385) / (2 * dist_263_to_362)
    else:
        left_ear = np.nan

    if (not np.isnan(right_ear)) and (right_ear != 0) and (not np.isnan(left_ear)) and (left_ear != 0):
        eyes_symmetry = right_ear / left_ear
        eyes_symmetry = round(eyes_symmetry, 2)
    else:
        eyes_symmetry = np.nan

    return eyes_symmetry


def get_eyebrows_symmetry(points, image_width, image_height):
    # p_164 is point between nose and mouth
    right_eyebrow = [70, 63, 105, 66, 107, 46, 53, 52, 65, 55]
    right_eyebrow_dist = 0
    for p_index in right_eyebrow:
        right_eyebrow_dist += get_distance(points, 164, p_index, image_width, image_height)
    right_eyebrow_dist = right_eyebrow_dist / len(right_eyebrow)

    left_eyebrow = [336, 296, 334, 293, 300, 285, 295, 282, 283, 276]
    left_eyebrow_dist = 0
    for p_index in left_eyebrow:
        left_eyebrow_dist += get_distance(points, 164, p_index, image_width, image_height)
    left_eyebrow_dist = left_eyebrow_dist / len(left_eyebrow)

    if ((not np.isnan(right_eyebrow_dist)) and (right_eyebrow_dist != 0)
            and (not np.isnan(left_eyebrow_dist)) and (left_eyebrow_dist != 0)):
        eyebrows_symmetry = right_eyebrow_dist / left_eyebrow_dist
        eyebrows_symmetry = round(eyebrows_symmetry, 2)
    else:
        eyebrows_symmetry = np.nan

    return eyebrows_symmetry


def get_nose_symmetry (points, image_width, image_height):
    right_nose_wing_dist = get_distance(points, 33, 64, image_width, image_height)
    left_nose_wing_dist = get_distance(points, 263, 294, image_width, image_height)

    if ((not np.isnan(right_nose_wing_dist)) and (right_nose_wing_dist != 0)
            and (not np.isnan(left_nose_wing_dist)) and (left_nose_wing_dist != 0)):
        nose_symmetry = right_nose_wing_dist / left_nose_wing_dist
        nose_symmetry = round(nose_symmetry, 2)
    else:
        nose_symmetry = np.nan

    return nose_symmetry


def get_mouth_symmetry (points, image_width, image_height):
    right_mouth_corner_dist = get_distance(points, 33, 61, image_width, image_height)
    left_mouth_corner_dist = get_distance(points, 291, 263, image_width, image_height)
    if ((not np.isnan(right_mouth_corner_dist)) and (right_mouth_corner_dist != 0)
            and (not np.isnan(left_mouth_corner_dist)) and (left_mouth_corner_dist != 0)):
        mouth_symmetry = right_mouth_corner_dist / left_mouth_corner_dist
        mouth_symmetry = round(mouth_symmetry, 2)
    else:
        mouth_symmetry = np.nan

    return mouth_symmetry


def get_face_symmetries(points, image_width, image_height):
    eyebrows_symmetry = get_eyebrows_symmetry(points, image_width, image_height)
    eyes_symmetry = get_eyes_symmetry(points, image_width, image_height)
    nose_symmetry = get_nose_symmetry(points, image_width, image_height)
    mouth_symmetry = get_mouth_symmetry(points, image_width, image_height)

    return eyebrows_symmetry, eyes_symmetry, nose_symmetry, mouth_symmetry


def put_image_points(input_image, points,
                     regular_point_radius, interest_point_radius,
                     regular_point_color, interest_point_color):
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

    right_eyebrow_interest_points = [105]   # right eyebrow midpoint
    left_eyebrow_interest_points = [334]    # left eyebrow midpoint

    right_eye_interest_points = [33]        # right eye outer corner
    left_eye_interest_points = [263]        # left eye outer corner

    nose_interest_points = [64, 294]        # right and left nose wings
    nasospinale_interest_points = [164]     # point between nose and mouth
    mouth_interest_points = [61, 291]       # right and left mouth corners

    interest_points = right_eyebrow_interest_points + left_eyebrow_interest_points + \
        right_eye_interest_points + left_eye_interest_points + \
        nose_interest_points + nasospinale_interest_points + mouth_interest_points

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

    return output_image
