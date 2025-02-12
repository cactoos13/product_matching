import os
import subprocess
import time
import dotenv
dotenv.load_dotenv()

def start_app():

    app_startup_script = os.getenv('APP_STARTUP_SCRIPT')
    print("Starting Celery Worker...")
    celery_process = subprocess.Popen(
        ['poetry', 'run', 'celery', '-A', {app_startup_script}, 'worker', '--loglevel=info']
    )
    print("Celery Worker started successfully.")


    print("Waiting for 2 seconds...")
    time.sleep(2)

    print("Starting Celery Beat...")
    celery_beat_process = subprocess.Popen(['poetry', 'run',  'celery', '-A', {app_startup_script}, 'beat', '--loglevel=info'])
    print("Celery Worker and Beat started successfully.")


    print("Starting the App...")
    app_process = subprocess.Popen(['poetry', 'run',  'python', '-m', {app_startup_script}])
    print("App started successfully.")

    try:
        celery_process.wait()
        celery_beat_process.wait()
        app_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        celery_process.kill()
        celery_beat_process.kill()
        app_process.kill()
        print("Shut down successfully.")
    except Exception as e:
        print("An error occurred: ", e)
        print("Shutting down...")
        celery_process.kill()
        celery_beat_process.kill()
        app_process.kill()
        print("Shut down successfully.")