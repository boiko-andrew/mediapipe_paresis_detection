import pandas as pd
from pathlib import Path
from typing import Callable

from mediapipe_get_video_symmetries import get_mediapipe_video_symmetries

DIVIDER = '=' * 70

VIDEO_EXTENSIONS = {'.mp4', '.mov'}
EXCEL_EXTENSIONS = {'.xlsx'}


def get_mediapipe_video_symmetries_batch(
        folder_path: str,
        progress_callback: Callable[[int, int], None] | None = None
) -> None:
    """
    Обрабатывает все подпапки пациентов в указанной директории и создает файлы результатов.
    Опционально возвращает прогресс обработки.
    """
    root_path = Path(folder_path)

    if not root_path.is_dir():
        print(f"Предупреждение: Указанный путь не является папкой: {folder_path}")
        return

    patient_dirs = [d for d in root_path.iterdir() if d.is_dir()]
    total_dirs = len(patient_dirs)
    if total_dirs == 0:
        print("Не найдено папок для обработки в директории: {folder_path}")
        return

    print(f"Массовая обработка пациентов. Всего: {total_dirs}")
    all_last_rows = []

    for idx, patient_dir in enumerate(patient_dirs):
        if progress_callback:
            progress_callback(idx, total_dirs)

        patient_last_rows = []

        for target_dir in patient_dir.iterdir():
            if not target_dir.is_dir():
                continue

            print(DIVIDER)
            print(f"Обработка пациента: {patient_dir.name}")
            print(f"Обработка папки: {target_dir.name}")

            video_file = find_file_by_extension(target_dir, VIDEO_EXTENSIONS)
            excel_file = find_file_by_extension(target_dir, EXCEL_EXTENSIONS)

            if not video_file:
                print(f"Папка пропущена: видеофайл не найден в {target_dir.relative_to(root_path)}")
                continue
            if not excel_file:
                print(f"Папка пропущена: файл разметки не найден в {target_dir.relative_to(root_path)}")
                continue

            output_images_path = find_or_create_image_dir(target_dir)

            print(f"Найдены видео: '{video_file.name}', файл разметки: '{excel_file.name}'\n")

            try:
                last_row_df = get_mediapipe_video_symmetries(
                    str(video_file),
                    str(excel_file),
                    str(output_images_path)
                )
                if last_row_df is not None:
                    patient_last_rows.append(last_row_df)
                    all_last_rows.append(last_row_df)
                    print(f"Успешно обработана папка: {target_dir.relative_to(root_path)}")
                else:
                    print(
                        f"Предупреждение: функция вернула пустой результат для папки: {target_dir.relative_to(root_path)}")
            except Exception as e:
                print(f"Ошибка при обработке папки: {target_dir.relative_to(root_path)}: {e}")

        # Создаем файл результатов для текущего пациента
        if patient_last_rows:
            patient_combined = pd.concat(patient_last_rows, ignore_index=True)
            patient_output_file = patient_dir / f"{patient_dir.name}_all_results.xlsx"
            save_results_to_excel(patient_combined, patient_output_file)
            print(f"\nСоздан файл результатов для пациента {patient_dir.name}")
            print(f"Обработка пациента {patient_dir.name} завершена, обработано папок: {len(patient_last_rows)}")

    print(DIVIDER)

    # Создаем общий файл результатов для всех пациентов
    if all_last_rows:
        combined_results = pd.concat(all_last_rows, ignore_index=True)
        output_file = root_path / f"{root_path.name}_all_results.xlsx"
        save_results_to_excel(combined_results, output_file)
        print(f"\nСоздан общий файл результатов: {output_file}")
        print(f"Суммарно обработано папок: {len(all_last_rows)}")
    else:
        print("Не удалось обработать ни одной папки.")

    print("\nМассовая обработка завершена.")


def save_results_to_excel(df: pd.DataFrame, filepath: Path) -> None:
    df.to_excel(filepath, index=False)


def find_file_by_extension(directory: Path, extensions: set) -> Path | None:
    for file_path in directory.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            return file_path
    return None


def find_or_create_image_dir(directory: Path) -> Path:
    for item in directory.iterdir():
        if item.is_dir():
            return item

    # Если папка не найдена, создаем новую
    new_dir = directory / f"{directory.name}_images"
    new_dir.mkdir(exist_ok=True)
    return new_dir