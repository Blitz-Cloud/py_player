import os
import sys
import json
import math
import time
import re
import random
from pydub import AudioSegment
from pydub.playback import play

# Prototip pt structura pauzelor
# ["7:50_10"]

# Date generale despre program
# acesta primeste ca date de intrare un array de sub forma
# ["hh:mm_d{m/h}"]
# unde hh si mm sunt ora plus durata pauzei in ore sau minute
# iar d este durata pauzei in care trebuie sa se redea muzica
# Pe langa array ul cu pauze acesta primeste de asemenea si path ul pentru folderul
# cu muzica


pauze = ["21:20_5m", "21:25_1m"]


class MusicPlayer:
    def __init__(self, breaks, musicPath) -> None:
        self.breaks = breaks
        self.musicPath = musicPath
        self.index = 0
        self.tracks = os.listdir(musicPath)
        self.bkTracks = self.tracks.copy()
        # doar pt debugging se face o copie a array ul inainte de transformarea
        # in ms
        self.bkBreaks = self.breaks.copy()
        self.__parseInputArray()

    def __randomTrack(self):
        if len(self.tracks):
            track = random.choice(self.tracks)
            trackPath = self.musicPath + "/" + track
            print(f"{track}\n")
            self.tracks.pop(self.index(track))
            return trackPath
        else:
            self.tracks = self.bkBreaks.copy()

    def Play(this, url, duration):
        song = AudioSegment.from_file(url, format="mp3")
        audio = song[:duration]
        play(audio)

    # transforma hh:mm_durata in [hh,mm,durata,h/m],unde hh,mm si durata sunt int
    def __parseInputArray(self):
        regex = r"^(\d{1,2}):(\d{1,2})_(\d+)([hm])$"
        for i in range(0, len(self.breaks)):
            match = re.match(regex, self.breaks[i])
            timeData = []
            if match:
                for match in match.groups():
                    if not (match == "h" or match == "m"):
                        timeData.append(int(match))
                    else:
                        timeData.append(match)
            else:
                raise Exception(
                    "Eroare neasteptata atunci cand s-a incercat valitidatea datelor"
                )

            timeData = self.__convertToMs(
                timeData[0], timeData[1], timeData[2], timeData[3]
            )
            self.breaks[i] = timeData

    # face conversia din [h,min,d?=0] in [ms,ms,d?=0]
    # unde d?=0 este inclus in array doar daca nu este null

    def __convertToMs(self, h, mins, duration=0, durationFormat=0):
        h = h * 3600 * 1000
        mins = mins * 60 * 1000
        duration = (
            duration * 3600 * 1000 if durationFormat == "h" else duration * 60 * 1000
        )

        return (
            {
                "h": h,
                "min": mins,
                "duration": duration,
                "startTime": h + mins,
                "endTime": h + mins + duration,
            }
            if duration
            else {
                "h": h,
                "min": mins,
                "startTime": h + mins,
            }
        )

    def initPlayer(self, duration=0):
        brk = self.breaks[self.index]
        print(brk)
        duration = duration
        if not duration:
            duration = brk["duration"]
        print(duration)
        while duration > 0:
            track = self.__randomTrack()
            ext = track.split(".")[-1]
            audio = AudioSegment.from_file(track, ext)
            length = len(audio)
            if length >= duration:
                length = duration
            audio = audio[:length]
            play(audio)
            duration -= length
        if self.index != len(self.breaks) - 1:
            self.index += 1
            print("Se trece la urmatoarea pauza")
        else:
            self.index = 0
            print("Se trece la prima pauza")
        # marirea / resetare de index

    # se ocupa de selectia intervalului potrivit din array ul cu pauze
    # este important deoarece in cazul in care acesta este pornit mai tarziu decat,
    # acesta sa determine pauza portrivita in care sa redea muzica
    def __syncTimeline(self):
        print("Se alege pauza din in care trebuie sa se redea muzica...")
        curentTime = time.localtime()
        now = self.__convertToMs(curentTime.tm_hour, curentTime.tm_min)
        for i in range(0, len(self.breaks)):
            brk = self.breaks[i]

            # trebuie sa fie verificate doua cazuri
            # daca este inainte de pauza
            # daca este in timpul unei pauze
            if now["h"] == brk["h"]:
                if now["min"] < brk["min"]:
                    self.index = i
                    print(f"Pauza selectata este {self.bkBreaks[i]}")
                elif (
                    now["startTime"] >= brk["startTime"]
                    and now["startTime"] < brk["endTime"]
                ):
                    duration = brk["endTime"] - now["startTime"]
                    bkDuration = duration / (60 * 1000)
                    print(
                        f"Suntem in pauza se v a reda muzica pentru un interval de {bkDuration} min"
                    )
                    self.initPlayer(duration)
                else:
                    # in cazul in care pauza deja a trecut se va selecta urmatoarea pauza din lista
                    self.index = i + 1
                    print(f"Pauza selectata este {self.bkBreaks[i+1]}")

    def start(self):
        print("S a pornit playerul")
        now = time.localtime()
        timeout = 60 - now[5]
        time.sleep(timeout)
        self.__syncTimeline()
        while True:
            locaTime = time.localtime()
            now = self.__convertToMs(locaTime.tm_hour, locaTime.tm_min)

            brk = self.breaks[self.index]
            if brk["startTime"] == now["startTime"]:
                self.initPlayer()
            time.sleep(60)


player = MusicPlayer(pauze, "C:\\Users\\Tudor-Pricop Ionut\\Project\\py_player\music")
player.start()
