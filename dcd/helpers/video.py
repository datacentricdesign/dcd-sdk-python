from threading import Thread
import asyncio
import math
import time

loop = asyncio.get_event_loop()
video_property=None

class VideoRecorder(asyncio.SubprocessProtocol):

    def __init__(self, prop, port='/dev/video0', segment_size='30'):
        self.current_video_file = None
        self.current_video_start_ts = None
        global video_property
        video_property = prop
        self.port = port
        self.segment_size = segment_size

    def start_recording(self):

        try:
            loop.run_until_complete(
                loop.subprocess_exec(SubProcessRecorder,
                                          "ffmpeg",
                                          "-f", "video4linux2",
                                          "-i", self.port,
                                          "-reset_timestamps", "1",
                                          "-f", "segment",
                                          "-segment_time", self.segment_size,
                                          "-segment_format",
                                          "mp4",
                                          "capture-%03d.mp4"))

            loop.run_forever()
        finally:
            print("Closing recording process.")
            loop.close()

    def stop_recording(self):
        loop.stop()


class SubProcessRecorder(asyncio.SubprocessProtocol):

    def __init__(self):
        self.current_video_file = None
        self.current_video_start_ts = None

    def pipe_data_received(self, fd, data):
        # if avconv is opening a new file, there is one ready to send
        line = str(data)
        if "Opening" in line:
            new_time = math.floor(time.time() * 1000)
            new_file = line.split("'")[1]
            print(new_file)

            if self.current_video_file is not None:
                file_name = self.current_video_file
                ts = self.current_video_start_ts
                duration = new_time - ts
                thread = Thread(target=video_property.update_values,
                                kwargs={"values": [duration], "time_ms": ts, "file_name":file_name})
                thread.start()
            self.current_video_start_ts = new_time
            self.current_video_file = new_file

    def connection_lost(self, exc):
        loop.stop()  # end loop.run_forever()
