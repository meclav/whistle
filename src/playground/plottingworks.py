
import numpy as np
import random
from matplotlib import pyplot as plt
from matplotlib import animation
from collections import deque

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure()
ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
line, = ax.plot([], [], lw=2)

# initialization function: plot the background of each frame
def init():
	line.set_data([], [])
	return line,

# animation function.  This is called sequentially

buffer_size = 300

buffer = deque([0]*buffer_size, maxlen=buffer_size)


class Walker:
	def __init__(self,velocity,position,lower_bound,upper_bound):
		self.velocity = velocity
		self.position=position
		self.lower_bound = lower_bound
		self.upper_bound = upper_bound
	
	def next_point(self):
		x = self.position + random.random() * self.velocity
		if x > self.upper_bound:
			x = 2*self.upper_bound - x
			self.velocity *=-1
		elif x < self.lower_bound:
			x  = 2* self.lower_bound - x
			self.velocity *=-1
		self.position = x
		return x	


	
def make_animate( buffer, walker):
	def animate(i):
		x = np.linspace(0, 2, buffer_size)
		buffer.append(walker.next_point())
		y = list(buffer)
		line.set_data(x, y)
		return line,
	return animate
	
w = Walker(0.3,0,0,1)		
animate = make_animate(buffer, w)
# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(fig, animate, init_func=init,
							   blit=True)



plt.show()