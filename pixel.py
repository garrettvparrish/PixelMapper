class Pixel:
    def __init__(self, n, x, y):
        self.index = n
        self.x = x
        self.y = y
        self.r = 0
        self.g = 0
        self.b = 127

    def colorString(self):
    	return 	"#%02x%02x%02x" % (int(self.r), int(self.g), int(self.b))
