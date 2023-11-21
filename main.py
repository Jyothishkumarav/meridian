import subprocess
import os
import time

# Set up the environment by sourcing the setup.bash file
def start_roscore():
    import subprocess
    import os
    import time

    # Set up the environment by sourcing the setup.bash file
    bash_file_path = '/home/slam/catkin_ws/devel/setup.bash'

    # Start roscore in a new process and detach it
    roscore_process = subprocess.Popen(f"source {bash_file_path} && roscore &", shell=True, preexec_fn=os.setsid)

    # Give some time for roscore to start (you might need to adjust the sleep duration)
    time.sleep(5)

    # Get the process ID of the roscore process
    roscore_pid = roscore_process.pid
    print(f"roscore process ID: {roscore_pid}")


    # exit_code = roscore_process.returncode
    # print(f"roscore exit code: {exit_code}")


if __name__ == '__main__':
   start_roscore()
   print('Lidar stopped.')
