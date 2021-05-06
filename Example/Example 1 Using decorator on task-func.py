import os
import sys

from datetime import datetime, timedelta
from time import time, sleep, strftime, localtime, strptime, mktime

from apscheduler.schedulers.background import BackgroundScheduler
from scheduled_task_verification_framework import scheduler_task_manager
scheduler_task_manager_obj = scheduler_task_manager()


def get_next_target_datetime(time_shift_timedelta,specified_today = None):
    today = datetime.now() if specified_today == None else specified_today

    if(today.month == 12):
        nm_year = today.year +1
        nm_month = 1
    else:
        nm_year = today.year
        nm_month = today.month + 1


    next_monday = today.replace(hour=0, minute=0 ,second=0, microsecond= 0) + timedelta(weeks= 1, days= -today.weekday())
    next_month_1st = today.replace(year= nm_year, month= nm_month, day= 1, hour=0, minute=0 ,second=0, microsecond= 0)
    

    next_target_datetime = next_monday if next_monday < next_month_1st else next_month_1st

    return next_target_datetime + time_shift_timedelta



def now_is_monday():
    return datetime.now().isoweekday() == 1

def now_is_month_1st():
    return datetime.now().day == 1


@scheduler_task_manager_obj.is_cronTask(name = "monday",task_scheduled_run_at = now_is_monday)
def task_on_every_monday():
    print("Running task [task_on_every_monday], %s" %strftime("%Y-%m-%d-%H_%M_%S", localtime()))


@scheduler_task_manager_obj.is_cronTask(name = "month_1st",task_scheduled_run_at = now_is_month_1st)
def task_on_every_month_1st():
    print("Running task [task_on_every_month_1st], %s" %strftime("%Y-%m-%d-%H_%M_%S", localtime()))


def load_tasks_and_start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(task_on_every_monday, 'cron',day_of_week="mon", hour=1, minute=1)
    scheduler.add_job(task_on_every_month_1st, 'cron', day=1, hour=1, minute=1)
    scheduler.start()




if __name__ == "__main__": 


    target_start_time = "2030-1-1 01:00:55"
    target_end_time = "2030-3-1 00:00:00"

    sec_start = mktime(strptime(target_start_time, "%Y-%m-%d %H:%M:%S"))
    sec_end = mktime(strptime(target_end_time,"%Y-%m-%d %H:%M:%S"))

    start_time_struct = localtime(sec_start)
    sts = start_time_struct


    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    from sys_time_changer import change_sys_time
    change_sys_time(sts.tm_year, sts.tm_mon, sts.tm_mday, sts.tm_hour, sts.tm_min, sts.tm_sec)



    load_tasks_and_start()

    while True:
        if(time() >= sec_end):
            exit()

        else:
            next_time = get_next_target_datetime(timedelta(hours=1, seconds=55))
            nt_time = next_time
            scheduler_task_manager_obj.monitor(change_sys_time, timeout = 60, args = (nt_time.year, nt_time.month, nt_time.day, nt_time.hour, nt_time.minute, nt_time.second))