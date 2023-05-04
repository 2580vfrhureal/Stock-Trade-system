import numpy as np
import matplotlib.pyplot as plt

p = [0, 0.2, 0.4, 0.6, 0.8, 1]
query = [0.0725, 0.0693, 0.0832, 0.0703, 0.0635, 0.0652]
trade = [0.0, 0.0879, 0.0928, 0.0880, 0.0781, 0.0896]

plt.plot(p, query, label = 'query')
plt.plot(p, trade, label = 'trade')

# Add labels and title
plt.xlabel('probability')
plt.ylabel('average latency')
plt.title('test result without caching')

plt.legend()
# Display the plot
plt.show()

