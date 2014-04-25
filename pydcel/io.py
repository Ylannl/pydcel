from dcel import vertex, hedge, face, DCEL
from sets import Set
from writegrid2ply import writegrid2ply

def ply2datadict(infile):
	"""collect vertex coordinates and normals from input file"""
	datadict = {}
	with open(infile) as f:
		vertexcount = facecount = None
		while True:
			line = f.readline()
			if line.startswith("element vertex"):
				vertexcount = line.split()[-1]
			if line.startswith("element face"):
				facecount = line.split()[-1]
			if line.startswith("end_header"):
				break

		datadict['coords'] = []
		datadict['normals'] = []

		for i in xrange(int(vertexcount)):
			line = f.readline()
			x,y,z= line.split()
			datadict['coords'].append([float(x),float(y),float(z)])

		if facecount is not None:
			datadict['faces'] = []
			for i in xrange(int(facecount)):
				line = f.readline().split()
				vertex_ids = [int(x) for x in line[1:]]
				datadict['faces'].append(vertex_ids)

	return datadict

def datadict2dcel(datadict):
	#assume ccw vertex order
	hedges = {} # he_id: (v_origin, v_end), f, nextedge, prevedge
	vertices = {} # v_id: (e0,...,en) i.e. the edges originating from this v

	m = len(datadict['coords'])
	for i in xrange(m):
		vertices[i] = []

	# find all halfedges, keep track of their vertices and faces
	j=0
	for i, face in enumerate(datadict['faces']):
		# face.reverse()
		n_vertices = len(face)

		for v_i in xrange(n_vertices):
			# store reference to this hedge in vertex list
			vertices[face[v_i]].append(j)

			if v_i ==0:
				hedges[j] = (face[v_i], face[v_i+1]), i, j+1, j+(n_vertices-1)
				vertices[face[v_i+1]].append(j)
			elif v_i < n_vertices-1:
				hedges[j] = (face[v_i], face[v_i+1]), i, j+1, j-1
				vertices[face[v_i+1]].append(j)
			else:
				hedges[j] = (face[v_i], face[0]), i, j-(n_vertices-1), j-1
				vertices[face[0]].append(j)
			vertices[face[v_i]].append(j)
			j+=1

	D = DCEL()

	# create vertices for all points
	for v in datadict['coords']:
		dcel_v = D.createVertex(v[0], v[1], v[2])

	# create faces
	for f in xrange(len(datadict['faces'])):
		D.createFace()
	# the last face in the DCEL will be the infinite face:
	infinite_face = D.createInfFace()

	# create all edges except for the ones incident to the infinite face
	for e in xrange(len(hedges)):
		D.createHedge()

	inf_edge = None
	for this_edge, value in hedges.iteritems():
		v, face, nextedge, prevedge = value
		v_origin, v_end = v

		v_origin_edges = Set(vertices[v_origin])
		v_end_edges = Set(vertices[v_end])

		# print v_origin_edges, v_end_edges
		twin_edge = v_origin_edges.intersection(v_end_edges)
		twin_edge.discard(this_edge)
		
		e = D.hedgeList[this_edge]

		if len(twin_edge) == 0: # oh that must be incident to infinite face...
			# face = infinite_face
			e_twin = D.createHedge()
			e_twin.setTopology( D.vertexList[v_end], e, infinite_face, None, None ) # oops, forgetting to set something here...
			inf_edge = e_twin
		else:
			e_twin = D.hedgeList[twin_edge.pop()]
		D.faceList[face].setTopology(e)
		
		e.setTopology( D.vertexList[v_origin], e_twin, D.faceList[face], D.hedgeList[nextedge], D.hedgeList[prevedge] )
		e.origin.setTopology(e)

	# now fix prev/next refs for all edges incident to inf face
	infinite_face.innerComponent = inf_edge
	current_edge = last_correct_edge = inf_edge

	while inf_edge.previous == None:

		current_edge = last_correct_edge
		while current_edge.twin.incidentFace != infinite_face:
			current_edge = current_edge.twin.previous
		current_edge = current_edge.twin

		last_correct_edge.next = current_edge
		current_edge.previous = last_correct_edge
		last_correct_edge = current_edge

	return D

def ply2dcel(infile):
	datadict = ply2datadict(infile)
	return datadict2dcel(datadict)

def dcel2ply(dcel, outfile):
	vertexcount = len(dcel.vertexList)
	facecount = len(dcel.faceList)
	with open(outfile, 'w') as f:
		f.write("ply\n")
		f.write("format ascii 1.0\n")
		f.write("comment python generated\n")
		f.write("element vertex {}\n".format(vertexcount))
		f.write("property float x\n")
		f.write("property float y\n")
		f.write("property float z\n")
		f.write("element face {}\n".format(facecount))
		f.write("property list uchar int vertex_indices\n")
		f.write("end_header\n")

		for v in dcel.vertexList:
			f.write("{} {} {}\n".format(v.x, v.y, v.z))

		for face in dcel.faceList: # don't consider inf face
			vertex_list = [dcel.vertexList.index(v) for v in face.loopOuterVertices()]
			f.write( str(len(vertex_list)) )
			for v_id in vertex_list:
				f.write(" {}".format(v_id))
			f.write("\n")
