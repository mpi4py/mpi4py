"""
Compare the speed of downloading URLs sequentially vs. using futures.
"""

import contextlib
import functools
import sys
import time

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    ThreadPoolExecutor = lambda _: None  # noqa: E731
try:
    from concurrent.futures import ProcessPoolExecutor
except ImportError:
    ProcessPoolExecutor = lambda _: None  # noqa: E731

from mpi4py.futures import MPIPoolExecutor, as_completed

URLS = [
    "http://www.google.com/",
    "http://www.apple.com/",
    "http://www.ibm.com",
    "http://www.thisurlprobablydoesnotexist.com",
    "http://www.slashdot.org/",
    "http://www.python.org/",
    "http://www.bing.com/",
    "http://www.facebook.com/",
    "http://www.github.com/",
    "http://www.youtube.com/",
    "http://www.blogger.com/",
]


def load_url(url, timeout):
    return urlopen(url, timeout=timeout).read()


def download_urls_sequential(urls, timeout=60):
    url_to_content = {}
    for url in urls:
        with contextlib.suppress(Exception):
            url_to_content[url] = load_url(url, timeout=timeout)
    return url_to_content


def download_urls_with_executor(executor, urls, timeout=60):
    if executor is None:
        return {}
    try:
        url_to_content = {}
        future_to_url = {
            executor.submit(load_url, url, timeout): url for url in urls
        }
        for future in as_completed(future_to_url):
            with contextlib.suppress(Exception):
                url_to_content[future_to_url[future]] = future.result()
        return url_to_content
    finally:
        executor.shutdown()


def main():
    for meth, fn in [
        ("sequential", functools.partial(download_urls_sequential, URLS)),
        (
            "threads",
            functools.partial(
                download_urls_with_executor, ThreadPoolExecutor(10), URLS
            ),
        ),
        (
            "processes",
            functools.partial(
                download_urls_with_executor, ProcessPoolExecutor(10), URLS
            ),
        ),
        (
            "mpi4py",
            functools.partial(
                download_urls_with_executor, MPIPoolExecutor(10), URLS
            ),
        ),
    ]:
        sys.stdout.write(f"{meth.ljust(11)}: ")
        sys.stdout.flush()
        start = time.time()
        url_map = fn()
        elapsed = time.time() - start
        m, n = len(url_map), len(URLS)
        sys.stdout.write(
            f"{elapsed:5.2f} seconds ({m:2d} of {n:d} downloaded)\n",
        )
        sys.stdout.flush()


if __name__ == "__main__":
    main()
