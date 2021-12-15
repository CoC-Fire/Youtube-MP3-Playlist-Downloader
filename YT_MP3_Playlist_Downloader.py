import PySimpleGUI as sg
from sys import exit
from enum import Enum
import os
import youtube_dl
import yt_dlp


class YtdlImpl(Enum):
    yt_dl = 1
    yt_dlp = 2


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    @staticmethod
    def error(msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
    if d['status'] == 'downloading':
        print(d['filename'], d['_percent_str'], d['_eta_str'])


def download_mp3_playlist(playlist_url, destination_path, youtube_dl_impl):
    ydl_opts = {
        'ignoreerrors': True,
        'WriteThumbnail': True,
        'EmbedThumbnail': True,
        'format': 'bestaudio/best',
        'outtmpl': destination_path + '/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
            {'key': 'FFmpegMetadata'},
        ],
        'logger': MyLogger(),
        'progress_hooks': [my_hook]
    }

    if youtube_dl_impl == YtdlImpl.yt_dlp:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
    elif youtube_dl_impl == YtdlImpl.yt_dl:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])


def loadpath():
    file_path = sg.filedialog.askdirectory()
    return file_path


def cancel(*_):
    exit()


def open_and_exit(url_destination):
    os.system('start ' + url_destination)
    exit()


def main():
    sg.theme('DarkRed')

    key_yt_url = 'yt_url'
    key_path = 'path'
    key_start_button = 'key_start_button'
    key_is_yt_dl = 'youtube-dl'
    key_is_yt_dlp = 'youtube-dlp (faster)'

    layout = [
        [sg.Text('YT-playlist Link (or link to single YT-video):')],
        [sg.Input(key=key_yt_url, size=(60, 1), enable_events=True)],
        [sg.Text('')],
        [sg.Text('Please select the destination folder of your downloads:')],
        [sg.Input(key=key_path, size=(60, 1), disabled=True, disabled_readonly_background_color='DarkRed',
                  enable_events=True), sg.Button(button_text="...")],
        [sg.Text('')],
        [sg.Text('Please select a youtube-dl implementation:')],
        [sg.Radio(key_is_yt_dl, "RADIO1", default=False, key=key_is_yt_dl, enable_events=True)],
        [sg.Radio(key_is_yt_dlp, "RADIO1", default=True, key=key_is_yt_dlp, enable_events=True)],
        [sg.Text('')],
        [sg.Button('Start', disabled=True, key=key_start_button, enable_events=True),
         sg.Button('Cancel')]
    ]
    window = sg.Window('Youtube MP3 Playlist Downloader', layout)

    def check_if_button_should_be_enabled():
        if window.Element(key_path).get() and window.Element(key_yt_url).get():
            return True
        else:
            return False

    while True:
        event, values = window.read()

        yt_url = window.Element(key_yt_url).get()
        path = window.Element(key_path).get()
        if window.Element(key_is_yt_dl).get() is True:
            yt_dl_impl = key_is_yt_dl
        else:
            yt_dl_impl = key_is_yt_dlp

        if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
            cancel()
        elif event == key_yt_url:
            window.Element(key_start_button).update(disabled=not check_if_button_should_be_enabled())
        elif event == '...':
            window.Element(key_path).update(loadpath())
            window.Element(key_start_button).update(disabled=not check_if_button_should_be_enabled())
        elif event == key_start_button:
            window.close()
            break

    if yt_dl_impl == key_is_yt_dlp:
        download_mp3_playlist(yt_url, path, YtdlImpl.yt_dlp)
    elif yt_dl_impl == key_is_yt_dl:
        download_mp3_playlist(yt_url, path, YtdlImpl.yt_dl)

    layout_2 = [
        [sg.Text('Your video was successfully downloaded!')],
        [sg.Button('Close'), sg.Button('Close and open folder')]
    ]

    window = sg.Window("Download finished!", layout_2)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit', 'Close'):
            cancel()
        elif event == 'Close and open folder':
            open_and_exit(path)


if __name__ == '__main__':
    main()
