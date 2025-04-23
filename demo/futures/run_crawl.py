from urllib.request import urlopen

from mpi4py.futures import MPIPoolExecutor

URLS = [
    "http://www.google.com/",
    "http://www.apple.com/",
    "http://www.ibm.com/",
    "http://www.slashdot.org/",
    "http://www.python.org/",
    "http://www.bing.com/",
    "http://www.facebook.com/",
    "http://www.github.com/",
    "http://www.youtube.com/",
    "http://www.blogger.com/",
]


def load_url(url):
    return url, urlopen(url).read()


def test_crawl():
    with MPIPoolExecutor(10) as executor:
        for url, content in executor.map(
            load_url, URLS, timeout=10, unordered=True
        ):
            kib = len(content) / (1 << 10)
            print(f"{url:25s}: {kib:6.2f} KiB")


if __name__ == "__main__":
    test_crawl()
