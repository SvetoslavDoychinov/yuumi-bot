import logging
import shlex
import subprocess
import time
from typing import Callable

import psutil

logger = logging.getLogger(__name__)


def wait_for_condition(condition_callback: Callable[[], bool], timeout: int = 300, delay: int = 10) -> bool:
    """
    Helper to keep retrying a method for a given time
    :param condition_callback: method to retry
    :param timeout: time to wait till condition is met
    :param delay: time to wait between retries
    :return: True if condition met in given timeout, False otherwise
    """
    start = time.time()
    while time.time() < start + timeout:
        if condition_callback():
            logger.info("Condition met")
            return True
        time.sleep(delay)
    logger.info("Failed to meet condition in given time")
    return False


def is_process_running(process_name: str) -> bool:
    """
    Check if process is running
    :param process_name: name of said process
    :return: True if running, False otherwise
    """
    for process in psutil.process_iter():
        if process.name() == process_name:
            logger.debug(f"Process {process_name} is running = True")
            return True
    logger.debug(f"Process {process_name} is running = False")
    return False


def run_process(process_name: str, args: str, shell: bool = False, capture_output: bool = False) -> psutil.Process:
    """
    Run a process
    :param process_name: name of process
    :param args: arguments to run process with
    :param shell: run process in shell if True, don't otherwise
    :param capture_output: True to capture output, False not to
    :return: psutil.Process object
    """
    command = shlex.split(f"{process_name} {args}", posix=False)
    stdout, stderr = None, None
    if capture_output:
        stdout, stderr = subprocess.PIPE, subprocess.PIPE
    return psutil.Popen(args=command, stdout=stdout, stderr=stderr, shell=shell)
