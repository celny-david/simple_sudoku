# Info
Simple sudoku game writen in python using pygame.

This is simple past time project for familiarizing oneself with pygame.

# Capabilities
- run the game in CLI with `./sudoku.py`
    - wither make it executable first with `chmod +x sudoku.py`
    - or run it with `python sudoku.py`
- optionally you can select difficulty Easy,Intermediate,Expert
    - the puzzle of chosen difficulty is selected ranomly from `puzzle_data.csv`
- simple help is provided with `-h` flag
- your solution time is tracked
- you can use mouse for selecting the numbers
    - alternatively numeric keys can be used when the cell is selected
- after finishing the new entry is put into `score.csv` for later reference

# Enhancement proposals
- enable loading/continuing unfinished puzzles
- allow for arrow navigation for sell selection
- enable restriction update
