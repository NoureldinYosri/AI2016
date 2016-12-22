import os;
def norm(grid):
	del grid[11];
	del grid[7];
	del grid[3];
	for i in xrange(9):
		grid[i] = grid[i].replace(' ','');
		grid[i] = grid[i].replace('_','*');
	return grid;

inp = sol = None;
num_steps = [];

def read():
	f = file("gen.out");
	F = [l for l in f];
	f.close();
	global inp,sol
	inp = norm(F[1:13]);
	sol = norm(F[16:(16 + 12)]);

def write(grid,name):
	f = file(name,"w");
	for l in grid:
		f.write("%s"%l);
	f.close();

def run():
	write(inp,"grid.in");
	write(sol,"grid.out");
	os.system("./test < grid.in > out.out 2> num_steps.out");
	os.system("diff out.out grid.out > err.log");

def is_correct():
	f = file("err.log");
	F = [l for l in f];
	f.close();
	return len(F) == 0;


def read_num_steps():
	f = file("num_steps.out");
	F = [l for l in f];
	f.close();
	num_steps.append(int(F[0].split()[2]));	

MAX = 50;
for i in xrange(MAX):
	os.system("python gen.py > gen.out");
	read();
	run();
	if not is_correct():
		print "not correct";
		break;
	print "done with %d cases"%(i + 1);
	read_num_steps();

print num_steps;
