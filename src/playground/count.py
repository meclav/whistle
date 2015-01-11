

class Box:
	def __init__(self, x):
		self.value = x


def countWithBox():
	box = 0
	def count():
		nonlocal box
		box+=1
		return box
	return count
	
c = countWithBox()

print(c())
print(c())