import subprocess
import os
import signal

from meridian_api import meridian_path


def start_lidar(parent_folder):
    script_path = meridian_path + '/start_lidar.sh'
    path = parent_folder + '/lidar'
    try:
        # Run the Bash script in the background
        lidar_sensor_process = subprocess.Popen(
            [script_path, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        print(f'lidar shell script started successfully.')
        print(f'lidar Sensor process started with PID: {lidar_sensor_process.pid}')
        return lidar_sensor_process
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        return None


def stop_lidar(lidar_sensor_process):
    sensor_type = 'lidar'
    if lidar_sensor_process:
        try:
            # Send a signal to terminate the sensor process
            os.killpg(os.getpgid(lidar_sensor_process.pid), signal.SIGTERM)
            lidar_sensor_process.wait()
            print(f'Sensor process for {sensor_type} stopped successfully.')
            return {'message': f'Sensor process for {sensor_type} stopped successfully.'}
        except Exception as e:
            print(f'Error stopping sensor process for {sensor_type}: {str(e)}')
            return {'error': f'Error stopping sensor process for {sensor_type}: {str(e)}'}, 500
    else:
        print(f'No running sensor process for {sensor_type} to stop.')
        return {'error': f'No running sensor process for {sensor_type} to stop.'}, 400
