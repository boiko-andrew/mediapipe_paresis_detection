import os
import tkinter
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.constants import DISABLED, NORMAL

from mediapipe_get_video_symmetries import get_mediapipe_video_symmetries

video_full_file_name = ''
markup_full_file_name = ''
output_images_file_path = ''
working_dir_path = '/'


def select_video_file():
    filetypes = (
        ('Video files', ['*.mp4', '*.mov']),
        ('All files', '*.*')
    )

    global working_dir_path
    result = fd.askopenfilename(
        title='Выберите видеофайл',
        initialdir=working_dir_path,
        filetypes=filetypes)

    global video_full_file_name
    if len(result) > 0:
        video_full_file_name = result
        working_dir_path = os.path.abspath(result)
        video_label.config(text=video_full_file_name)
        markup_btn['state'] = NORMAL


def select_markup_file():
    filetypes = (
        ('MS Excel files', '*.xlsx'),
        ('All files', '*.*')
    )

    result = fd.askopenfilename(
        title='Выберите файл разметки',
        initialdir=working_dir_path,
        filetypes=filetypes)

    global markup_full_file_name
    if len(result) > 0:
        markup_full_file_name = result
        markup_label.config(text=markup_full_file_name)
        output_images_btn['state'] = NORMAL


def select_output_images_folder():
    result = fd.askdirectory(
        title='Выберите папку для сохранения кадров',
        initialdir=working_dir_path)

    global output_images_file_path
    if len(result) > 0:
        output_images_file_path = result
        output_images_label.config(text=output_images_file_path)
        calculate_btn['state'] = NORMAL


def calculate():
    global progress_var

    progress_var.set('Идет обработка...')
    root.update()

    get_mediapipe_video_symmetries(video_full_file_name, markup_full_file_name, output_images_file_path)
    progress_var.set('Обработка завершена')
    root.update()

    return 0


root = Tk()
root.title('Асимметрия')
root.iconbitmap(default='./_internal/face.ico')
root.geometry('770x230')

video_btn = ttk.Button(text='Видеозапись', command=select_video_file)
video_btn.place(x=20, y=20, width=140, height=30)

markup_btn = ttk.Button(text='Файл разметки', state=DISABLED,
                        command=select_markup_file)
markup_btn.place(x=20, y=70, width=140, height=30)

output_images_btn = ttk.Button(text='Папка для кадров', state=DISABLED,
                               command=select_output_images_folder)
output_images_btn.place(x=20, y=120, width=140, height=30)

calculate_btn = ttk.Button(text='Обработать', state=DISABLED,
                           command=calculate)
calculate_btn.place(x=20, y=170, width=140, height=30)

video_label = ttk.Label(text='...')
video_label.place(x=180, y=20, width=560, height=30)

markup_label = ttk.Label(text='...')
markup_label.place(x=180, y=70, width=560, height=30)

output_images_label = ttk.Label(text='...')
output_images_label.place(x=180, y=120, width=560, height=30)

progress_var = tkinter.StringVar()
progress_label = ttk.Label(textvariable=progress_var)
progress_label.place(x=180, y=170, width=240, height=30)
progress_var.set('Обработка не начата')

root.mainloop()
