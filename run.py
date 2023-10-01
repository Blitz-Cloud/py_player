from player import MusicPlayer

examplePauze = ["8:50_10m","9:50_10m","10:50_10m","11:50_10m","12:50_10m","13:50_10m","14:50_10m","15:50_10m","16:50_10m","17:50_10m","18:50_10m"]
examplePath = "C:\Users\<User>\Project\py_player\music"
player = MusicPlayer(examplePauze,examplePath )
player.start()
