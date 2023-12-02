"""
Downloader class is a wrapper for libtorrent library.
It allows to download a single file from a torrent file.
"""

import libtorrent as lt
import time
import threading

class Downloader:
    def __init__(self, torrent_path):
        self.ses = lt.session()
        self.ses.add_extension('ut_metadata')
        self.ses.add_extension('ut_pex')
        self.ses.add_extension('metadata_transfer')

        self.info = lt.torrent_info(torrent_path)
        self.handle = self.ses.add_torrent({'ti': self.info, 'save_path': '.'})
        self.torrent_file = torrent_path
        self.download_thread = None

    def get_files_list(self):
        return {file_index: {"filename": file.path, "size_bytes": file.size}
                for file_index, file in enumerate(self.info.files())}

    def download(self, file_index, download_path):
        # Set file priorities
        self.handle.file_priority(file_index, 7)  # Highest priority for the selected file
        for i in range(self.info.num_files()):
            if i != file_index:
                self.handle.file_priority(i, 0)  # Do not download other files

        self.handle.move_storage(download_path)

        if self.download_thread is None or not self.download_thread.is_alive():
            self.download_thread = threading.Thread(target=self._download)
            self.download_thread.start()

    def _download(self):
        while not self.handle.is_seed():
            time.sleep(1)

    def get_status(self):
        s = self.handle.status()
        return {
            "progress": s.progress * 100,
            "download_rate": s.download_rate,
            "upload_rate": s.upload_rate,
            "num_peers": s.num_peers,
            "state": s.state
        }

    def is_downloading(self):
        return self.download_thread is not None and self.download_thread.is_alive()

# Example usage
if __name__ == "__main__":
    torrent_file = 'path/to/torrent_file.torrent'
    downloader = Downloader(torrent_file)

    # List files
    files = downloader.get_files_list()
    print(files)

    # Start download
    file_index = 0  # Example file index
    download_path = 'path/to/download'
    downloader.download(file_index, download_path)

    # Check status periodically
    while downloader.is_downloading():
        print(downloader.get_status())
        time.sleep(5)
