#!/usr/bin/env python3

import pygame
import os
import pandas as pd
import random
import argparse

# === === === === #
#   DEFINITIONS   #
# === === === === #

WIN_WIDTH = 640    # [px]
WIN_HEIGHT = 640   # [px]
WIN_FRAMERATE = 40 # FPD
WIN_PADDING = 40
WIN_NAME = "Simple sudoku game"

cell_size = ((WIN_WIDTH - 2*WIN_PADDING)/9, (WIN_HEIGHT - 5*WIN_PADDING)/9)
cell_edge = min(cell_size)
grid_size = (cell_edge*9,cell_edge*9)
grid_root = ((WIN_WIDTH-grid_size[0])/2,WIN_PADDING*2)

gameDisplay = None
gameClock = None
gameFontBasic = None
gameFontBold = None


square_colors =[(255, 77, 77),
				(255,166, 77),
				(255,255, 77),
				(166,166, 77),
				( 77,255,255),
				( 77,166,255),
				(166, 77,255),
				(255, 77,166),
				(128,128,128), # 1-9 colors for squares
				(255,255,255)]# last color for number bar
# === === === === #
#     CLASSES     #
# === === === === #

class SudokuPosition:
	"""  define redundant positioning tripplet with row and coll and square indices
		row is counted from top to bottom [0..8]
		coll is counted left to right [0..8]
		square follows the same order from left to right top to bottom [0..8]"""
	def __init__(self, row: int, col: int, square: int= None):
		if row not in (0,1,2,3,4,5,6,7,8):
			raise ValueError("Error in row initialization with impropper value")
		else:
			self.row = row
		if col not in (0,1,2,3,4,5,6,7,8):
			raise ValueError("Error in coll initialization with impropper value")
		else:
			self.col = col
		if square is None:			
			self.square = row//3 + 3*(col//3)
		else:
			self.square = square

	def __eq__ (self, other):
		if self.row != other.row:
			return False
		if self.col != other.col:
			return False
		return True		

	def __ne__(self, other):
		return not(self.__eq__(other))

class SudokuNumber:
	
	def __init__(self, num: int, row: int, col: int, given: bool = False, square: int = None):
		self.npos = SudokuPosition(row, col, square)	
		self.pencilmarks = {}
		self.number = num

		self.given = given
		self.mouseover = False
		self.selected = False

		self.root = (0,0)
		self.size = (40,40)
		self.pos = ( self.root[0] + self.size[0]*self.npos.row ,
				 	 self.root[1] + self.size[1]*self.npos.col)
		self.rect = pygame.Rect(self.pos, self.size)
		self.set_colors()

	def set_colors(self, letter: tuple =None, background : tuple =None, selected: tuple =None, mouseover: tuple =None):
		if letter is None:
			self.color = (255,255,255)
		else:
			self.color = letter
		if background is None:
			self.background = square_colors[self.npos.square]
		else:
			self.background = background
		self.background_selected = selected
		self.background_mouseover = mouseover
		# self.background = square_colors[self.npos.square]
		# self.background_selected = (150,30,30)
		# self.background_mouseover = (30,150,30)

	def set_restriction(self, all_grid):
		self.restriction = SudokuRestriction(all_grid, self)
		self.pencilmarks = self.restriction.candidates

	def set_in_grid(self, root: tuple, size: float):
		self.root = root		
		self.size = (size,size)
		self.pos = ( self.root[0] + self.size[0]*self.npos.row ,
				     self.root[1] + self.size[1]*self.npos.col)
		self.rect = pygame.Rect(self.pos, self.size)

	def set_number(self, number):
		if self.given is False:
			if number in (0,1,2,3,4,5,6,7,8,9):
				self.number = number
		else:		
			print("Can't change given number")

	def set_pencilmark(self, number):
		if self.given is False:
			if number in (0,1,2,3,4,5,6,7,8,9):
				if number not in self.pencilmarks:
					self.pencilmarks.append(number)
		else:		
			print("Can't change given number")
			

	def is_valid(self):	
		if self.given:
			return True
		if self.number in self.restriction.candidates:
			return True
		return False

	def update(self, mouse_pos, button):		
		if self.rect.collidepoint(mouse_pos[0], mouse_pos[1]):
			self.mouseover = True
			if button == 1:
				self.selected = True
				return self			
		else:	
			self.mouseover = False
			if button is not None :
				self.selected = False
		return None

	def draw(self):		
		if (self.selected is True) and (self.background_selected is not None):			
			gameDisplay.fill(self.background_selected,self.rect)
			# pygame.draw.rect(gameDisplay,self.background_selected,self.rect,2)
		elif (self.mouseover is True) and (self.background_mouseover is not None):
			gameDisplay.fill(self.background_mouseover,self.rect)
			# pygame.draw.rect(gameDisplay,self.background_mouseover,self.rect,2)			
		else:			
			gameDisplay.fill((0,0,0),self.rect)
		
		pygame.draw.rect(gameDisplay,self.background,self.rect,2)

		if self.given:
			number_label = gameFontBold.render(f"{self.number}",True,self.color) 			
			gameDisplay.blit(number_label,(	self.pos[0] + (self.size[0] - number_label.get_width())/2,
											self.pos[1] + (self.size[1] - number_label.get_height())/2))			
		elif self.number > 0:
			if self.number not in self.restriction.candidates:
				number_label = gameFontBasic.render(f"{self.number}",True,(255,0,0)) 
			else:
				number_label = gameFontBasic.render(f"{self.number}",True,self.color) 
			gameDisplay.blit(number_label,(	self.pos[0] + (self.size[0] - number_label.get_width())/2,
											self.pos[1] + (self.size[1] - number_label.get_height())/2))			
		else:
			for num in self.pencilmarks:
				number_label = gameFontSmall.render(f"{num}",True,self.color) 			
				
				gameDisplay.blit(number_label,(	self.pos[0] + ((num-1)//3)*self.size[0]/3 + (self.size[0]/3 - number_label.get_width())/2,
												self.pos[1] + ((num-1)%3)*self.size[1]/3 + (self.size[1]/3 - number_label.get_height())/2))					
			return

			

class SudokuRestriction:
	
	def __init__(self, all_grid, sn: SudokuNumber):
		self.sn = sn
		self.neighbors = []		
		for el in all_grid:
			if el.npos == sn.npos:
				continue
			if (el.npos.row == self.sn.npos.row) or (el.npos.col == self.sn.npos.col) or (el.npos.square == self.sn.npos.square):
				self.neighbors.append(el)
		self.candidates = self.get_candidates()

	def get_candidates(self):
		if self.sn.given is True:
			return {self.sn.number}
		candidates = {1,2,3,4,5,6,7,8,9}
		for el in self.neighbors:
			candidates = candidates.difference({el.number})
		return candidates

	def __repr__(self):
		return str(self.sp) + str(self.neighbors)

class SudokuGrid:

	def __init__(self, pos:tuple, size:float ):
		self.pos = pos
		self.size = size
		self.fill_cells([0]*9*9)
		self.selected_cell = None
		self.finished = False

	def fill_cells(self, numbers:list, letter: tuple =None, background : tuple =None, selected: tuple =None, mouseover: tuple =None):
		self.cells = []
		for (ind, num) in enumerate(numbers):
			if (type(num) == str):
				if num in {'1','2','3','4','5','6','7','8','9'}:
					num = int(num)
				else:
					num = 0
			sn = SudokuNumber(num,ind%9,ind//9,num > 0)
			sn.set_in_grid(self.pos, self.size[0]/9)
			sn.set_colors(letter, background, selected, mouseover)
			self.cells.append(sn)
		for el in self.cells:
			el.set_restriction(self.cells)
			# print(el.restriction) # DEBUG

	def set_colors(self, letter: tuple =None, background : tuple =None, selected: tuple =None, mouseover: tuple =None):
		for el in self.cells:
			el.set_colors(letter, background, selected, mouseover)

	def update(self, mouse_pos, button):
		finished = True
		for el in self.cells:
			tmp = el.update(mouse_pos, button)
			if tmp is not None:
				self.selected_cell = tmp
			finished = finished and el.is_valid()
		self.finished = finished

	def draw(self):
		for el in self.cells:
			el.draw()

	def get_puzzle_state_str(self):
		puzzle_str = ""
		for el in self.cells:
			if el.number == 0:
				puzzle_str += "."
			else:
				puzzle_str += f"{el.number}"
		return puzzle_str

class GridLoader:

	def __init__(self, datafile, scorefile):
		self.datafile = datafile
		self.scorefile = scorefile

		self.data = pd.read_csv(datafile, index_col=False)
		self.score = pd.read_csv(scorefile, index_col=False)
		# self.data = pd.read_csv(datafile)
		# self.score = pd.read_csv(scorefile)
		# print(self.score) #DEBUG

		self.current_puzzle = None

	def select_puzzle(self, challange_level):
		print(self.score["Puzzle_id"])
		available = self.data.drop(self.score["Puzzle_id"])
		available = available[ self.data["Difficulty"] == challange_level]
		# print(available) #DEBUG
		self.current_puzzle_index = random.choice(available.index)
		puzzle = available.loc[self.current_puzzle_index,"Puzzle"]

		print(f"selecting {challange_level} puzzle: {puzzle}") # LOG inof

		sg = SudokuGrid(grid_root, grid_size )
		sg.fill_cells( list(puzzle), selected=(150,30,30), mouseover=(30,150,30))
		self.current_puzzle = sg
		return sg

	def new_score(self, time):
		self.score = self.score.append({
			"Time": time,
			"Finished": self.current_puzzle.finished,
			"Puzzle_id": self.current_puzzle_index,
			"Puzzle_state": self.current_puzzle.get_puzzle_state_str()},
			ignore_index=True,
			verify_integrity=True)
		self.score.to_csv(self.scorefile,
			index=False)

class NumberPanel:

	def __init__(self, pos:tuple, size:tuple):
		self.pos = pos
		self.size = size
		self.fill_cells([1,2,3,4,5,6,7,8,9])

	def fill_cells(self, numbers:list):
		self.cells = []
		for (ind, num) in enumerate(numbers):
			sn = SudokuNumber(num,ind%9,ind//9,True,9)
			sn.set_in_grid(self.pos, self.size[0]/9)
			self.cells.append(sn)

	def set_colors(self, letter: tuple =None, background : tuple =None, selected: tuple =None, mouseover: tuple =None):
		for el in self.cells:
			el.set_colors(letter, background, selected, mouseover)

	def set_number(self, key, selected_cell:SudokuNumber):
		tmp_num = -1
		if (key == pygame.K_9) or (key == pygame.K_KP9):
			tmp_num = 9
		elif (key == pygame.K_8) or (key == pygame.K_KP8):
			tmp_num = 8
		elif (key == pygame.K_7) or (key == pygame.K_KP7):
			tmp_num = 7
		elif (key == pygame.K_6) or (key == pygame.K_KP6):
			tmp_num = 6
		elif (key == pygame.K_5) or (key == pygame.K_KP5):
			tmp_num = 5
		elif (key == pygame.K_4) or (key == pygame.K_KP4):
			tmp_num = 4
		elif (key == pygame.K_3) or (key == pygame.K_KP3):
			tmp_num = 3
		elif (key == pygame.K_2) or (key == pygame.K_KP2):
			tmp_num = 2
		elif (key == pygame.K_1) or (key == pygame.K_KP1):
			tmp_num = 1
		elif (key == pygame.K_0) or (key == pygame.K_KP0):
			tmp_num = 0
		elif (key == pygame.K_DELETE) or (key == pygame.K_BACKSPACE):
			tmp_num = 0

		if (selected_cell is not None) and (tmp_num != -1):
			selected_cell.set_number(tmp_num)

	def update(self, mouse_pos, button, selected_cell:SudokuNumber):
		self.set_available(selected_cell)
		for el in self.cells:
			tmp = el.update(mouse_pos, button)
			if (tmp is not None) and (selected_cell is not None):
				# print(selected_cell)
				# print(tmp.number)
				selected_cell.set_number(tmp.number)

	def set_available(self, selected_cell:SudokuNumber):
		candidates = {}
		if selected_cell is not None:
			candidates = selected_cell.restriction.get_candidates()
		for (ind,el) in enumerate(self.cells):
			if ind+1 in candidates:
				el.set_colors(letter=(255,255,0))
			else:
				el.set_colors()

	def draw(self):
		for el in self.cells:
			el.draw()

class TimerPanel:

	def __init__(self, pos, size, clock:pygame.time.Clock):
		self.pos = pos
		self.size = size
		self.clock = clock
		self.time = 0

	def update(self, finished:bool):
		if not finished:
			self.time += self.clock.get_time()


	def draw(self):
		time = self.time//1000
		self.timestr = f"{time//60:02d}:{time%60:02d}"
		number_label = gameFontBold.render(self.timestr, True, (255,255,255)) 			
		
		gameDisplay.blit(number_label,(	self.pos[0] + (self.size[0] - number_label.get_width())/2,
										self.pos[1] + (self.size[1] - number_label.get_height())/2))			
			


def draw_window():
	"""function for updating graphics in the window"""
	# label_test = gameFontBasic3.render("test",True,(255,255,255))
	# gameDisplay.blit(label_test,(int((WIN_WIDTH - label_test.get_width())/2),
	# 							 int((WIN_HEIGHT - label_test.get_height())/2)))
	pygame.display.update()

if __name__ == "__main__":
	""" function for launching the core of apliacation and game loop"""

	# init
	pygame.init()
	pygame.font.init()
	pygame.display.set_caption(WIN_NAME)
	# set up 
	gameDisplay = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
	gameClock = pygame.time.Clock()
	gameFontSmall = pygame.font.SysFont("Arial", 12, bold=False)
	gameFontBasic = pygame.font.SysFont("Arial", 26, bold=False)
	gameFontBold = pygame.font.SysFont("Arial", 30, bold=True)
	
	# parsing the input
	parser = argparse.ArgumentParser(description="Process the difficulty level of a task.")

	parser.add_argument("difficulty",
						metavar= "difficulty",
						choices=["Easy", "Intermediate", "Expert"],
						nargs="?",
						default="Easy",
						help="Set the difficulty level (Easy, Intermediate, or Expert).")

	args = parser.parse_args()
	print(args.difficulty)

	# load the puzzle
	loader = GridLoader("puzzle_data.csv", "score.csv")
	sg = loader.select_puzzle(args.difficulty)


	# initialization of the display
	panel_size = (cell_edge*9,cell_edge)
	panel_root = (grid_root[0],WIN_HEIGHT- WIN_PADDING - panel_size[1] )
	np = NumberPanel(panel_root, panel_size)
	np.set_colors(background=(255,255,255))
	
	timer_root = (grid_root[0],WIN_PADDING/2 )
	tp = TimerPanel(timer_root, panel_size, gameClock)

	runGame = True

	while runGame:

		# mouse_pos = pygame.mouse.get_pos()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				runGame = False
				print(f"You have exited the sudoku game at {tp.timestr} [mm:ss]")
				print(f"current state: {sg.get_puzzle_state_str()}")
				loader.new_score(tp.timestr)
			if event.type == pygame.MOUSEMOTION:
				sg.update(event.pos,None)
				np.update(event.pos,None,sg.selected_cell)
			if event.type == pygame.MOUSEBUTTONUP:
				sg.update(event.pos,event.button)
				np.update(event.pos,event.button,sg.selected_cell)
			if event.type == pygame.KEYUP:
				np.set_number(event.key,sg.selected_cell)
		tp.update(sg.finished)
		if sg.finished:
			print(f"You have finished the sudoku game at {tp.timestr} [mm:ss]")
			loader.new_score(tp.timestr)
			runGame = False

		# sg.update(mouse_pos,False)
		gameDisplay.fill((0,0,0))
		sg.draw()
		np.draw()
		tp.draw()

		draw_window()

		gameClock.tick(WIN_FRAMERATE)
