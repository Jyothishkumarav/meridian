import subprocess
import sys
import signal
import shlex
import psutil
import time


class Process:

    def __init__(self, cmd):
        self.cmd = cmd

    def run(self):
        try:
            self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, start_new_session=True)
            time.sleep(5)
            self.proc_id = self.process.pid
        except OSError as ex:
            raise ex

    def _kill_child_process(self, p_id, sig=signal.SIGTERM):
        try:
            parent = psutil.Process(p_id)
        except psutil.NoSuchProcess:
            print(f'No such process')
            return
        children = parent.children(recursive=True)
        for proc in children:
            proc.send_signal(sig)

    def terminate(self):
        self._kill_child_process(self.proc_id)
        self.process.terminate()
        self.process.wait()


def is_process_running(proc_name):
    for prc in psutil.process_iter():
        if proc_name in prc.name():
            return True
    return False







# How to use --->


# > is_process_running('roscore')
# False
# >>> ps = Process(['roscore'])
# >>> ps.run()
# >>> is_process_running('roscore')
# True
# >>> ps.terminate()
# >>> is_process_running('roscore')
# False