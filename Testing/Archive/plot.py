import matplotlib.pyplot as plt
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)


plt.rcdefaults()
fig, ax = plt.subplots()

# Example data
people = ('Sequential', 'Parallel v.1', 'Parallel v.2')
y_pos = np.arange(len(people))
performance = (36.4101, 35.9719, 29.931)

ax.barh(y_pos, performance, align='center')
ax.set_yticks(y_pos)
ax.set_yticklabels(people)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Speed (seconds)')
ax.set_title('Without creating tiles (Overall execution time)')

plt.show()