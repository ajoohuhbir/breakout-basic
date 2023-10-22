# Breakout

This is a clone of [Breakout](https://en.wikipedia.org/wiki/Breakout_(video_game))

Use the A and D keys to move the paddle. Don't let the ball fall off, and try to break all the blocks. If you manage to break all the blocks before your lives run out, you win! Be on the lookout for special blocks and powerups...

# Installation instructions
You will need python and pygame to run this program.  
Installing python: https://www.python.org/downloads/  
Make sure to add it to path!  

Once you've done that, pip should be in path. In the command line, run  
```
pip install pygame
```

Now, you can download the files! Probably the best way to do that is to clone the repository.   
Once you have all the files for the repository, `cd` to that directory, then `cd src` and run  

```
python main.py
```
or
```
python3 main.py
```
(depending on your system)

# Video Demo
A video demo of the installation and running of the program:  
https://youtu.be/ehea1WAf2sE

# Developer notes

While completely playable in its current state, it is still a work-in-progress and many features are yet to be added, like separate levels, the ability to save a game, more powerups, etc. 

The design philosophy behind this program is to separate out all the components of the program such that each one is able to function independently of the other, instead of requiring an environment in which other components are also active. This makes it very easy to separate out behavior. 

In practice, this means that components do not 'know' about any state data not directly relevant to them. The component storing game state does not know aout the rersolution, and the component writing graphics does not know about the game state. Instead, the components communicate with each other by passing in objects that contain instructions on what to do. Thus, state data is passed to the graphics component by the game state component, which lets it know what to draw and where to draw it.

This also separates actual state calculations from any I/O, such as user input or audio-visual output, making it easier to track down which component is a source of bugs.

All code is formatted with [Black](https://pypi.org/project/black/)

# Acknowledgements
All music taken from [Pixabay](https://pixabay.com/music/search/genre/video%20games/)