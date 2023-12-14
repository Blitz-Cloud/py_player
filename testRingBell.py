import time
from pydub import AudioSegment
from pydub import playback

audio = AudioSegment.from_file("./ring.mp3", "mp3")
audio = audio[: 1.4 * 1000]
audio.export("new.mp3", format="mp3", parameters=["-af", "volume=1"])
