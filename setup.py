import os
import sys
from pathlib import Path

parent = Path(__file__).parent
filename = parent / 'loading.py'

# Консольная опция
with_console = False  # True, если нужна консоль

# Папка для выходного файла
dist_dir = parent / '.user/dist'

# Берём текущий Python, с которого запустили скрипт
venv_python = sys.executable

# Базовая команда
command = f"{venv_python} -m nuitka \
    --onefile \
    --output-dir={dist_dir} \
    --remove-output \
    --enable-plugin=tk-inter "

# Добавляем опцию для скрытия консоли
if not with_console:
    command += "--windows-console-mode=disable "

# Финальная команда + путь к файлу
command += f"\"{filename}\""

print(command)
os.system(command)
