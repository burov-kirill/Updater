import os
import ast
import subprocess
from time import sleep
import PySimpleGUI as sg
import sys
import threading
import requests
import shutil
from pathlib import Path
import py7zr
def download_file(window, APP_URL, APP_NAME):
    # auth = (LOGIN, ACCESSTOKEN)
    # with urllib.request.urlopen(APP_URL, context=context) as r:
    with requests.get(APP_URL, stream=True) as r:
        chunk_size = 64*1024
        total_length = int(r.headers.get('content-length'))
        total = total_length//chunk_size if total_length % chunk_size == 0 else total_length//chunk_size + 1
        with open(APP_NAME, 'wb') as f:
            for i, chunk in enumerate(r.iter_content(chunk_size=chunk_size)):
                f.write(chunk)
                PERCENT = int((i+1)/total*100)
                window.write_event_value('Next', PERCENT)


def create_download_window(APP_URL, APP_NAME):
    progress_bar = [
        [sg.ProgressBar(100, size=(40, 20), pad=(0, 0), key='Progress Bar', border_width = 0),
         sg.Text("  0%", size=(4, 1), key='Percent', background_color='#007bfb', border_width=0), ],
    ]

    layout = [
        [sg.pin(sg.Column(progress_bar, key='Progress', visible=True, background_color='#007bfb',
                          pad=(0, 0), element_justification='center'))],
    ]
    window = sg.Window('Загрузка', layout, size=(600, 40), finalize=True,
                       use_default_focus=False, background_color='#007bfb')
    progress_bar = window['Progress Bar']
    percent = window['Percent']
    # progressB = window['Progress']
    default_event = True
    while True:
        event, values = window.read(timeout=10)
        if event == sg.WINDOW_CLOSED:
            break
        elif default_event:
            default_event = False
            progress_bar.update(current_count=0, max=100)
            thread = threading.Thread(target=download_file, args=(window, APP_URL, APP_NAME), daemon=True)
            thread.start()
        elif event == 'Next':
            count = values[event]
            progress_bar.update(current_count=count)
            percent.update(value=f'{count:>3d}%')
            window.refresh()
            if count == 100:
                sleep(1)
                break
    window.close()

def killProcess(pid):
    subprocess.Popen('taskkill /F /PID {0}'.format(pid, shell=True))

def is_directory(path):
    onlyfiles = [f[f.rfind('.')+1:] for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if any(map(lambda x: x == 'pyd', onlyfiles)):
        return True
    else:
        return False

def get_subpath(path, i, symbol):
    while i > 0:
        path = path[:path.rfind(symbol)]
        i-=1
    return path


# APP_URL = 'https://raw.githubusercontent.com/burov-kirill/CRMandAccount/master/dist/CRMandBIT.exe'
# APP_NAME = f'CRMandBIT.exe'


EXE_PATH = sys.argv[0]
APP_URL = sys.argv[2]
APP_NAME = sys.argv[3]
pid = int(sys.argv[4])
PATH = sys.argv[5]
# if not is_dir:
#     # Если вызывается из папки с содержымым остальным, то папку создаем на уровень выше
#     os.mkdir('temp_folder')
#     FULL_APP_NAME = f'{PATH}\\temp_folder\\{APP_NAME}'
#     killProcess(pid)
#     create_download_window(APP_URL, FULL_APP_NAME)
#     # удаление предполагает, что удаляется файл, а не папка с содержимым
#     os.remove(f'{PATH}\\{APP_NAME}')
#     os.replace(FULL_APP_NAME, f'{PATH}\\{APP_NAME}')
#     os.rmdir('temp_folder')
#     new_pid = str(os.getpid())
#     new_args = f'{PATH}\\{APP_NAME} -config {new_pid}'
#     subprocess.call(new_args)
# else:
path = get_subpath(EXE_PATH, 2, '/')
# ROOT_PATH = get_subpath(PATH, 1, '\\')
print(path)
Path(f'{path}\\temp_folder').mkdir(parents=True, exist_ok=True)
os.chdir(f'{path}\\temp_folder')
# os.mkdir('temp_folder')
UPD_PATH = os.path.abspath(__file__)
ZIP_NAME = APP_NAME[:APP_NAME.rfind('.')] + '.7z'
ZIP_FULL_APP_NAME = f'{path}\\temp_folder\\{ZIP_NAME}'
killProcess(pid)
create_download_window(APP_URL, ZIP_FULL_APP_NAME)
shutil.rmtree(PATH, ignore_errors=True)

with py7zr.SevenZipFile(ZIP_FULL_APP_NAME, mode='r') as z:
    z.extractall()
file_names = os.listdir(f"{path}\\temp_folder\\{APP_NAME[:APP_NAME.rfind('.')]}")

for file_name in file_names:
    shutil.move(os.path.join(f"{path}\\temp_folder\\{APP_NAME[:APP_NAME.rfind('.')]}", file_name), PATH)
shutil.rmtree(f'{path}\\temp_folder', ignore_errors=True)
os.chdir(f'{path}')
new_pid = str(os.getpid())
new_args = f'{PATH}\\{APP_NAME} -config {new_pid}'
subprocess.call(new_args)
# удалить временную папку
# запустить процесс



