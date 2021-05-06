import os
from time import sleep, time
from functools import wraps
from threading import RLock, Thread
from thread import interrupt_main
from logging import StreamHandler, handlers, getLogger, INFO, Formatter


if(os.path.isdir(os.path.join(os.path.dirname(__file__), "log")) == False):
    os.mkdir(os.path.join(os.path.dirname(__file__), "log"))

stvf_handler = handlers.TimedRotatingFileHandler(os.path.join(os.path.dirname(
    __file__), "log", "scheduled_task_verification_framework.log"), when='D', interval=1, backupCount=365*10*3)
stvf_handler.setFormatter(Formatter(
    "%(asctime)s [%(levelname)s] thread(%(thread)d-%(threadName)s) %(pathname)s : %(module)s - %(funcName)s\n%(message)s\n"))

logger = getLogger(__file__)
logger.setLevel(INFO)
logger.addHandler(stvf_handler)
logger.addHandler(StreamHandler())



class status_enum(object):
    not_exist = None
    initial = 0
    running = 1
    done = 2


class scheduler_task_manager(object):

    def __init__(self):
        global logger
        self.logger = logger

        self.status_flag_dict = {}
        self.status_flag_dict_rlock = RLock()

        self.cronTask_run_time_table_dict = {}

        self.if_occurred_error = False
        self.change_error_flag_rlock = RLock()

    def _add_role(self, name, check_run_func):
        self.status_flag_dict_rlock.acquire()
        if(self.status_flag_dict.get(name) == None):
            self.status_flag_dict[name] = status_enum.initial
            self.cronTask_run_time_table_dict[name] = check_run_func
            self.status_flag_dict_rlock.release()

        else:
            self.occurring_error()

            self.status_flag_dict_rlock.release()

            self.logger.error("Already has role named [%s]" % name)
            raise NameError("Already has role named [%s]" % name)

    def _check_role_status(self, name):
        self.status_flag_dict_rlock.acquire()
        if(self.status_flag_dict.get(name) == None):
            ret = status_enum.not_exist

        else:
            ret = self.status_flag_dict[name]

        self.status_flag_dict_rlock.release()
        return ret

    def _if_task_should_be_executed(self, name):
        return self.cronTask_run_time_table_dict[name]()

    def change_role_status(self, name, status):
        self.status_flag_dict_rlock.acquire()
        if(self.status_flag_dict.get(name) == None):
            self.logger.error("Not found role named [%s]" % name)
            ret = False

        else:
            self.status_flag_dict[name] = status
            ret = True

        self.status_flag_dict_rlock.release()
        return ret

    def _if_error(self):
        self.change_error_flag_rlock.acquire()
        ret = self.if_occurred_error
        self.change_error_flag_rlock.release()
        return ret

    def occurring_error(self):
        self.change_error_flag_rlock.acquire()
        self.if_occurred_error = True
        self.change_error_flag_rlock.release()

    def monitor(self, intervene_func, timeout = 60, args = None):
        if(self._if_error()):
            self.logger.error("Error detected in monitor")
            self.logger.info("Exiting with error !")
            exit()

        start_sec = time()

        self.status_flag_dict_rlock.acquire()
        unready_role_list = self.status_flag_dict.keys()
        self.status_flag_dict_rlock.release()

        while (unready_role_list != []):
            
            _tmp_list = []

            for name in unready_role_list:
                role_status = self._check_role_status(name)

                if(role_status == status_enum.initial):

                    if(self._if_task_should_be_executed(name) == True):
                    # Current role status is "initial", if the task of this role should be executed at this time point, 
                    # its status will be changed from "initial" to "running" instead of staying at "initial" for a long time.

                        if(time() <= start_sec + timeout):
                            _tmp_list.append(name)

                        else:
                            self.occurring_error()
                            self.logger.error("[%s] The task has not started after the time limit." % name)
                            self.logger.info("Exiting with error !")

                            exit()
                        
                    else:
                        continue
                        

                elif(role_status == status_enum.running):
                    if(time() <= start_sec + timeout * 2):
                        _tmp_list.append(name)
                    else:
                        self.occurring_error()
                        self.logger.error("[%s] running timeout - %ds." % (name, timeout*10))
                        self.logger.info("Exiting with error !")

                        exit()

                elif(role_status == status_enum.done):
                    self.change_role_status(name, status_enum.initial)
                    continue

                elif(role_status == status_enum.not_exist):
                    self.occurring_error()
                    self.logger.error("[%s] does not exist.")
                    self.logger.info("Exiting with error !")

                    exit()

            unready_role_list = _tmp_list
            sleep(3)

        return intervene_func() if args == None else intervene_func(*args)


    def is_cronTask(self, name, task_scheduled_run_at):
        if(self._if_error()):
            self.logger.error("Error detected. name : [%s]" % name)
            self.logger.info("Exiting with error !")
            exit()
        else:
            self._add_role(name, task_scheduled_run_at)

        def cronTask_inner(func):

            @wraps(func)
            def new_func(*args, **argv):
                if(self._check_role_status(name) != status_enum.initial):
                    self.occurring_error()
                    self.logger.error("Check out the status of [%s] is not initial" % name)
                    self.logger.info("Exiting with error !")
                    exit()

                else:
                    self.change_role_status(name, status_enum.running)
                    st = time()
                    self.logger.info("Task [%s] started." % name)
                    ret = func(*args, **argv)
                    self.logger.info("Task [%s] ended." % name)
                    self.logger.info("Use time %f s.\n" % (time()-st) )
                    self.change_role_status(name, status_enum.done)
                    return ret

            return new_func

        return cronTask_inner

