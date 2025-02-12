from celery import Celery, Task

# Step 1: Create the Celery app
app = Celery(
    'my_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)


@app.task(name='my_task')
def my_task_instance(self, *args, **kwargs):
    print("Hello from my_task_instance")
    print("Args:", args)
    print("Kwargs:", kwargs)
    return "Task executed successfully"

my_task_instance.delay(1, 2, 3, name="John Doe")