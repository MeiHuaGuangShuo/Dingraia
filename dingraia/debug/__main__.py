import argparse
import os
import platform
import signal
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from ..log import logger

python_executable = sys.executable
isOnReload = False
logger = logger.switch_logger(2)
waitAfterLastReload = 5
waitAfterShutdown = 1
lastReloadTime = time.time()


class FileChangedHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    # 2. rsync 默认行为：临时文件 -> rename 覆盖目标
    def on_moved(self, event):
        # event.dest_path 才是真正的“目标文件”
        if not event.is_directory:
            self._handle(event.dest_path)

    # 3. 个别情况下 rsync 会触发 CREATE（比如新文件）
    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def _handle(self, src_path):
        global lastReloadTime
        if not isOnReload:
            if list(filter(lambda x: src_path.endswith(x), watch_file_type)):
                logger.warning(f'文件 {src_path} 发生了变动')
                if time.time() - lastReloadTime < waitAfterLastReload:
                    logger.warning(f'距离上次重载时间过短, 设定值为 {waitAfterLastReload} 秒')
                    return
                lastReloadTime = time.time()
                stop_program()


def stop_program():
    global exit_code
    global isOnReload
    if isOnReload:
        return
    isOnReload = True
    exit_code = -114514
    logger.info("正在重载...")
    if platform.system() == "Windows":
        process.send_signal(signal.CTRL_C_EVENT)
    else:
        process.send_signal(signal.SIGINT)


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
    event_handler = FileChangedHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logger.info(f"File Watcher running at PID {os.getpid()}")
    exit_code = None
    try:
        while exit_code in (None, -114514):
            cmd = [python_executable, python_file] + python_args
            process = subprocess.Popen(cmd, shell=False)
            logger.info(f"启动命令: {cmd}")
            logger.info(f"正在运行 {python_file}, Python PID {process.pid}")
            isOnReload = False
            try:
                process.wait()
            except KeyboardInterrupt:
                logger.info("正在退出, 等待程序结束...")
                if platform.system() == "Windows":
                    process.send_signal(signal.CTRL_C_EVENT)
                else:
                    process.send_signal(signal.SIGINT)
                process.wait()
                exit_code = 1
                logger.info("程序已退出")
                if isOnReload:
                    exit_code = -114514
                else:
                    observer.stop()
                    observer.join()
                    sys.exit(0)
            finally:
                if exit_code != -114514:
                    exit_code = process.returncode
                else:
                    exit_code = None
                    time.sleep(waitAfterShutdown)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
