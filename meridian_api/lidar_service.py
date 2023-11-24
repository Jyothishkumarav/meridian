from meridian_api import meridian_path
from service_util.process import Process, is_process_running

lidar_cmd = ""


def start_lidar(parent_folder):
    script_path = meridian_path + '/start_lidar.sh'
    lidar_project_dir_path = parent_folder + '/lidar'
    try:
        is_lidar_running = is_process_running(lidar_cmd)
        if not is_lidar_running:
            lidar_ps = Process([f'{lidar_cmd}'])
            lidar_ps.run()
            msg = f'lidar sensor process started with PID: {lidar_ps.proc_id}'
            print(msg)
            return lidar_ps, msg
        else:
            return None, 'lidar service is already running !!!'

    except OSError as exc:
        msg = f"Status : FAIL,{exc.returncode}, {exc.output}"
        print(msg)
        return None, msg


def stop_lidar(lidar_sensor_process: Process):
    sensor_type = 'lidar'
    if lidar_sensor_process:
        try:
            # Send a signal to terminate the sensor process
            lidar_sensor_process.terminate()
            print(f'Sensor process for {sensor_type} stopped successfully.')
            return {'message': f'Sensor process for {sensor_type} stopped successfully.'}
        except Exception as e:
            print(f'Error stopping sensor process for {sensor_type}: {str(e)}')
            return {'error': f'Error stopping sensor process for {sensor_type}: {str(e)}'}, 500
    else:
        print(f'No running sensor process for {sensor_type} to stop.')
        return {'error': f'No running sensor process for {sensor_type} to stop.'}, 400
