from params import *
from model_functions import *


data=read_data()
print(data.head())
print(len(data))
data=clean(data)
print(data.head())
print(len(data))

# print(data.dtypes)
