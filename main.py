from http.server	import HTTPServer,BaseHTTPRequestHandler
from win32api		import SetConsoleTitle as title
from json			import dumps as encodeJSON
import os,cv2 as cv

vidName =	"video.mp4"
vid =		cv.VideoCapture(vidName)

assert vid.isOpened(),"failed to open "+vidName

vidFrameCount:int =	int(vid.get(cv.CAP_PROP_FRAME_COUNT))
vidWidth:int =		int(vid.get(cv.CAP_PROP_FRAME_WIDTH)/4)
vidHeight:int =		int(vid.get(cv.CAP_PROP_FRAME_HEIGHT)/4)

frames:list[list[list[int]]] =	[]

class HTTPRequestHandler(BaseHTTPRequestHandler):
	@property
	def data(self) -> bytes:
		return self.rfile.read(int(self.headers.get("Content-Length","0")))
	def send(self,arg:str|bytes|object):
		arg:str = arg.decode(errors="replace") if isinstance(arg,bytes) else str(arg)
		return self.wfile.write(bytes(arg,"utf-8"))
	def assertContentType(self,required:str) -> bool:
		required = required.lower()
		if self.headers.get("Content-Type","").lower() != required:
			self.send_error(400,f"only content type {required} is applicable")
			return False
		return True
	def do_GET(self):
		if not self.assertContentType("application/json"):return
		self.send_response(200)
		self.send_header("Content-Type","application/json")
		self.end_headers()
		self.send(encodeJSON({"frames":vidFrameCount,"width":vidWidth,"height":vidHeight,"FPS":vid.get(cv.CAP_PROP_FPS)}))
	def do_POST(self):
		if not self.assertContentType("application/json"):return
		data = self.data
		if not data.isdigit():
			self.send_error(400,"must be an integer")
			return
		frameIndex = int(data)-1
		if frameIndex < 0 or frameIndex >= vidFrameCount:
			self.send_error(400,f"out of range (1-{vidFrameCount})")
			return
		self.send_response(200)
		self.send_header("Content-Type","application/json")
		self.end_headers()
		self.send(encodeJSON(frames[frameIndex]))

os.system("cls")

print("Pre-rendering frames...")
while 1:
	notError,frame = vid.read()
	if notError:
		title(f"{len(frames)+1}/{vidFrameCount}")
		frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
		frame = cv.resize(frame,(vidWidth,vidHeight))
		frames.append(frame.tolist())
	else:break

os.system("cls")

title("bad apple server")
serv = HTTPServer(("127.0.0.1",50069),HTTPRequestHandler)
print("\nserver started\n")
try:serv.serve_forever()
except KeyboardInterrupt:
	serv.server_close()
	exit("\nserver closed\n")