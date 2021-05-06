# scheduled_task_verification_framework
#### This is a python framework used to verify whether the scheduled task will execute as expected.
#### It has been personally tested on centos7.
#### <font color="#dd0000">Please note that running the example will change the system time!</font><br />
#### <font color="#dd0000">Please execute the example in a test environment</font><br /><br/>
## Usage
#### Way 1: Explicitly add decorators to your scheduled method. (See "<u>Example\Example 1 Using decorator on task-func.py</u>" for the complete code)
```python
from apscheduler.schedulers.background import BackgroundScheduler
from scheduled_task_verification_framework import scheduler_task_manager
scheduler_task_manager_obj = scheduler_task_manager()

@scheduler_task_manager_obj.is_cronTask(name = "monday",task_scheduled_run_at = now_is_monday)
def task_on_every_monday():
    print("Running task [task_on_every_monday], %s" %strftime("%Y-%m-%d-%H_%M_%S", localtime()))

scheduler = BackgroundScheduler()
scheduler.add_job(task_on_every_monday, 'cron',day_of_week="mon", hour=1, minute=1)

scheduler.start()
scheduler_task_manager_obj.monitor(……)
```

#### Way 2: Create a new method with hook instead of the old scheduled method. (See "<u>Example\Example 2 Run new task func instead of old.py</u>" for the complete code) 
```python
from apscheduler.schedulers.background import BackgroundScheduler
from scheduled_task_verification_framework import scheduler_task_manager
scheduler_task_manager_obj = scheduler_task_manager()

def task_on_every_monday():
    print("Running task [task_on_every_monday], %s" %strftime("%Y-%m-%d-%H_%M_%S", localtime()))

new_task_on_every_monday = scheduler_task_manager_obj.is_cronTask(name = "monday",task_scheduled_run_at = now_is_monday)(task_on_every_monday)

scheduler.add_job(new_task_on_every_monday, 'cron',day_of_week="mon", hour=1, minute=1)

scheduler.start()
scheduler_task_manager_obj.monitor(……)
```