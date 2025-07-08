import time, threading, sys

class PauseThread(threading.Thread):
	def pause(self):
		self.paused = True
		while self.paused:
			time.sleep(0.001)
			if self.stop_thread:
				sys.exit()

	def unpause(self):
		self.paused = False

	def stop(self):
		self.stop_thread = True