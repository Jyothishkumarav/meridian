from config import ROS_CORE
from service_util.process import Process, is_process_running

ros_core_command = 'ping google.com'
def start_roscore():
    try:
        # Run the Bash script in the background
        is_ros_core_running = is_process_running(ros_core_command)
        if not is_ros_core_running:
            roscore_ps = Process([f'{ros_core_command}'])
            roscore_ps.run()
            msg = f'ros core process started with PID: {roscore_ps.proc_id}'
            print(msg)
            return roscore_ps, msg
        else:
            return None, 'ros core service is already running !!!'
    except OSError as exc:
        msg = f"Status : FAIL,{ exc.returncode}, {exc.output}"
        print(msg)
        return None, msg

def stop_roscore(roscore_process:Process):
    sensor_type = ROS_CORE
    if roscore_process:
        try:
            # Send a signal to terminate the sensor process
            roscore_process.terminate()
            print(f'roscore stopped successfully.')
            return {'message': f'roscore stopped successfully.'}
        except Exception as e:
            print(f'Error stopping  process for {sensor_type}: {str(e)}')
            return {'error': f'Error stopping sensor process for {sensor_type}: {str(e)}'}, 500
    else:
        print(f'No running sensor process for {sensor_type} to stop.')
        return {'error': f'No running sensor process for {sensor_type} to stop.'}, 400
