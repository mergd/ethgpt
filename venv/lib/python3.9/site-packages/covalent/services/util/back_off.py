""" import modules """
import math
import time
from datetime import datetime
import requests
from .debugger import debug_output
from .types import user_agent

DEFAULT_BACKOFF_MAX_RETRIES = 5
BASE_DELAY_MS = 1000

class MaxRetriesExceededError(Exception):
    """ max retry exceeded class """
    def __init__(self, max_retries):
        self.max_retries = max_retries
        super().__init__(f"Max retries ({max_retries}) exceeded.")

class ExponentialBackoff:
    """ exponential backoff class """
    retry_count = 1
    max_retries = DEFAULT_BACKOFF_MAX_RETRIES
    api_key: str
    debug: bool

    def __init__(self, api_key: str, debug: bool, max_retries = DEFAULT_BACKOFF_MAX_RETRIES):
        self.max_retries = max_retries
        self.api_key = api_key
        self.debug = debug

    def back_off(self, url: str):
        response = None
        try:
            start_time = None
            if self.debug:
                start_time = datetime.now()
            
            response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api_key}",
                "X-Requested-With": user_agent
            })
                        
            debug_output(response.url, response.status_code, start_time)
            if response.status_code == 429:
                raise Exception(f"Received status code: {response.status_code}")
            else:
                return response.json()

        except Exception as e:
            error_message = str(e)  # Get the error message as a string
            if "Received status code: 429" in error_message and self.retry_count < self.max_retries:
                self.retry_count += 1
                delay_ms = math.pow(2, self.retry_count) * BASE_DELAY_MS / 1000
                time.sleep(delay_ms)
                return self.back_off(url)
            raise MaxRetriesExceededError(self.max_retries)
            
        

    def set_num_attempts(self, retry_count: int):
        """ num of attempts """
        self.retry_count = retry_count
