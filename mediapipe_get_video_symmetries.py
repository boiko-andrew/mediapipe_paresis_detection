import os

import cv2
import ffmpeg
import mediapipe as mp
import numpy as np
import pandas as pd
from pandas import ExcelWriter

from mediapipe_utils import get_exercise_symmetry
from mediapipe_utils import get_face_symmetries
from mediapipe_utils import put_image_points
from mediapipe_utils import put_image_exercise_points

REGULAR_RADIUS = 4  # for regular points
LARGE_RADIUS = 6  # for interest points

WHITE_COLOUR = (255, 255, 255)  # for regular points
RED_COLOUR = (0, 0, 255)  # for interest points
GREEN_COLOUR = (0, 255, 0)  # for connection lines

EYEBROWS_EXERCISES = ['eyebrows_raising', 'eyebrows_frowning', 'rest_state']
EYES_EXERCISES = ['eyes_squeezing', 'forced_eyes_squeezing', 'rest_state', 'blinking']
NOSE_EXERCISES = ['nose_wrinkling', 'rest_state']
MOUTH_EXERCISES = ['lips_struggling', 'letter_i', 'closed_smile',
                   'mouth_opening', 'lower_lip_raising', 'letter_y',
                   'rest_state']
REST_STATE = 'rest_state'


def check_rotation(video_full_file_name):
    try:
        # Fetch video metadata
        metadata = ffmpeg.probe(video_full_file_name)
    except Exception as e:
        print(f'failed to read video: {video_full_file_name}\n'
              f'{e}\n',
              end='',
              flush=True)
        return None
    # Extract rotate info from metadata
    video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
    rotation = int(video_stream.get('tags', {}).get('rotate', 0))

    # Extract rotation info from side_data_list, popular for Apple phones
    side_data_types = video_stream.get('side_data_list', [])

    side_data_rotation = 0
    for side_data_type in side_data_types:
        side_data_rotation = int(side_data_type.get('rotation', 0))
        if side_data_rotation != 0:
            break

    if side_data_rotation != 0:
        rotation -= side_data_rotation

    if rotation == 90:
        rotate_code = cv2.ROTATE_90_CLOCKWISE
    elif rotation == 180:
        rotate_code = cv2.ROTATE_180
    elif rotation == 270:
        rotate_code = cv2.ROTATE_90_COUNTERCLOCKWISE
    else:
        rotate_code = None

    return rotation, rotate_code


def correct_rotation(frame, rotate_code):
    return cv2.rotate(frame, rotate_code)


def get_mediapipe_video_symmetries(video_full_file_name, markup_full_file_name, output_images_file_path):
    results_file_path = os.path.dirname(os.path.abspath(markup_full_file_name))
    results_file_name = os.path.splitext(os.path.basename(markup_full_file_name))[0] + '_results.xlsx'
    results_full_file_name = str(os.path.join(results_file_path, results_file_name))

    markup = pd.read_excel(markup_full_file_name, sheet_name=0)
    patient_name = markup.loc[0, 'patient_name']
    palsied_side = markup.loc[0, 'palsied_side']
    time_point = markup.loc[0, 'time_point']

    markup.insert(loc=6, column='particular_ex', value=np.nan)
    markup.insert(loc=7, column='eyebrows_all', value=np.nan)
    markup.insert(loc=8, column='eyebrows_ex', value=np.nan)
    markup.insert(loc=9, column='eyes_all', value=np.nan)
    markup.insert(loc=10, column='eyes_ex', value=np.nan)
    markup.insert(loc=11, column='nose_all', value=np.nan)
    markup.insert(loc=12, column='nose_ex', value=np.nan)
    markup.insert(loc=13, column='mouth_all', value=np.nan)
    markup.insert(loc=14, column='mouth_ex', value=np.nan)
    markup.insert(loc=15, column='mean_all', value=np.nan)
    markup.insert(loc=16, column='mean_ex', value=np.nan)

    cap = cv2.VideoCapture(video_full_file_name)
    video_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    rotation, rotate_code = check_rotation(video_full_file_name)

    print(f'video height = {video_height:.0f}')
    print(f'video width = {video_width:.0f}')
    print(f'video rotation = {rotation:.0f}')
    print()

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                      static_image_mode=True, refine_landmarks=True)

    read_result = True
    frame_num = 0
    while read_result:
        read_result, frame = cap.read()
        if frame_num in markup['peak_frame'].to_list():
            exercise = markup.loc[markup['peak_frame'] == frame_num, 'exercise'].iloc[0]
            exercise = exercise.strip()

            print('exercise = ' + exercise)
            print('frame number = ' + str(frame_num))

            frame_width, frame_height, _ = frame.shape

            print(f'frame height = {frame_height:.0f}')
            print(f'frame width  = {frame_width:.0f}')

            if rotate_code is not None:
                output_frame = correct_rotation(frame, rotate_code)
            else:
                output_frame = frame

            output_image_file_name = patient_name + '_' + time_point + '_frame_' \
                                     + str(frame_num).zfill(4) + '_' + exercise + '.jpeg'
            output_image_full_file_name = \
                str(os.path.join(output_images_file_path, output_image_file_name))
            cv2.imwrite(output_image_full_file_name, output_frame)

            results = face_mesh.process(cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB))
            frame_landmarks = results.multi_face_landmarks[0].landmark

            # Stationary points for distance calculations
            center_points = [195, 127, 356]

            # Points for "eyebrows_raising" exercise (exercise no. 01)
            eyebrows_raising_right_side_points = [107, 66, 105, 63, 70]
            eyebrows_raising_left_side_points = [336, 296, 334, 293, 300]
            eyebrows_raising_points = eyebrows_raising_right_side_points + eyebrows_raising_left_side_points

            # Points for "eyebrows_frowning" exercise (exercise no. 02)
            eyebrows_frowning_right_side_points = [107, 55, 66, 65]
            eyebrows_frowning_left_side_points = [336, 285, 296, 295]
            eyebrows_frowning_points = eyebrows_frowning_right_side_points + eyebrows_frowning_left_side_points

            # Points for "eyes_squeezing" exercise (exercise no. 03)
            eyes_squeezing_right_side_points = [173, 157, 158, 159, 160, 161, 246, 155, 154, 153,
                                                145, 144, 163, 7]
            eyes_squeezing_left_side_points = [398, 384, 385, 386, 387, 388, 466, 382, 381, 380,
                                               374, 373, 390, 249]
            eyes_squeezing_points = eyes_squeezing_right_side_points + eyes_squeezing_left_side_points

            # Points for "forced_eyes_squeezing" exercise (exercise no. 04)
            forced_eyes_squeezing_right_side_points = [65, 52, 53, 46, 156, 70, 124, 143, 35, 111,
                                                       117, 31, 228, 25, 110, 229, 24, 23, 230, 22,
                                                       231, 26, 232, 233, 118, 119, 120, 121]
            forced_eyes_squeezing_left_side_points = [295, 282, 283, 276, 383, 300, 353, 372, 265, 340,
                                                      346, 261, 448, 255, 339, 449, 254, 253, 450, 252,
                                                      451, 256, 452, 453, 347, 348, 349, 350]
            forced_eyes_squeezing_points = \
                forced_eyes_squeezing_right_side_points + forced_eyes_squeezing_left_side_points

            # Points for "nose_wrinkling" exercise (exercise no. 05)
            nose_wrinkling_right_side_points = [108, 107, 55, 193, 122, 188, 196, 174, 236, 3,
                                                114, 128, 217, 126, 198, 209, 49]
            nose_wrinkling_left_side_points = [337, 336, 285, 417, 351, 412, 419, 399, 456, 248,
                                               343, 357, 437, 355, 420, 429, 279]
            nose_wrinkling_points = nose_wrinkling_right_side_points + nose_wrinkling_left_side_points

            # Points for "lips_struggling" exercise (exercise no. 07)
            lips_struggling_right_side_points = [37, 39, 40, 185, 61, 146, 91, 181, 84]
            lips_struggling_left_side_points = [267, 269, 270, 409, 291, 375, 321, 405, 314]
            lips_struggling_points = lips_struggling_right_side_points + lips_struggling_left_side_points

            # Points for "letter_i" exercise (exercise no. 08)
            letter_i_right_side_points = [203, 206, 216, 207, 205, 36, 50, 123, 117, 76,
                                          61, 185, 186, 57]
            letter_i_left_side_points = [423, 426, 436, 427, 425, 266, 280, 352, 346, 306,
                                         291, 409, 410, 287]
            letter_i_points = letter_i_right_side_points + letter_i_left_side_points

            # Points for "closed_smile" exercise (exercise no. 09)
            closed_smile_right_side_points = [207, 187, 147, 213, 192]
            closed_smile_left_side_points = [427, 411, 376, 433, 416]
            closed_smile_points = closed_smile_right_side_points + closed_smile_left_side_points

            # Points for "mouth_opening" exercise (exercise no. 10)
            mouth_opening_right_side_points = [37, 39, 40, 185, 92, 203, 143, 126, 217, 114,
                                               146, 91, 181, 84, 7, 106, 104, 162, 194, 211,
                                               32, 83, 201]
            mouth_opening_left_side_points = [267, 269, 270, 409, 322, 423, 372, 355, 437, 343,
                                              375, 321, 405, 314, 249, 335, 333, 389, 418, 431,
                                              262, 313, 421]
            mouth_opening_points = mouth_opening_right_side_points + mouth_opening_left_side_points

            # Points for "cheeks_puffing" exercise (exercise no. 11)
            cheeks_puffing_right_side_points = [207, 187, 147, 213, 192, 205, 50, 123, 214]
            cheeks_puffing_left_side_points = [427, 411, 376, 433, 416, 425, 280, 352, 434]
            cheeks_puffing_points = cheeks_puffing_right_side_points + cheeks_puffing_left_side_points

            # Points for "lower_lip_raising" exercise (exercise no. 12)
            lower_lip_raising_right_side_points = [61, 146, 91, 181, 84, 43, 106, 182, 204, 194,
                                                   211, 32, 203, 171, 140, 170, 159, 210]
            lower_lip_raising_left_side_points = [291, 375, 321, 405, 314, 273, 335, 406, 424, 418,
                                                  431, 262, 423, 396, 369, 395, 386, 430]
            lower_lip_raising_points = lower_lip_raising_right_side_points + lower_lip_raising_left_side_points

            # Points for "letter_y" exercise (exercise no. 13)
            letter_y_right_side_points = [43, 57, 61, 76, 202, 212, 210, 214, 211, 170,
                                          140, 150, 169, 136, 172, 138]
            letter_y_left_side_points = [273, 291, 291, 306, 422, 432, 430, 434, 431, 395,
                                         369, 379, 394, 365, 397, 367]
            letter_y_points = letter_y_right_side_points + letter_y_left_side_points

            # Points for "rest_state" (this is not an exercise and so has no number)
            rest_state_right_side_points = list(set(eyebrows_raising_right_side_points +
                                                    eyebrows_frowning_right_side_points +
                                                    eyes_squeezing_right_side_points +
                                                    forced_eyes_squeezing_right_side_points +
                                                    nose_wrinkling_right_side_points +
                                                    lips_struggling_right_side_points +
                                                    letter_i_right_side_points +
                                                    closed_smile_right_side_points +
                                                    mouth_opening_right_side_points +
                                                    cheeks_puffing_right_side_points +
                                                    lower_lip_raising_right_side_points +
                                                    letter_y_right_side_points
                                                    ))
            rest_state_left_side_points = list(set(eyebrows_raising_left_side_points +
                                                   eyebrows_frowning_left_side_points +
                                                   eyes_squeezing_left_side_points +
                                                   forced_eyes_squeezing_left_side_points +
                                                   nose_wrinkling_left_side_points +
                                                   lips_struggling_left_side_points +
                                                   letter_i_left_side_points +
                                                   closed_smile_left_side_points +
                                                   mouth_opening_left_side_points +
                                                   cheeks_puffing_left_side_points +
                                                   lower_lip_raising_left_side_points +
                                                   letter_y_left_side_points
                                                   ))
            rest_state_points = rest_state_right_side_points + rest_state_left_side_points

            if exercise == 'eyebrows_raising':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              eyebrows_raising_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'eyebrows_frowning':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              eyebrows_frowning_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'eyes_squeezing':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              eyes_squeezing_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'forced_eyes_squeezing':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              forced_eyes_squeezing_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'nose_wrinkling':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              nose_wrinkling_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'lips_struggling':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              lips_struggling_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'letter_i':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              letter_i_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'closed_smile':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              closed_smile_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'mouth_opening':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              mouth_opening_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'cheeks_puffing':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              cheeks_puffing_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'lower_lip_raising':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              lower_lip_raising_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'letter_y':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              letter_y_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            elif exercise == 'rest_state':
                image_with_points = \
                    put_image_exercise_points(output_frame, frame_landmarks,
                                              rest_state_points, center_points,
                                              REGULAR_RADIUS, LARGE_RADIUS, WHITE_COLOUR, RED_COLOUR)
            else:
                image_with_points = put_image_points(output_frame, frame_landmarks, REGULAR_RADIUS, LARGE_RADIUS,
                                                     WHITE_COLOUR, RED_COLOUR, GREEN_COLOUR)

            image_with_points_width, image_with_points_height, _ = image_with_points.shape

            eyebrows_symmetry, eyes_symmetry, nose_symmetry, mouth_symmetry = \
                get_face_symmetries(frame_landmarks, image_with_points_width, image_with_points_height)

            # Exercise no. 01
            eyebrows_raising_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      eyebrows_raising_right_side_points, eyebrows_raising_left_side_points)

            # Exercise no. 02
            eyebrows_frowning_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      eyebrows_frowning_right_side_points, eyebrows_frowning_left_side_points)

            # Exercise no. 03
            eyes_squeezing_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      eyes_squeezing_right_side_points, eyes_squeezing_left_side_points)

            # Exercise no. 04
            forced_eyes_squeezing_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      forced_eyes_squeezing_right_side_points,
                                      forced_eyes_squeezing_left_side_points)

            # Exercise no. 05
            nose_wrinkling_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      nose_wrinkling_right_side_points, nose_wrinkling_left_side_points)

            # Exercise no. 07
            lips_struggling_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      lips_struggling_right_side_points, lips_struggling_left_side_points)

            # Exercise no. 08
            letter_i_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      letter_i_right_side_points, letter_i_left_side_points)

            # Exercise no. 09
            closed_smile_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      closed_smile_right_side_points, closed_smile_left_side_points)

            # Exercise no. 10
            mouth_opening_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      mouth_opening_right_side_points, mouth_opening_left_side_points)

            # Exercise no. 11
            cheeks_puffing_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      cheeks_puffing_right_side_points, cheeks_puffing_left_side_points)

            # Exercise no. 12
            lower_lip_raising_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      lower_lip_raising_right_side_points, lower_lip_raising_left_side_points)

            # Exercise no. 13
            letter_y_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      letter_y_right_side_points, letter_y_left_side_points)

            rest_state_symmetry = \
                get_exercise_symmetry(frame_landmarks,
                                      image_with_points_width, image_with_points_height, center_points,
                                      rest_state_right_side_points, rest_state_left_side_points)

            mean_ex = 0

            markup.loc[markup['peak_frame'] == frame_num, 'eyebrows_all'] = eyebrows_symmetry
            if exercise in EYEBROWS_EXERCISES:
                markup.loc[markup['peak_frame'] == frame_num, 'eyebrows_ex'] = eyebrows_symmetry
                if exercise != REST_STATE:
                    mean_ex = eyebrows_symmetry
            else:
                markup.loc[markup['peak_frame'] == frame_num, 'eyebrows_ex'] = np.nan

            markup.loc[markup['peak_frame'] == frame_num, 'eyes_all'] = eyes_symmetry
            if exercise in EYES_EXERCISES:
                markup.loc[markup['peak_frame'] == frame_num, 'eyes_ex'] = eyes_symmetry
                if exercise != REST_STATE:
                    mean_ex = eyes_symmetry
            else:
                markup.loc[markup['peak_frame'] == frame_num, 'eyes_ex'] = np.nan

            markup.loc[markup['peak_frame'] == frame_num, 'nose_all'] = nose_symmetry
            if exercise in NOSE_EXERCISES:
                markup.loc[markup['peak_frame'] == frame_num, 'nose_ex'] = nose_symmetry
                if exercise != REST_STATE:
                    mean_ex = nose_symmetry
            else:
                markup.loc[markup['peak_frame'] == frame_num, 'nose_ex'] = np.nan

            markup.loc[markup['peak_frame'] == frame_num, 'mouth_all'] = mouth_symmetry
            if exercise in MOUTH_EXERCISES:
                markup.loc[markup['peak_frame'] == frame_num, 'mouth_ex'] = mouth_symmetry
                if exercise != REST_STATE:
                    mean_ex = mouth_symmetry
            else:
                markup.loc[markup['peak_frame'] == frame_num, 'mouth_ex'] = np.nan

            mean_all = round((eyebrows_symmetry + eyes_symmetry +
                              nose_symmetry + mouth_symmetry) / 4, 2)
            markup.loc[markup['peak_frame'] == frame_num, 'mean_all'] = mean_all

            if exercise == REST_STATE:
                mean_ex = mean_all
            markup.loc[markup['peak_frame'] == frame_num, 'mean_ex'] = mean_ex

            if exercise == 'eyebrows_raising':
                markup.loc[markup['exercise'] == exercise, 'particular_ex'] = eyebrows_raising_symmetry

            if exercise == 'eyebrows_frowning':
                markup.loc[markup['exercise'] == exercise, 'particular_ex'] = eyebrows_frowning_symmetry

            if exercise == 'eyes_squeezing':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = eyes_squeezing_symmetry

            if exercise == 'forced_eyes_squeezing':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = forced_eyes_squeezing_symmetry

            if exercise == 'nose_wrinkling':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = nose_wrinkling_symmetry

            if exercise == 'lips_struggling':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = lips_struggling_symmetry

            if exercise == 'letter_i':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = letter_i_symmetry

            if exercise == 'closed_smile':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = closed_smile_symmetry

            if exercise == 'mouth_opening':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = mouth_opening_symmetry

            if exercise == 'cheeks_puffing':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = cheeks_puffing_symmetry

            if exercise == 'lower_lip_raising':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = lower_lip_raising_symmetry

            if exercise == 'letter_y':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = letter_y_symmetry

            if exercise == 'rest_state':
                markup.loc[markup['peak_frame'] == frame_num, 'particular_ex'] = rest_state_symmetry

            # if not (video_height == image_with_points_height and video_width == image_with_points_width):
            #     output_image_with_points = cv2.rotate(image_with_points, cv2.ROTATE_90_CLOCKWISE)
            # else:
            #     output_image_with_points = image_with_points

            output_image_with_points = image_with_points

            image_with_points_file_name = patient_name + '_' + time_point + '_frame_' \
                                          + str(frame_num).zfill(4) + '_' + exercise \
                                          + '_mediapipe_points' + '.jpeg'
            image_with_points_full_file_name = \
                str(os.path.join(output_images_file_path, image_with_points_file_name))

            cv2.imwrite(image_with_points_full_file_name, output_image_with_points)
        frame_num += 1
    cap.release()

    # Calculate mean value for output columns
    markup.loc[len(markup)] = [patient_name, palsied_side, time_point, 'mean_value', '', '',
                               round(markup['particular_ex'].mean(), 2),
                               round(markup['eyebrows_all'].mean(), 2),
                               round(markup['eyebrows_ex'].mean(), 2),
                               round(markup['eyes_all'].mean(), 2),
                               round(markup['eyes_ex'].mean(), 2),
                               round(markup['nose_all'].mean(), 2),
                               round(markup['nose_ex'].mean(), 2),
                               round(markup['mouth_all'].mean(), 2),
                               round(markup['mouth_ex'].mean(), 2),
                               round(markup['mean_all'].mean(), 2),
                               round(markup['mean_ex'].mean(), 2)]

    with ExcelWriter(results_full_file_name) as writer:
        markup.to_excel(writer, sheet_name='results')

    return markup.iloc[[-1]]
