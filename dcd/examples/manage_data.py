
from ..entities.property import Property

test_val1 = ([5,1],[10,2],[15,3])
test_val2 = ([6,1],[8,1],[10,1],[13,1],[13,3],[16,4])
p1 = Property("test", values=test_val1)
p2 = Property("test2", values=test_val2)
p1.align_values_to(p2)
print(p1.values)