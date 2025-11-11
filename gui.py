import os
import tkinter
from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.constants import DISABLED, NORMAL

from mediapipe_get_video_symmetries import get_mediapipe_video_symmetries
from batch_utils import get_mediapipe_video_symmetries_batch

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


def select_batch_folder():
    global working_dir_path
    result = fd.askdirectory(
        title='Выберите папку для массовой обработки',
        initialdir=working_dir_path)

    if len(result) > 0:
        working_dir_path = result
        batch_folder_label.config(text=result)
        batch_calculate_btn['state'] = NORMAL


def calculate():
    global progress_var

    progress_var.set('Идет обработка...')
    root.update()

    get_mediapipe_video_symmetries(video_full_file_name, markup_full_file_name, output_images_file_path)
    progress_var.set('Обработка завершена')
    root.update()

    return 0


def batch_calculate():
    global batch_progress_var

    batch_progress_var.set('Идет массовая обработка...')
    root.update()

    folder_path = batch_folder_label.cget("text")
    if not folder_path or folder_path == "...":
        batch_progress_var.set('Не указана папка для обработки')
        root.update()
        return 1

    def progress_callback(current: int, total: int):
        if total > 0:
            batch_progress_var.set(f'Прогресс обработки: {current} из {total}')
        else:
            batch_progress_var.set('Нет папок для обработки')
        root.update()

    try:
        get_mediapipe_video_symmetries_batch(folder_path, progress_callback=progress_callback)
        batch_progress_var.set('Массовая обработка завершена')
        root.update()
        return 0
    except Exception as e:
        batch_progress_var.set(f'Ошибка: {str(e)}')
        root.update()
        return 1


root = Tk()
root.title('Асимметрия')
root.iconbitmap(default='./_internal/face.ico')
root.geometry('770x300')

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

single_frame = Frame(notebook)
batch_frame = Frame(notebook)

notebook.add(single_frame, text='Обычная загрузка')
notebook.add(batch_frame, text='Массовая загрузка')

#Вкладка "Обычная загрузка"
video_btn = ttk.Button(single_frame, text='Видеозапись', command=select_video_file)
video_btn.place(x=20, y=20, width=140, height=30)

markup_btn = ttk.Button(single_frame, text='Файл разметки', state=DISABLED,
                        command=select_markup_file)
markup_btn.place(x=20, y=70, width=140, height=30)

output_images_btn = ttk.Button(single_frame, text='Папка для кадров', state=DISABLED,
                               command=select_output_images_folder)
output_images_btn.place(x=20, y=120, width=140, height=30)

calculate_btn = ttk.Button(single_frame, text='Обработать', state=DISABLED,
                           command=calculate)
calculate_btn.place(x=20, y=220, width=140, height=30)

video_label = ttk.Label(single_frame, text='...')
video_label.place(x=180, y=20, width=560, height=30)

markup_label = ttk.Label(single_frame, text='...')
markup_label.place(x=180, y=70, width=560, height=30)

output_images_label = ttk.Label(single_frame, text='...')
output_images_label.place(x=180, y=120, width=560, height=30)

progress_var = tkinter.StringVar()
progress_label = ttk.Label(single_frame, textvariable=progress_var)
progress_label.place(x=180, y=220, width=240, height=30)
progress_var.set('Обработка не начата')

#Вкладка "Массовая загрузка"
batch_select_folder_btn = ttk.Button(batch_frame, text='Общая папка', command=select_batch_folder)
batch_select_folder_btn.place(x=20, y=20, width=140, height=30)

batch_calculate_btn = ttk.Button(batch_frame, text='Обработать', state=DISABLED,
                                 command=batch_calculate)
batch_calculate_btn.place(x=20, y=220, width=140, height=30)

batch_folder_label = ttk.Label(batch_frame, text='...', wraplength=250)
batch_folder_label.place(x=180, y=20, width=560, height=30)

batch_progress_var = tkinter.StringVar()
batch_progress_label = ttk.Label(batch_frame, textvariable=batch_progress_var, wraplength=250)
batch_progress_label.place(x=180, y=220, width=240, height=30)
batch_progress_var.set('Массовая обработка не начата')

structure_label = ttk.Label(batch_frame, text="Структура папки для массовой обработки:",
                           font=('Arial', 10, 'bold'))
structure_label.place(x=440, y=10, width=300, height=25)

structure_text = Text(batch_frame, wrap=WORD, font=('Courier New', 9),
                     bg='#f0f0f0', relief=SOLID, borderwidth=0)
structure_text.place(x=440, y=30, width=320, height=220)

structure_example = """
Общая папка
├── Папка пациента 1
│   ├── Подпапка after
│   │   ├── видео.mp4
│   │   ├── разметка.xlsx
│   │   └── папка для изображений
│   └── Подпапка before
└── Папка пациента 2
└── ...
└── Папка пациента N

Названия файлов и папок могут быть любыми
"""

structure_text.insert('1.0', structure_example)
structure_text.config(state=DISABLED)

root.mainloop()
