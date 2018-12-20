from tspdata import TSPData
from sys import argv
from mip.model import *
from mip.constants import *
import networkx as nx
from math import floor

class SubTourCutGenerator(CutsGenerator):
	def __init__(self, model : "Model", n : int ):
		self.super(model)
		self.n = n

	def generate_cuts(self, vars : List[Var], values : List[float] ) -> List[LinExpr]:
		G = nx.DiGraph()
		for (i, v) in enumerate(vars):
			if 'x(' not in v.name:
				continue
			strarc = v.name.split('(')[1].split(')')[0]
			if abs(values[i])<1e-6:
				continue
			u = int(strarc.split(',')[0].strip())
			v = int(strarc.split(',')[1].strip())
			G.add_edge(u,v, capacity=int(floor(values[i]*10000.0)))

		cuts = []

		for u in range(self.n):
			for v in range(self.n):
				val,part = nx.minimum_cut(G, u, v)
				# checking violation
				if val < 10000:
					continue

				reachable, nonreachable = part

				cutvars = []

				for u in reachable:
					for v in nonreachable:
						var = model.get_var_by_name('x({},{})'.format(u,v))
						if var != None:
							cutvars += var

				cuts.append( xsum(v for v in cutvars) >= 1 )

		return cuts


if len(argv) <= 1:
    print('enter instance name.')
    exit(1)
    
inst = TSPData(argv[1])
n = inst.n
d = inst.d
print('solving TSP with {} cities'.format(inst.n))

model = Model()

# binary variables indicating if arc (i,j) is used on the route or not
x = [ [ model.add_var(
	       name='x({},{})'.format(i,j),
           type=BINARY) 
             for j in range(n) ] 
               for i in range(n) ]

# continuous variable to prevent subtours: each
# city will have a different "identifier" in the planned route
y = [ model.add_var(
       name='y({})'.format(i),
       lb=0.0,
       ub=n) 
         for i in range(n) ]

# objective function: minimize the distance
model += xsum( d[i][j]*x[i][j]
                for j in range(n) for i in range(n) )

# constraint : enter each city coming from another city
for i in range(n):
    model += xsum( x[j][i] for j in range(n) if j != i ) == 1, 'enter({})'.format(i)
    
# constraint : leave each city coming from another city
for i in range(n):
    model += xsum( x[i][j] for j in range(n) if j != i ) == 1, 'leave({})'.format(i)
    
# no 2 subtours
for i in range(n):
    for j in range(n):
        if j!=j:
            model += x[i][j] + x[j][i] <= 1
    
# subtour elimination
for i in range(0, n):
    for j in range(0, n):
        if i==j or i==0 or j==0:
            continue
        model += \
            y[i]  - (n+1)*x[i][j] >=  y[j] -n, 'noSub({},{})'.format(i,j)
                 
    
model.optimize( maxSeconds=10 )
#model.write('tsp.lp')

print('best route found has length {}'.format(model.get_objective_value()))

for i in range(n):
    for j in range(n):
        if x[i][j].x >= 0.98:
            print('arc ({},{})'.format(i,j))

print('finished')        
    
