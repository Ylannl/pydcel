def writegrid2ply(outfile, n=9):
	"""Writes an nxn grid to a ply file"""
	n_vertices = n**2
	n_faces = 2 * (n-1)**2

	s = """ply
	format ascii 1.0
	comment python generated
	element vertex {}
	property float x
	property float y
	property float z
	element face {}
	property list uchar int vertex_indices
	end_header\n""".format(n_vertices, n_faces)

	for i in xrange(n):
		for j in xrange(n):
			s += "{} {} 0\n".format(i,j)

	for i in xrange(n-1):
		for j in xrange(n-1):
			ul = j*n + i
			ur = ul + 1
			ll = (j+1)*n + i
			lr = ll +1
			s += "3 {} {} {}\n".format(ur, ul, ll)
			s += "3 {} {} {}\n".format(lr, ur, ll)
	
	with open(outfile, 'w') as f:
		f.write(s)