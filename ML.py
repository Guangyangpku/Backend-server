import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data.csv')
n_users = df.id.nunique()
n_items = df.columns.nunique() - 1

scaler = StandardScaler()
scaler.fit(df.drop('id',axis=1))
scaled_features = scaler.transform(df.drop('id',axis=1))
df_feat = pd.DataFrame(scaled_features,columns=df.columns[1:])
# df_feat.head()

data_matrix = np.zeros((n_users, n_items))

for line in df_feat.itertuples():
    for i in range(n_items):
        data_matrix[line[0], i] = line[i+1]

user_similarity = pairwise_distances(data_matrix, metric='l2')

' '.join([str(i[0]) for i in sorted(enumerate(user_similarity[0]),key=lambda x:x[1])[1:11]])
