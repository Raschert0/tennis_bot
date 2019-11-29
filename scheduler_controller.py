from time import sleep
import schedule
import multiprocessing
import logging
import atexit


def daily_job():
    pass


def __scheduler_run(cease_run, interval=60):
    while not cease_run.is_set():
        schedule.run_pending()
        sleep(60)


def schedule_controller():
    cease_continuous_run = multiprocessing.Event()
    schedule.logger.setLevel(logging.WARNING)

    schedule.every().day.do(daily_job)

    p = multiprocessing.Process(target=__scheduler_run, args=(cease_continuous_run,))
    p.start()

    atexit.register(p.terminate)
    atexit.register(cease_continuous_run.set)

    return cease_continuous_run


if __name__ == '__main__':
    schedule_controller()
