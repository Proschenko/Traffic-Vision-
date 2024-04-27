from Tracker.main import Master


def main():
    url = 'rtsp://rtsp:EL3gS7XV@80.91.19.85:58002/Streaming/Channels/101'
    Master((url, url)).run()

if __name__ == "__main__":
    main()
