import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
df = pd.read_csv('Test.csv', delimiter=',')

diff_scores = []
diff_distance = []
for i in range(len(df)):
    diff = df.iloc[i]["score2"] - df.iloc[i]["score1"]
    diff_scores.append(diff)
    diff_distance.append(df.iloc[i]["distance"])

print(np.mean(diff_scores))
plt.scatter(diff_scores, diff_distance)
plt.xlabel('Difference in score')
plt.ylabel('Distance between sentences')
plt.show()
