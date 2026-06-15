# Zoink Simulator

> Pretend to be the king of Geometry Dash in Pygame!

<sub>school project</sub>

## Overview

> This project is a recreation of the basic functionality of the wave gamemode from **Geometry Dash**, which moves in 45 degrees diagonally up and down. I decided to create this as I have had a lot of passion for the game for the past 6 years, and I thought some of my friends might like it, hence why I named it **Zoink Simulator**, the name of the best player in the game at the moment, also paying homage to a lot of silly simulator games I used to enjoy many years ago by random developers.
## How to Run

1. Make sure you have **Python 3.13** installed.
2. Install the dependencies:
    - `pip install pygame-ce`
3. Run the game:
   ```
   python main.py
   ```

## Controls

| Input             | Action                      |
| ----------------- | --------------------------- |
| Up/W/Spacebar/LMB | Move upward                 |
| R                 | Reset/Suicide               |
| N                 | Enable Noclip/practice mode |
## Dependencies

- Python 3.13
- pygame-ce
## Assets

- `assets/wave.png` - Made via [GD Browser Icon Kit](https://gdbrowser.com/iconkit/)
- `assets/explode.mp3` - Taken from [DELTARUNE](https://store.steampowered.com/app/1671210/DELTARUNE/) Chapter 2's explosion [sound effect](https://www.myinstants.com/en/instant/deltarune-explosion-13037/) (originally from the Hanna-Barbera Library but I couldn't find it)
- `assets/song.mp3` - "[**Pixel Peeker Polka - faster**](https://youtu.be/XosfAzrpjWQ)" by Kevin Macleod
## Resources Used

This project relied on many resources to be create:

- **Gemini AI**
	Helped give direction for what functions to use to achieve effects I wanted, as well as helping with understanding the logic required to make certain functionalities. It also suggested tiny ideas or improvements that I could implement, such as Delta Time. *No code was directly copy and pasted from Gemini.*

- **Pygame Documentation**
	- Allowed me to understand how to use certain functions and their syntax structure.

- **10_pygame_collision.py**
	- Provided a basic boilerplate and some initial reference for the `class` structure and collision logic.

- **Geometry Dash** *(& related online resources*)
	- Source material for my game. The idea is also inspired by the **[Juggernaut Freeplay](https://geode-sdk.org/mods/gdsrwave.jfp?version=1.6.8)** Geode mod made by the GDSR Wave Community. The mod is currently discontinued.

## AI Usage

> As stated, [**Gemini 3.5 Flash**](https://gemini.google.com/app) was very useful and played a key role in being able to create my game. It helped me understand concepts like Delta Time and suggested to use a polygon for my wave trail. 

> I actually applied this polygon idea in Geometry Dash itself to create a fake wave trail out of objects, so I'm confident I understand each of these ideas to their fullest. 

> No code was directly copy and pasted into my project.

## Known Bugs

- The player somewhat bugs out visually when colliding with the floor but is practically negligible.

- When playing at higher game speeds than intended, slopes may generate at different positions due to game lag.
## Possible Improvements

- I could implement ~3 different difficulties which would just involve changing the game speed as right now it is painfully easy for more experienced players such as myself. 
	- However, this would also necessitate allowing for a best time for each difficulty, hence why it was not implemented

- I could improve on the design of the game or add more visual customization, such as with a custom background you could select in a settings menu.

> I'm really proud of how this project turned out. To name a few things I'm especially proud of, I thought the trail system was implemented by me quite brilliantly, and the random slope generation took a lot of brainpower to create the logic due to the very unconventional math involved. A lot of interesting math was involved in most of this project, actually. Also, shoutouts to Terrence and Joshua for playtesting because otherwise the game would have been 3 times faster by default.
