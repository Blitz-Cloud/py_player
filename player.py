import os
import sys
import json
import math
import time
import random
from mutagen.mp3 import MP3
from pydub import AudioSegment
from pydub.playback import play

# from pymongo import MongoClient

# host = os.environ["host"]
# db = os.environ["db"]


scriptPath = os.path.dirname(os.path.abspath(__file__))
# client = MongoClient(host)
# db = client[db]
# pauze = db["site_configs"].find_one()["timeTable"]


class MusicPlayer:
    def __init__(this, jsonData, musicPath: str):
        this.pauze = jsonData
        this.musicPath = musicPath
        this.index = 0
        this.traks = os.listdir(musicPath)

    def __validateInputsFormat(self, array: [str]):
        regex = r"^\d{1,2}:\d{1,2}_\d+"
        for i in range(0, len(array)):
            if not re.match(regex, array[i]):
                raise Exception(
                    f"Invalid data set(index:{i+1}) \n{array[i]} \nCan't start the program"
                )

    def __parseInputToGetTime(self, array: [str]):
        regex = r"^(\d{1,2}):(\d{1,2})_(\d+)$"
        for i in range(0, len(array)):
            match = re.match(regex, pauze[i])
            pauza = []
            if match:
                for match in match.groups():
                    pauza.append(int(match))
            else:
                raise Exception("Unexpected error when parsing")
            array[i] = pauza

    def __convertToMs(h: int, min: int):
        return (h * 3600 + min * 60) * 1000

    def __str__(this) -> str:
        return this

    # Este folosita atunci cand programul are nevoie de timpul exact de incepere si terminare al pauzelor
    # va returna ora si minutul de start respectiv de sfarsit al pauzei impreuna cu ora curenta
    def __getBreaks(this, pauza):
        now = time.localtime()
        start, end = pauza.split("_")
        Sh, Sm = start.split(":")
        Eh, Em = end.split(":")
        if int(Em) == 0:
            Em = "60"
        return [int(Sh), int(Sm), int(Eh), int(Em), now]

    # Selecteaza o piesa random din nr lor total
    # sunt necesare inbunatatiri
    def __randomTrack(this):
        track = random.choice(this.traks)
        trackPath = this.musicPath + "/" + track
        sys.stdout.write(f"{track}\n")
        sys.stdout.flush()
        return trackPath

    # trebuie adaugat un fade in si un fade out pt melodii
    def Play(this, url, duration):
        song = AudioSegment.from_file(url, format="mp3")
        audio = song[:duration]
        play(audio)

    # Poate fi folosita in doua instante
    # cu o durata prestabilita atunci cand este folosita in interiorul lui sysncTimeline
    # cu durata default in orice alte cazuri
    # da Play la melodii random atat timp cat durata nu este 0
    def __initPlayer(this, duration=0):
        Sh, Sm, Eh, Em, now = this.__getBreaks(this.pauze[this.index])
        if not duration:
            if Sh < Eh and (Em != 60 or Eh - Sh > 1):
                print("Pauza extra mare initializare normala")
                duration = ((60 - Sm) + (Eh - Sh - 1) * 60 + Em) * 60000
            else:
                duration = (Em - now[4]) * 60000
        while duration > 0:
            track = this.__randomTrack()
            audio = MP3(track)
            trackLenght = math.floor(audio.info.length) * 1000
            if trackLenght >= duration:
                trackLenght = duration
            this.Play(track, trackLenght)
            duration -= trackLenght
        if this.index != len(this.pauze) - 1:
            print("Marire")
            this.index += 1
        else:
            print("Resetare")
            this.index = 0

    # In baza vectorului functia detecteaza care este urmatoarea pauza
    # in functie de ora curenta
    # Iar in cazul in care programul este pornit in timpul unei pauze acesta va chema __initPlayer pt restul de pauza
    # necesita inbunatatiri pt a putea calcula si secundele
    def __syncTimeline(this) -> int:
        # print("Sync")
        for i in range(0, len(this.pauze)):
            Sh, Sm, Eh, Em, now = this.__getBreaks(this.pauze[i])
            if now[3] == Sh:
                if now[4] < Sm:
                    this.index = i
                elif now[4] >= Sm and now[4] < Em and Sh == Eh:
                    print("Suntem in pauza")
                    duration = (Em - now[4]) * 60000
                    this.__initPlayer(duration)
                elif now[4] >= Sm and Sh < Eh:
                    print("Pauza extra mare")
                    duration = ((60 - now[4]) + (Eh - now[3] - 1) * 60 + Em) * 60000
                    this.__initPlayer(duration)
                elif now[4] > Em:
                    print("Mai este pana la pauze")
                    this.index = i + 1
            now = time.localtime()
            if now[3] >= Sh and now[4] >= Em:
                # resetare
                this.index = 0

    # Verifica in fiecare minut daca este momentul in care sa dea drumul la muzica
    # Necesita inbunatatiri pt a da un semnal sonor pt sfarsitul de ora
    def start(this):
        sys.stdout.write("Player started \n")
        sys.stdout.flush()
        now = time.localtime()
        # ringPath = os.path.join(this.musicPath, "..", "ring/ring.wav")
        # timeout = 60 - now[5]
        # time.sleep(timeout)
        this.__syncTimeline()
        while True:
            now = time.localtime()
            Sh, Sm, Eh, Em, now = this.__getBreaks(this.pauze[this.index])
            if now[3] == Sh and now[4] == Sm:
                this.__initPlayer()
            # elif now[3] == Sh and now[4] + 1 == Sm and now[5] == 0:
            # this.Play(ringPath, 3000)
            # time.sleep(60)


print(scriptPath)
player = MusicPlayer(["21:24_21:25"], os.path.join(scriptPath, "music"))
player.start()
