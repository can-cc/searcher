import curses

if __name__ == "__main__":
	import locale

	locale.setlocale(locale.LC_ALL, '')

	screen = curses.initscr()
	begin_x = 20; begin_y = 7
	height = 5; width = 40
	win = curses.newwin(height, width, begin_y, begin_x)
	pad = curses.newpad(10, 50)
	#  These loops fill the pad with letters; this is
	# explained in the next section
	for y in range(0, 10):
		for x in range(0, 10):
			try:
				pad.addch(y,x, ord('a') + (x*x+y*y) % 26)
			except curses.error:
				pass

	pad.refresh(0,0, 1,3, 10,20)
