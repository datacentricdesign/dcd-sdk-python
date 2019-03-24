
from ..entities.property import Property

test_val1 = ([5,1],[10,2],[15,3])
d1 = ({'name': 'd1 1'},)
d2 = ({'name': 'd2 1'},)
test_val2 = ([6,1],[8,1],[10,1],[13,1],[13,3],[16,4])
p1 = Property("test", name='Test', values=test_val1, dimensions=d1)
p2 = Property("test2", name='Test 2', values=test_val2, dimensions=d2)
p1.align_values_to(p2)
print(p1.values)
print(p2.values)

p3 = p1.merge(p2)
print(p3.dimensions)
print(p3.values)