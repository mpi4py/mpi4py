"""
Compare the speed of downloading URLs sequentially vs. using futures.
"""

import sys
import time
import functools

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    from concurrent.futures import ThreadPoolExecutor
except ImportError:
    ThreadPoolExecutor = lambda n: None
try:
    from concurrent.futures import ProcessPoolExecutor
except ImportError:
    ProcessPoolExecutor = lambda n: None

from mpi4py.futures import MPIPoolExecutor, as_completed

URLS = [
    'http://www.google.com/',
    'http://www.apple.com/',
    'http://www.ibm.com',
    'http://www.thisurlprobablydoesnotexist.com',
    'http://www.slashdot.org/',
    'http://www.python.org/',
    'http://www.bing.com/',
    'http://www.facebook.com/',
    'http://www.yahoo.com/',
    'http://www.youtube.com/',
    'http://www.blogger.com/',
]

def load_url(url, timeout):
    kwargs = {'timeout': timeout} if sys.version_info >= (2, 6) else {}
    return urlopen(url, **kwargs).read()

def download_urls_sequential(urls, timeout=60):
    url_to_content = {}
    for url in urls:
        try:
            url_to_content[url] = load_url(url, timeout=timeout)
        except:
            pass
    return url_to_content

def download_urls_with_executor(executor, urls, timeout=60):
    if executor is None: return {}
    try:
        url_to_content = {}
        future_to_url = dict((executor.submit(load_url, url, timeout), url)
                             for url in urls)
        for future in as_completed(future_to_url):
            try:
                url_to_content[future_to_url[future]] = future.result()
            except:
                pass
        return url_to_content
    finally:
        executor.shutdown()

def main():
    for meth, fn in [('sequential',
                      functools.partial(download_urls_sequential,
                                        URLS)),
                     ('threads',
                      functools.partial(download_urls_with_executor,
                                        ThreadPoolExecutor(10), URLS)),
                     ('processes',
                      functools.partial(download_urls_with_executor,
                                        ProcessPoolExecutor(10), URLS)),
                     ('mpi4py',
                      functools.partial(download_urls_with_executor,
                                        MPIPoolExecutor(10), URLS))]:
        sys.stdout.write('%s: ' % meth.ljust(11))
        sys.stdout.flush()
        start = time.time()
        url_map = fn()
        elapsed = time.time() - start
        sys.stdout.write('%5.2f seconds (%2d of %d downloaded)\n' %
                         (elapsed, len(url_map), len(URLS)))
        sys.stdout.flush()

if __name__ == '__main__':
    main()
