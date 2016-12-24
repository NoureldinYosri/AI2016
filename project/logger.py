def save(A,info):
	print "saving"
	f = file("new logger 3.txt","a+");
	f.write("%s\n"%info);
	for b in A:
		f.write(" ".join([str(x) for x in b]));
		f.write("\n");
	f.write("=====================================================\n");
	f.close();
	print "done saving"

def write(s):
	f = file("logger 3.txt","a+");
	f.write(s);
	f.close();
