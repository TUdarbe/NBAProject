import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

x = np.array([0.46,0.59,0.68,0.99,0.39,0.31,1.09,
              0.77,0.72,0.49,0.55,0.62,0.58,0.88,0.78])
y = np.array([0.315,0.383,0.452,0.650,0.279,0.215,0.727,0.512,
              0.478,0.335,0.365,0.424,0.390,0.585,0.511])

sns.plot(x,y)
sns.show()