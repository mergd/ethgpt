from .types import CYAN, GREEN, RED, RESET, YELLOW
from datetime import datetime


def debug_output(url, response_status, start_time):
    if start_time is None:
        return

    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds() * 1000

    print(f"{RED}[DEBUG]{RESET} | Request URL: {YELLOW}{url}{RESET} | Response code: {RED if response_status != 200 else GREEN}{response_status}{RESET} | Response time: {CYAN}{elapsed_time:.2f}ms{RESET}")
