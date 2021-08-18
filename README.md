CodeNames
=========

This project is an attempt to create an AI that can play the spymaster role in the board game CodeNames at or around the level of a human.

To see a report explaining what I have done and how it performs, [visit here](https://docs.google.com/document/d/1Em-Eb0xMGwogTIeCImytmzTrkSaFKozmYJZQmxP_Ee8/edit?usp=sharing)

Running the Project
-------------------
1. Get the association models and word lists required to run. I have [uploaded the models I have used](https://drive.google.com/drive/folders/12i2WA_B-LHDkjzPFoMXtm2nNspy5qK9y?usp=sharing), the models named with numbers being trimmed versions of [models found here](http://vectors.nlpl.eu/repository/)
2. To run locally:
  <br /> Define what models and engine you want to use at the top of the local.py file
  <br /> Run `python local.py`
3. To run remotely:
  <br /> Define what models and engine you want to use at the top of the remote.py file
  <br /> Start a room on the [codenames website](https://codenames.game/) and copy the room name at the end of the url
  <br /> Run `python remote.py [room name]`
  <br /> Input an name for the ai in the selenium window of the game
  <br /> You can put the game into the background so you do not see the cipher, but do *not* minimize the selenium window
  <br /> Type `init` to set the ai as a spymaster
  <br /> Type `red` or `blue` based on which team's turn it is
