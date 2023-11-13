from typing import AsyncIterable, Generic, Optional, TypeVar
from .back_off import ExponentialBackoff
import aiohttp
from datetime import datetime
from .debugger import debug_output
from .types import user_agent

T = TypeVar('T')

class Response(Generic[T]):
    data: Optional[T]
    error: bool
    error_code: Optional[int]
    error_message: Optional[str]

    def __init__(self, data: Optional[T], error: bool, error_code: Optional[int], error_message: Optional[str]):
        self.data = data
        self.error = error
        self.error_code = error_code
        self.error_message = error_message

def check_and_modify_response(json_obj):
    """ modify reponse and remove next_update_at """
    for key in list(vars(json_obj).keys()):
        if key == 'next_update_at':
            del vars(json_obj)[key]
        elif isinstance(vars(json_obj)[key], dict):
            check_and_modify_response(vars(json_obj)[key])


async def paginate_endpoint(url: str, api_key: str, urls_params, data_class_constructor: T, debug: Optional[bool] = False) -> AsyncIterable[T]:
    has_next = True
    page_number = 0
    backoff = ExponentialBackoff(api_key, debug)
    data = None

    while has_next:
        try:

            if urls_params.get("page-number") is None:
                urls_params["page-number"] = str(page_number)
                
            start_time = None
            if debug:
                start_time = datetime.now()

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}", params=urls_params, headers={"Authorization": f"Bearer {api_key}", "X-Requested-With": user_agent}) as response:
                    
                    debug_output(response.url, response.status, start_time)

                    if response.status == 429:
                        try:
                            data = backoff.back_off(response.url)
                        except Exception as e:
                            has_next = False
                            raise Exception(f"An error occurred {response.status}: {e}")
                    else:
                        data = await response.json()
                    
                    for tx in data.get("data").get("items"):
                        data_class = data_class_constructor(tx)
                        check_and_modify_response(data_class)
                        yield data_class
                    
                    backoff.set_num_attempts(1)

                    if not data.get("error"):
                        pagination = data.get("data", {}).get("pagination")

                        if pagination and not pagination.get("has_more"):
                            has_next = False

                        next_page = int(urls_params.get("page-number")) + 1
                        urls_params["page-number"] = str(next_page)
                    else:
                        has_next = False

        except Exception as e:
            has_next = False
            error_message = str(e)  # Get the error message as a string
            if "An error occurred 429" in error_message:
                raise Exception(error_message)
            raise Exception(f"An error occurred {data.get('error_code') if data else response.status}: {data.get('error_message') if data else 'Internal server error' if response.status == 500 else '401 Authorization Required'}")

