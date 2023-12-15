import requests

class Archiver:
    def __init__(self, proxies=None):
        # Initialize a session and configure proxies if provided
        self.session = requests.Session()
        if proxies:
            self.session.proxies.update(proxies)

    def status(self, url):
        """Returns the status of the closest snapshot for the given URL."""
        raise NotImplementedError

    def retrieve(self, url, timestamp=None):
        """Retrieves the content of the closest snapshot for the given URL."""
        raise NotImplementedError

    def submit(self, url):
        """Submits a URL to the archive."""
        raise NotImplementedError

    def close(self):
        """Close the session."""
        self.session.close()


class WaybackArchive(Archiver):
    def status(self, url):
        response = self.session.get(f'https://archive.org/wayback/available?url={url}')
        data = response.json()
        if data['archived_snapshots']:
            snapshot = data['archived_snapshots']['closest']
            return {'url': url, 'timestamp': snapshot['timestamp'], 'status': snapshot['status']}
        else:
            return None

    def retrieve(self, url, timestamp=None):
        if timestamp:
            url = f'https://web.archive.org/web/{timestamp}/{url}'
        else:
            url = f'https://web.archive.org/web/{url}'
        response = self.session.get(url, timeout=10)
        return response.content

    def submit(self, url):
        submit_url = f'https://web.archive.org/save/{url}'
        response = self.session.get(submit_url)
        return response.status_code


if __name__ == '__main__':
    proxies = {
        "http": "http://10.10.1.10:3128",
        "https": "http://10.10.1.10:1080",
    }

    wayback = WaybackArchive(proxies=proxies)

    url = 'http://example.com'
    status = wayback.status(url)
    print('Status:', status)

    wayback.close()