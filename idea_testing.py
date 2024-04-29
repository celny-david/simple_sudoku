#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

if __name__ == "__main__":
	filename = "sudoku_solved.txt"
	with open(filename) as f:
		sudoku = np.loadtxt(f)


	print(sudoku)
	
	# show the bar plot of solved
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection='3d')

	print(np.shape(sudoku))

	(x_dim, y_dim) = np.shape(sudoku)
	xx = np.tile(np.arange(x_dim),y_dim)
	yy = np.repeat(np.arange(y_dim),x_dim)
	bot = np.zeros_like(sudoku)

	print(xx)
	print(yy)
	print(bot.flatten())

	ax1.bar3d(xx, yy, bot.flatten(), 1, 1, sudoku.flatten(), shade=True)
	plt.show()