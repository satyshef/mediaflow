import os
import time
import json

def generate_filename(path):
    ext = get_file_extension(path)
    timestamp = str(time.time())
    timestamp = timestamp.replace(".", "_")
    return f"{timestamp}.{ext}"


def get_file_extension(file_path):
    # Извлечь расширение файла из пути
    _, file_extension = os.path.splitext(file_path)
    
    # Удалить точку из расширения (если она присутствует)
    file_extension = file_extension[1:] if file_extension.startswith('.') else file_extension
    
    return file_extension


def get_file_name(file_path):
    # Извлечь имя файла из полного пути
    file_name = os.path.basename(file_path)
    name, _ = os.path.splitext(file_name)
    #r = file_name.rsplit(".")
    return name


def get_file_directory(file_path):
    # Извлечь директорию из полного пути к файлу
    directory = os.path.dirname(file_path)
    
    return directory


def delete_file(file_path):
    # Удалить файл
    try:
        os.remove(file_path)
        print("Файл удален успешно.")
    except OSError as e:
        print(f"Ошибка при удалении файла: {e}")

#получить самый старый файл в директории
def oldest_file_in_directory(directory):
    files = os.listdir(directory)
    if not files:
        return None

    # Полный путь к файлам в директории
    file_paths = [os.path.join(directory, file) for file in files]

    # Получение времени последнего изменения для каждого файла
    file_times = [(file, os.path.getmtime(file)) for file in file_paths]
    # Находим файл с самым старым временем изменения
    oldest_file = min(file_times, key=lambda x: x[1])
    return oldest_file[0]  # Возвращаем путь к самому старому файлу


def read_file_lines(file_path):
    try:
        result = []
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            #result = []
            for line in lines:
                result.append(line.strip())
        if len(result) != 0:
            return result

    except FileNotFoundError:
        print("Файл не найден.")
    except IOError as e:
        print(f"Ошибка при чтении файла: {e}")
    return None


def read_file_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Файл не найден.")
    except IOError as e:
        print(f"Ошибка при чтении файла: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка при декодировании JSON: {e}")
    return None

def files_in_directory(directory, extensions = "*"):
    """
    Функция фильтрует файлы в указанной директории по расширениям.

    Аргументы:
    directory_path (str): Путь к директории.
    extensions (list): Список расширений файлов для фильтрации.

    Возвращает:
    list: Список файлов с указанными расширениями в указанной директории.
    """
    if not os.path.isdir(directory):
        return None

    filtered_files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            if extensions == "*" or extensions == '' or (any(file.endswith(ext) for ext in extensions)):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    filtered_files.append(file_path)
    filtered_files.sort()
    return filtered_files


def ___files_in_directory(directory):
    # Получить список файлов в директории
    files = [os.path.join(directory, file) for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
    
    # Отсортировать список файлов по времени модификации
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(x), reverse=False)
    return sorted_files