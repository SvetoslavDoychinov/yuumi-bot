import logging
import time
from functools import partial
from typing import Optional, Dict, Any, Callable

import requests
import urllib3
from requests import Response, HTTPError


class RequestAPI:
    """Base requests API class"""

    def __init__(self, protocol: str, domain: str, port: str):
        self.logger = logging.getLogger(__name__)
        self.base_url = f"{protocol}://{domain}:{port}"
        self.session = requests.session()
        self.headers = {}
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _retry_request(self, request_callback: Callable[[], Response], retries: int = 5, initial_delay: int = 1,
                       max_delay: int = 16) -> Response:
        """
        Method to retry a request
        :param retries: amount of retries
        :param initial_delay: starting delay between retries, increases exponentially
        :param max_delay: maximum delay between retries allowed
        :return: Response object
        """
        for i in range(retries):
            result = request_callback()
            try:
                result.raise_for_status()
                return result
            except HTTPError as err:
                self.logger.debug(f"Retrying request {i + 1} times. Error {err}")
            time.sleep(min(initial_delay * 2 ** i, max_delay))
        raise HTTPError("Retries exceeded")

    def get(self, url: str, data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Do a get request
        :param url: url to get
        :param data: data to send with request
        :param headers: headers to send with request
        :return: Response object
        """
        if not headers:
            headers = self.headers
        return self.session.get(url=self.base_url + url, headers=headers, json=data, verify=False)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Do a post request
        :param url: url to get
        :param data: data to send with request
        :param headers: headers to send with request
        :return: Response object
        """
        if not headers:
            headers = self.headers
        return self.session.post(url=self.base_url + url, headers=headers, json=data, verify=False)

    def put(self, url: str, data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Do a put request
        :param url: url to get
        :param data: data to send with request
        :param headers: headers to send with request
        :return: Response object
        """
        if not headers:
            headers = self.headers
        return self.session.put(url=self.base_url + url, headers=headers, json=data, verify=False)

    def patch(self, url: str, data: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Do a patch request
        :param url: url to get
        :param data: data to send with request
        :param headers: headers to send with request
        :return: Response object
        """
        if not headers:
            headers = self.headers
        return self.session.patch(url=self.base_url + url, headers=headers, json=data, verify=False)

    def get_with_retries(self, url: str, data: Optional[Dict[str, Any]] = None,
                         headers: Optional[Dict[str, Any]] = None, retries: int = 5, initial_delay: int = 1,
                         max_delay: int = 16) -> Response:
        """
        Attempt a get request given amount of time, delay between retries rises exponentially
        :param url: url to get
        :param data: data to send with request
        :param headers: headers to send with request
        :param retries: amount of retries
        :param initial_delay: starting delay between retries, increases exponentially
        :param max_delay: maximum delay between retries allowed
        :return: Response object
        """
        return self._retry_request(
            request_callback=partial(self.get, url=url, data=data, headers=headers),
            retries=retries,
            initial_delay=initial_delay,
            max_delay=max_delay
        )

    def post_with_retries(self, url: str, data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, Any]] = None, retries: int = 5, initial_delay: int = 1,
                          max_delay: int = 16) -> Response:
        """
        Attempt a post request given amount of time, delay between retries rises exponentially
        :param url: url to get
        :param data: data to send with request
        :param headers: headers to send with request
        :param retries: amount of retries
        :param initial_delay: starting delay between retries, increases exponentially
        :param max_delay: maximum delay between retries allowed
        :return: Response object
        """
        return self._retry_request(
            request_callback=partial(self.post, url=url, data=data, headers=headers),
            retries=retries,
            initial_delay=initial_delay,
            max_delay=max_delay
        )
