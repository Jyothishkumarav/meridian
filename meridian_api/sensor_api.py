import os
import signal
import subprocess
from configparser import ConfigParser

from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint

from meridian_api.startup_handler import StartupHandler

app = Flask(__name__)

# Configure Swagger UI
# Load configuration from config.ini
config = ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

# Configure Swagger UI
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Meridian API"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Create Flask-RESTx API
api = Api(app, version='1.0', title='Meridian API', description='API for managing sensors and folders')

sensor_processes = {}

# Namespace for sensors
sensor_ns = api.namespace('sensors', description='Sensor operations')

@sensor_ns.route('/control')
class SensorControlResource(Resource):
    @api.expect(api.model('SensorControlInput', {
        'sensor_type': fields.String(required=True, description='Sensor type (e.g., lidar, camera, imu)'),
        'action': fields.String(required=True, description='Action to perform (start or stop)')
    }))
    def post(self):
        """Control a sensor based on the sensor type and action"""
        data = request.json
        sensor_type = data['sensor_type']
        action = data['action']

        if action not in ['start', 'stop']:
            return {'error': f'Invalid action: {action}. Use "start" or "stop".'}, 400

        if action == 'start':
            result = self.start_sensor(sensor_type)
        elif action == 'stop':
            result = self.stop_sensor(sensor_type)

        return {'message': result}

    def start_sensor(self, sensor_type):
        # Execute a command to start a sensor process based on sensor type
        if sensor_type == 'lidar':
            command = self.start_lidar()
        elif sensor_type == 'camera':
            command = './start_camera_sensor.sh'
        elif sensor_type == 'imu':
            command = './start_imu_sensor.sh'
        else:
            return f'Unsupported sensor type: {sensor_type}'

        try:
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f'{sensor_type} sensor started successfully.'
        except Exception as e:
            return f'Error starting {sensor_type} sensor: {str(e)}'

    def stop_sensor(self, sensor_type):
        # Execute a command to stop a sensor process based on sensor type
        if sensor_type == 'lidar':
            command = self.stop_lidar()
        elif sensor_type == 'camera':
            command = './stop_camera_sensor.sh'
        elif sensor_type == 'imu':
            command = './stop_imu_sensor.sh'
        else:
            return f'Unsupported sensor type: {sensor_type}'

        try:
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f'{sensor_type} sensor stopped successfully.'
        except Exception as e:
            return f'Error stopping {sensor_type} sensor: {str(e)}'
    def start_lidar(self):
        global sensor_processes
        command = ['sudo', 'tcpdump', '-i', 'wlp1s0', 'tcp']
        try:
            # Run the command in the background
            lidar_sensor_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              preexec_fn=os.setsid)
            sensor_processes['lidar'] = lidar_sensor_process
            return {'message': 'Sensor process started successfully.'}
        except Exception as e:
            return {'error': f'Error starting sensor process: {str(e)}'}, 500

    def stop_lidar(self):
        global sensor_processes
        sensor_type = 'lidar'
        if sensor_type in sensor_processes and sensor_processes[sensor_type].poll() is None:
            try:
                # Send a signal to terminate the sensor process
                os.killpg(os.getpgid(sensor_processes[sensor_type].pid), signal.SIGTERM)
                sensor_processes[sensor_type].wait()
                return {'message': f'Sensor process for {sensor_type} stopped successfully.'}
            except Exception as e:
                return {'error': f'Error stopping sensor process for {sensor_type}: {str(e)}'}, 500
        else:
            return {'error': f'No running sensor process for {sensor_type} to stop.'}, 400


# Execute a bash script when the Flask application starts
@app.before_request
def run_startup_script():
    try:
        StartupHandler.get_instance().execute_commands()
        # subprocess.Popen('./startup_script.sh', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print(f'Error executing startup script: {str(e)}')

# Namespace for folders
folder_ns = api.namespace('folders', description='Folder operations')

@folder_ns.route('/')
class FolderResource(Resource):
    @api.expect(api.model('FolderInput', {
        'name': fields.String(required=True, description='Folder name')
    }))
    def post(self):
        """Create a folder and subfolders"""
        data = request.json
        folder_name = data['name']
        parent_folder = config.get('Startup', 'parent_folder')

        # Create the main folder
        main_folder_path = os.path.join(parent_folder, folder_name)
        os.makedirs(main_folder_path, exist_ok=True)

        # Create subfolders
        subfolders = ['lidar', 'camera', 'imu']
        for subfolder in subfolders:
            subfolder_path = os.path.join(main_folder_path, f'{subfolder}')
            os.makedirs(subfolder_path, exist_ok=True)

        return {'message': f'Folder "{folder_name}" and subfolders created successfully.'}


@folder_ns.route('/update-parent-folder')
class UpdateParentFolderResource(Resource):
    @api.expect(api.model('UpdateParentFolderInput', {
        'new_parent_folder': fields.String(required=True, description='New parent folder path')
    }))
    def post(self):
        """Update the parent folder path in the configuration"""
        data = request.json
        new_parent_folder = data['new_parent_folder']

        # Update the parent folder in the configuration
        config.set('Startup', 'parent_folder', new_parent_folder)
        with open(config_path, 'w') as config_file:
            config.write(config_file)

        return {'message': f'Parent folder updated to: {new_parent_folder}'}

if __name__ == '__main__':
    app.run(debug=True)
