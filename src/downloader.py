import libtorrent as lt
import time
import threading
from typing import Dict, Any


class Downloader:
    def __init__(self, torrentPath: str) -> None:
        self.session = lt.session()
        self.session.add_extension('ut_metadata')
        self.session.add_extension('ut_pex')
        self.session.add_extension('metadata_transfer')

        self.torrentInfo = lt.torrent_info(torrentPath)
        self.handle = self.session.add_torrent(
            {'ti': self.torrentInfo, 'save_path': '.'})
        self.downloadThread = None

    def get_files_list(self) -> Dict[int, Dict[str, Any]]:
        return {
            fileIndex: {"filename": file.path, "sizeBytes": file.size}
            for fileIndex, file in enumerate(self.torrentInfo.files())
        }

    def download(self, fileIndex: int, downloadPath: str) -> None:
        # Set file priorities
        # Highest priority for the selected file
        self.handle.file_priority(fileIndex, 7)
        for i in range(self.torrentInfo.num_files()):
            self.handle.file_priority(i, 0 if i != fileIndex else 7)

        self.handle.move_storage(downloadPath)

        if not self.is_downloading():
            self.downloadThread = threading.Thread(target=self._download)
            self.downloadThread.start()

    def _download(self) -> None:
        while not self.handle.is_seed():
            time.sleep(1)

    def get_status(self) -> Dict[str, Any]:
        status = self.handle.status()
        return {
            "progress": status.progress * 100,
            "downloadRate": status.download_rate,
            "uploadRate": status.upload_rate,
            "numPeers": status.num_peers,
            "state": status.state
        }

    def is_downloading(self) -> bool:
        return self.downloadThread and self.downloadThread.is_alive()


# Example usage
if __name__ == "__main__":
    torrentPath = 'path/to/torrent_file.torrent'
    downloader = Downloader(torrentPath)

    # List files
    files = downloader.get_files_list()
    print(files)

    # Start download
    fileIndex = 0  # Example file index
    downloadPath = 'path/to/download'
    downloader.download(fileIndex, downloadPath)

    # Check status periodically
    while downloader.is_downloading():
        print(downloader.get_status())
        time.sleep(5)
