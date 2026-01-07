"""
Example script showing how to run the AdvertisementBatchIndexByCategoriesTask

This script demonstrates how to:
1. Bootstrap the application
2. Create and run the task with category IDs (synchronously)

Note: This runs the task synchronously. For async execution via Celery,
use scheduler.run_task(task) instead (requires Redis/Celery worker).
"""

from bootstrap import bootstrap
from modules import Modules
from packages.business.modules.advertisement.tasks.once.advertisement_batch_index_by_categories_task import \
    AdvertisementBatchIndexByCategoriesTask

# Bootstrap the application (this registers all services, repositories, and tasks)
bootstrap(total=True, modules=Modules)

# Create the task with category IDs and optional limit/offset
task = AdvertisementBatchIndexByCategoriesTask(
    category_ids=[11],  # List of category IDs to index
    limit=100,          # Optional: maximum number of ads to fetch
    offset=0           # Optional: pagination offset
)

# Run the task synchronously (directly calls the run method)
print("Starting task execution...")
result = task.run(*task.get_args(), **task.get_kwargs())

if result:
    print("Task completed successfully!")
else:
    print("Task failed. Check the logs above for details.")

