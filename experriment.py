import random
class Sketch:

	def __init__(self, rows,buckets,k):
		self.rows = rows
		self.bucket = buckets
		self.s = [[[] for _ in range(buckets)] for _ in range(rows)]
		self.decode = []
		self.k = k


	def insert(self,f) :
		index = [random.randint(0,self.bucket-1) for _ in range(self.rows)]
		for i in range(self.rows) :
			self.s[i][index[i]].append(f)
		return index

	def print_sketch(self) :
		for i in range(self.rows) :
			print(f"row {i}: ", end="")
			for j in range(self.bucket) :
				print(f"{self.s[i][j]} ", end="")
			print()
		print()

	def verify(self) :
		change = 0
		for i in range(self.rows) :
			for j in range(self.bucket) :
				if len(self.s[i][j]) <= self.k and len(self.s[i][j]) > 0 :
					# print(f"row {i} bucket {j} pure: {self.s[i][j]}")
					for f in self.s[i][j] :
						change = 0
						self.decode.append(f)
						for ii in range(self.rows) :
							for jj in range(self.bucket) :
								if f in self.s[ii][jj] :
									self.s[ii][jj].remove(f)
				else :
					if change >= self.rows * self.bucket :
						return
					change += 1

def compare_accuracy(original, recovered) :
	fp = 0
	fn = 0
	for f in recovered :
		if f not in original :
			fp += 1
	for f in original :
		if f not in recovered :
			fn += 1
	accuracy = (len(original) - (fp + fn)) / len(original) * 100
	return fp, fn, accuracy	

# for b in ball :
# 	insert(b)
# print_sketch()
# verify()
# print("decode:",decode)
# fp, fn, accuracy = compare_accuracy(ball, decode)
# print(f"fp: {fp}, fn: {fn}, accuracy: {accuracy:.2f}%")
bucket_list = [50 * i for i in range(1, 10)]
balls = 100
row = 2
trial = 1000
acc = []

for b in bucket_list :
	accuracys = []
	fps = []
	fns = []
	for _ in range(trial) :
		sketch = Sketch(row,b,k=2)
		ball = [i for i in range(1,balls+1)]
		for f in ball :
			sketch.insert(f)
		# sketch.print_sketch()
		sketch.verify()
		# sketch.print_sketch()
		# print("decode:",sketch.decode)
		fp, fn, accuracy = compare_accuracy(ball, sketch.decode)
		accuracys.append(accuracy)
		fps.append(fp)
		fns.append(fn)
		# print(f"buckets: {b}, fp: {fp}, fn: {fn}, accuracy: {accuracy:.2f}%")
		# print("--------------------------------------------------")
	print(f"buckets: {b}, mean fp: {sum(fps)/trial}, mean fn: {sum(fns)/trial}, mean accuracy: {sum(accuracys)/trial:.2f}%")
	print("--------------------------------------------------")
	acc.append(sum(accuracys)/trial)

from matplotlib import pyplot as plt
plt.plot(bucket_list, acc, marker='o')
plt.xlabel("Number of Buckets")
plt.ylabel("Accuracy (%)")
plt.title("Sketch Accuracy vs. Number of Buckets")
plt.grid(True)
plt.show()	
