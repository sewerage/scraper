import libtorrent as lt
import time
import sys

def list_torrent_files(torrent_info):
    for file_index, file in enumerate(torrent_info.files()):
        print(f"{file_index}: {file.path} (size: {file.size})")

def download_file(torrent_path, file_index):
    ses = lt.session()
    ses.add_extension('ut_metadata')
    ses.add_extension('ut_pex')
    ses.add_extension('metadata_transfer')

    info = lt.torrent_info(torrent_path)
    h = ses.add_torrent({'ti': info, 'save_path': '.'})

    # Only download the specific file
    h.file_priority(file_index, 7)  # Highest priority
    for i in range(info.num_files()):
        if i != file_index:
            h.file_priority(i, 0)  # Do not download other files

    file_name = info.files().file_path(file_index)
    print(f"Downloading {file_name}...")

    while not h.is_seed():
        s = h.status()
        print(f"\rProgress: {s.progress * 100:.2f}%, Download rate: {s.download_rate / 1000:.2f} kB/s", end="")
        time.sleep(1)

    print("\nDownload complete.")

def main(torrent_path, file_index=None):
    info = lt.torrent_info(torrent_path)

    if file_index is not None:
        download_file(torrent_path, int(file_index))
    else:
        list_torrent_files(info)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <path_to_torrent_file> [index_of_file_to_download]")
        sys.exit(1)

    torrent_file = sys.argv[1]
    file_index = sys.argv[2] if len(sys.argv) > 2 else None
    main(torrent_file, file_index)
