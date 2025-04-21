import os

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from pandas import ExcelWriter

from mediapipe_utils import get_face_symmetries
from mediapipe_utils import put_image_points

REGULAR_RADIUS = 4  # for regular points
LARGE_RADIUS = 6  # for interest points

WHITE_COLOUR = (255, 255, 255)  # for regular points
RED_COLOUR = (0, 0, 255)        # for interest points
GREEN_COLOUR = (0, 255, 0)      # for connection lines

EYEBROWS_EXERCISES = ['eyebrows_raising', 'eyebrows_frowning', 'rest_state']
EYES_EXERCISES = ['eyes_squeezing', 'forced_eyes_squeezing', 'rest_state', 'blinking']
NOSE_EXERCISES = ['nose_wrinkling', 'rest_state']
MOUTH_EXERCISES = ['lips_struggling', 'letter_i', 'closed_smile',
                   'mouth_opening', 'lower_lip_raising', 'rest_state']
REST_STATE = 'rest_state'


def get_mediapipe_video_symmetries(video_full_file_name, markup_full_file_name, output_images_file_path):
    results_file_path = os.path.dirname(os.path.abspath(markup_full_file_name))
    results_file_name = os.path.splitext(os.path.basename(markup_full_file_name))[0] + '_results.xlsx'
    results_full_file_name = str(os.path.join(results_file_path, results_file_name))

    markup = pd.read_excel(markup_full_file_name, sheet_name=0)
    patient_name = markup.loc[0, 'patient_name']
    palsied_side = markup.loc[0, 'palsied_side']
    time_point = markup.loc[0, 'time_point']

    markup.insert(loc=6, column='eyebrows_all', value='')
    markup.insert(loc=7, column='eyebrows_ex', value='')
    markup.insert(loc=8, column='eyes_all', value='')
    markup.insert(loc=9, column='eyes_ex', value='')
    markup.insert(loc=10, column='nose_all', value='')
    markup.insert(loc=11, column='nose_ex', value='')
    markup.insert(loc=12, column='mouth_all', value='')
    markup.insert(loc=13, column='mouth_ex', value='')
    markup.insert(loc=14, column='mean_all', value='')
    markup.insert(loc=15, column='mean_ex', value='')

    cap = cv2.VideoCapture(video_full_file_name)
    video_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    video_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                      static_image_mode=True, refine_landmarks=True)

    read_result = True
    frame_num = 0
    while read_result:
        read_result, frame = cap.read()
        if frame_num in markup['peak_frame'].to_list():
            exercise = markup.loc[markup['peak_frame'] == frame_num, 'exercise'].iloc[0]

            print('exercise = ' + exercise)
            print('frame number = ' + str(frame_num))

            frame_width, frame_height, _ = frame.shape
            if not (video_height == frame_height and video_width == frame_width):
                output_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            else:
                output_frame = frame

            output_image_file_name = patient_name + '_' + time_point + '_frame_' \
                                     + str(frame_num).zfill(4) + '_' + exercise + '.jpeg'
            output_image_full_file_name = \
                str(os.path.join(output_images_file_path, output_image_file_name))
            cv2.imwrite(output_image_full_file_name, output_frame)

            results = face_mesh.process(cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB))
            frame_landmarks = results.multi_face_landmarks[0].landmark
            image_with_points = put_image_points(output_frame, frame_landmarks, REGULAR_RADIUS, LARGE_RADIUS,
                                                 WHITE_COLOUR, RED_COLOUR, GREEN_COLOUR)

            image_with_points_width, image_with_points_height, _ = image_with_points.shape

            eyebrows_symmetry, eyes_symmetry, nose_symmetry, mouth_symmetry = \
                get_face_symmetries(frame_landmarks, image_with_points_width, image_with_points_height)

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

            if not (video_height == image_with_points_height and video_width == image_with_points_width):
                output_image_with_points = cv2.rotate(image_with_points, cv2.ROTATE_90_CLOCKWISE)
            else:
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

    return 0
