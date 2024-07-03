import signal
import time
import os
import sys
import argparse
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from ..log import logger

python_executable = sys.executable
isOnReload = False


class MyHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if not isOnReload:
            if list(filter(lambda x: event.src_path.endswith(x), watch_file_type)):
                logger.warning(f'文件 {event.src_path} 发生了变动')
                your_function()


def your_function():
    global exit_code
    global isOnReload
    isOnReload = True
    exit_code = -114514
    logger.info("正在重载...")
    process.send_signal(signal.CTRL_C_EVENT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=argparse.FileType('r'), help='要执行的文件')
    parser.add_argument('--path', '-p', type=str, default=os.getcwd(), help='监控的路径')
    parser.add_argument('--watch-file-type', '-t', type=str, default='.py', help='监控的文件类型')
    args, python_args = parser.parse_known_args()
    python_file = args.file.name
    path = args.path
    watch_file_type = args.watch_file_type
    if ';' in watch_file_type:
        watch_file_type = watch_file_type.split(';')
    elif not watch_file_type:
        watch_file_type = []
    else:
        watch_file_type = [watch_file_type]
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logger.info(f"File Watcher running at PID {os.getpid()}")
    exit_code = None
    try:
        while exit_code in (None, -114514):
            process = subprocess.Popen([python_executable, python_file] + python_args, shell=True)
            logger.info(f"正在运行 {python_file}, PID {process.pid}")
            isOnReload = False
            try:
                process.wait()
            except KeyboardInterrupt:
                process.send_signal(signal.CTRL_C_EVENT)
                process.wait()
            finally:
                if exit_code != -114514:
                    exit_code = process.returncode
                else:
                    exit_code = None
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
