from mip.model import *
from sys import stdout, argv
from time import process_time
import time

Solvers=['cbc', 'gurobi']
N = range(50,501,50)

f = open('queens.csv', 'w')

for n in N:
	for solver in Solvers:
		st = time.time()
		queens = Model('queens', MINIMIZE, solver_name=solver)

		x = [[queens.add_var('x({},{})'.format(i, j), type='B')
			  for j in range(n)] for i in range(n)]

		# objective function
		queens += xsum(-x[i][j] for i in range(n) for j in range(n))

		# one per row
		for i in range(n):
			queens += xsum(x[i][j] for j in range(n)) == 1, 'row({})'.format(i)

		# one per column
		for j in range(n):
			queens += xsum(x[i][j] for i in range(n)) == 1, 'col({})'.format(j)

		# diagonal \
		for p, k in enumerate(range(2 - n, n - 2 + 1)):
			queens += xsum(x[i][j] for i in range(n) for j in range(n) if i - j == k) <= 1, 'diag1({})'.format(p)

		# diagonal /
		for p, k in enumerate(range(3, n + n)):
			queens += xsum(x[i][j] for i in range(n) for j in range(n) if i + j == k) <= 1, 'diag2({})'.format(p)

		ed = time.time()

		print('n {} cols {} rows {} solver {} time {}'.format(n, queens.num_cols, queens.num_rows, solver, ed-st))

		f.write('{},{},{:.4f}\n'.format(n, solver, ed-st))

f.close()