# -*- coding: utf-8 -*-
"""PRML_PROJECT.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dtHK_PmSTusnyQ-WyMxtwrg6Qd0Or5RY

####Mount Google Drive
"""

from google.colab import drive
drive.mount('/content/drive')

"""Import Modules"""

import numpy as np
import pandas as pd
import seaborn as sns
import warnings
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import plotly.express as px
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.cluster import MeanShift
from sklearn.cluster import estimate_bandwidth

#Set Style
sns.set_style("dark");

#ignore warnings
warnings.filterwarnings('ignore')

#Import Data
dataset=pd.read_csv('/content/drive/MyDrive/Country-data.csv')
dataset

"""####Performing Initial Data Visualization"""

#overall lookout of the data
dataset.head()

#information about the dataset
print(dataset.info())

#description of the dataset
print(dataset.describe())

"""#### Data Preprocessing

##### Missing Values
"""

#check for missing values
print("Percentage of missing values:")
print(((dataset.isna().sum())/dataset.shape[0])*100)

"""##### Data Visualization """

#Plots for visualiazing the datset
sns.pairplot(dataset, hue="country", size=3,diag_kind="hist");
plt.show()

#Plotting distributions of the attributes
data = dataset.drop('country',axis = 1)
for i in data.columns:
  print(f"\nPlot density v/s feature {i}\n")
  sns.distplot(data[i])
  plt.show()

#Separting Continous and categorical features
categorical_data=['country']
continuous_data=['child_mort','exports','health','imports','income','inflation','gdpp','total_fer','life_expec']
print(categorical_data)
print(continuous_data)

#Function for classify country into three types low ,median and high feature value
def classifier(data,X,Y):
  df_sorted = data.sort_values(Y, ascending=True)
  length = len(dataset)
  a = int((length + 1)/2)
  plt.figure(figsize=(8, 6))
  plt.title('Countries with low ' + Y)
  sns.barplot(x = X,y = Y, data = df_sorted[:7],palette = 'Paired',edgecolor = 'black')
  plt.show()
  plt.figure(figsize=(8, 6))
  plt.title('Countries with Median ' + Y)
  sns.barplot(x = X,y = Y, data = df_sorted[a-3:a+3],palette = 'Paired',edgecolor = 'black')
  plt.show()
  plt.figure(figsize=(8, 6))
  plt.title('Countries with High ' + Y)
  sns.barplot(x = X,y = Y, data = df_sorted[-6:],palette = 'Paired',edgecolor = 'black')
  plt.show()

"""Visualize the feature classify into three types high,median and low based on the feature value"""

classifier(dataset,'country','gdpp')

classifier(dataset,'country','total_fer')

classifier(dataset,'country','life_expec')

classifier(dataset,'country','inflation')

classifier(dataset,'country','income')

classifier(dataset,'country','imports')

classifier(dataset,'country','health')

#Calculating Correleation matrix
dataset.corr()

#Heatmap for the dataset
sns.heatmap(dataset.corr(),annot = True)

"""#####Data Standardization """

#Standardization of all the continuous features
scaler = StandardScaler()
dataset[continuous_data] = scaler.fit_transform(dataset[continuous_data])

"""# PCA (from scratch)"""

#Function to Centralize the Data
def centralize(data):
  mean = data.mean(axis =0)
  std= data.std(axis=0)
  data_cen = (data-mean)/std
  return data_cen

data_cen = centralize(dataset[continuous_data])

#function to compute covariance matrix from scratch
def covar(data):
  data_val = data.values
  N, M = data_val.shape
  cov = np.zeros((M, M))
  for i in range(M):
    for j in range(M):
      cov[i, j] = np.sum((data_val[:, j]) * (data_val[:, i]))/(N-1)
  return cov
cov=covar(data_cen)
print('covariance matrix for standardized data\n', cov)

#Calculating eigenvalues and eigenvectors
eig_vals, eig_vecs = np.linalg.eig(cov)
print('Eigenvectors are\n', eig_vecs)
print('\nEigenvalues corresponding to eigen vectors are\n', eig_vals)

#finding eigenvalues in decreasing order for non-standarized data
eigen_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
eigen_pairs = sorted(eigen_pairs,key=lambda k: k[0], reverse=True)
print('Eigenvalues in decreasing order for non-standardized data:\n')
for eigen_val in eigen_pairs:
    print(eigen_val[0])

#Calculating variance expressed by each component
#Calculating Cumulative variance 
var_exp = [(i / sum(eig_vals))*100 for i in sorted(eig_vals, reverse=True)]
cum_var_exp = np.cumsum(var_exp)
print("Variance expressed by each component is \n",var_exp)
print("Cumulative variance expressed as we travel each component")
for i in range(8):
    print('Eigenvectors upto',i+1, 'expresses',cum_var_exp[i], '% variance')

#Plotting Explained variance ratio and principal components
def plotting(eig_pairs):
    fig, ax = plt.subplots()
    ax.stem(range(1,10), var_exp, linefmt='r-', markerfmt='ro', label='individual explained variance')
    ax.bar(range(1,10), cum_var_exp,width = 0.2, color='b',alpha=0.5, label='cumulative explained variance')
    ax.set_ylabel('Explained variance ratio')
    ax.set_xlabel('Principal components')
    ax.legend()
    plt.show()

plotting(eigen_pairs)

# top 6 eigenvectors explain upto 97% variance so we will take only the top 6 eigen vectors for transformation
# we get 6 features in our updated data with pca
W=np.hstack((eigen_pairs[0][1][:, ].reshape(data_cen.shape[1],1),
             eigen_pairs[1][1][:, ].reshape(data_cen.shape[1],1),
             eigen_pairs[2][1][:, ].reshape(data_cen.shape[1],1),
             eigen_pairs[3][1][:, ].reshape(data_cen.shape[1],1),
             eigen_pairs[4][1][:, ].reshape(data_cen.shape[1],1),
             eigen_pairs[5][1][:, ].reshape(data_cen.shape[1],1))).real

data_pca = data_cen.dot(W)
data_pca

"""#KMeans"""

#using elbow method to find optimal number of clusters
wcss = []
for i in range(1, 9):
    kmeans = KMeans(n_clusters = i, init = 'k-means++')
    kmeans.fit(data_pca)
    wcss.append(kmeans.inertia_)
plt.plot(range(1, 9), wcss, 'bx-')
plt.title('The elbow method using inertias')
plt.xlabel('Number of clusters')
plt.ylabel('Within-cluster sum of squares (WCSS)')
plt.show()

#Calculate  Silhouette Score
max_score=0
list=[i for i in range(2, 9)]
silhouette=[]
for i in range(2, 9):
    kmeans = KMeans(n_clusters = i)
    kmeans.fit_predict(data_pca)
    score = silhouette_score(data_pca, kmeans.labels_, metric='euclidean')
    if score>max_score:
      clust=i
      max_score=score
    silhouette.append(score)
    print("Silhouette Score for number of clusters =", i , "is", score)

print("the optimul value of clusters is", clust)
plt.plot(list, silhouette)
plt.show()

#Apply Kmeans for number of clusters =4
kmeans = KMeans(n_clusters = 4)
y_kmeans = kmeans.fit_predict(data_pca)

#finding the predicted class labels
print("Predicted Class labels :- ")
print(kmeans.labels_)

#Finding clusters centres
centroids = kmeans.cluster_centers_

#Plotting the clusters in 2d
plt.figure(figsize=(10,5))
plt.scatter(data_pca.iloc[y_kmeans == 0, 0], data_pca.iloc[y_kmeans == 0, 1], s = 50, c = 'red', label = 'Class 0')
plt.scatter(data_pca.iloc[y_kmeans == 1, 0], data_pca.iloc[y_kmeans == 1, 1], s = 50, c = 'cyan', label = 'Class 1')
plt.scatter(data_pca.iloc[y_kmeans == 2, 0], data_pca.iloc[y_kmeans == 2, 1], s = 50, c = 'green', label = 'Class 2')
plt.scatter(data_pca.iloc[y_kmeans == 3, 0], data_pca.iloc[y_kmeans == 3, 1], s = 50, c = 'blue', label = 'Class 3')

#Plotting the centroids of the cluster
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:,1], s = 80, c = 'black', label = 'Centroids', marker='x')
plt.title('Clustering for number of clusters=4')
plt.legend()

# Create the 3D scatter plot
fig = px.scatter_3d(data_pca, x=0, y=1, z=2, color=kmeans.labels_)
fig.show()

#Added kemans predicted class to data_pca
data_pca['Class'] = kmeans.labels_

#Added kemans predicted class to dataset
dataset['Class'] = kmeans.labels_

#Function to plot feature and our predicted class labels
def plot(data,X,Y):
  sns.barplot(x = X, y = Y, data  = data)
  plt.title(Y + ' vs ' + X)
  plt.show()

"""Plotting the each feature with respect to aur predicted kmeans class labels"""

plot(dataset,'Class','child_mort')

plot(dataset,'Class','exports')

plot(dataset,'Class','health')

plot(dataset,'Class','imports')

plot(dataset,'Class','income')

plot(dataset,'Class','inflation')

plot(dataset,'Class','life_expec')

plot(dataset,'Class','total_fer')

plot(dataset,'Class','gdpp')

"""* Class 0 - High
* Class 1 - Low
* Class 2-Upper-MIDDLE
* Class 3- LOWER-MIDDLE
"""

print(data_pca)

#Plotting choropleth
data_pca.insert(0,column = 'Country', value = dataset['country'])
data_pca['Class'].loc[data_pca['Class'] == 0] = 'High'
data_pca['Class'].loc[data_pca['Class'] == 1] = 'Low'
data_pca['Class'].loc[data_pca['Class'] == 2] = 'Upper-middle'
data_pca['Class'].loc[data_pca['Class'] == 3] = 'Lower-middle'

fig = px.choropleth(data_pca[['Country','Class']],locationmode = 'country names',locations = 'Country',title = 'Overall development of the country',color = data_pca['Class'])
fig.show()

"""# DBSCAN"""

#K-Distance Graph
knn = NearestNeighbors(n_neighbors = 7)
model = knn.fit(data_pca.drop(['Class','Country'], axis  = 1))
distances, indices = knn.kneighbors(data_pca.drop(['Class','Country'], axis  = 1))
distances = np.sort(distances, axis=0)
distances = distances[:,1]
plt.grid()
plt.plot(distances);
plt.xlabel('Points Sorted by Distance')
plt.ylabel('7-NN Distance')
plt.title('K-Distance Graph');

#Apply DBSCAN 
db = DBSCAN(eps = 1.3, min_samples = 12).fit(data_pca.drop(['Class','Country'], axis  = 1))
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True

# Number of clusters in db.labels_

n_clusters_ = len(set(db.labels_))
print('Number of Clusters : ', n_clusters_)

data_pca['Class'] = db.labels_; data_pca['Class'] = db.labels_

#Plotting the clusters and outliers in 2d
plt.figure(figsize=(10,5))
data = data_pca.drop('Country',axis =1)
plt.scatter(data.iloc[db.labels_ == 0, 0], data.iloc[db.labels_ == 0, 1], s = 50, c = 'red', label = 'Class 0')
plt.scatter(data.iloc[db.labels_ == 1, 0], data.iloc[db.labels_ == 1, 1], s = 50, c = 'cyan', label = 'Class 1')
plt.scatter(data.iloc[db.labels_ == 2, 0], data.iloc[db.labels_ == 2, 1], s = 50, c = 'green', label = 'Class 2')
plt.scatter(data.iloc[db.labels_ == -1, 0], data.iloc[db.labels_ == -1, 1], s = 50, c = 'black', label = 'Outliers')

plt.title('Clustering for number of clusters=3 and outliers')
plt.legend()

# Create the 3D scatter plot
fig = px.scatter_3d(data_pca, x=0, y=1, z=2, color=db.labels_)
fig.show()

#Added DBSCAN predicted class to data_pca
data_pca['class'] = db.labels_

#Added DBSCAN predicted class to dataset
dataset['class'] = db.labels_

"""Plotting the each feature with respect to aur predicted DBSCAN class labels"""

plot(dataset,'class','child_mort')

plot(dataset,'class','exports')

plot(dataset,'class','exports')

plot(dataset,'class','health')

plot(dataset,'class','imports')

plot(dataset,'class','income')

plot(dataset,'class','inflation')

plot(dataset,'class','life_expec')

plot(dataset,'class','total_fer')

plot(dataset,'class','gdpp')

"""

*  Class 0:Middle
*  Class 1:Low
*  Class 2:High
*  Class -1: Outliers

"""

#Plotting choropleth
data_pca['class'].loc[data_pca['class'] == 0] = 'Middle'
data_pca['class'].loc[data_pca['class'] == 1] = 'Low'
data_pca['class'].loc[data_pca['class'] == 2] = 'High'
data_pca['class'].loc[data_pca['class'] == -1] = 'Outlier'

fig = px.choropleth(data_pca[['Country','class']],locationmode = 'country names',locations = 'Country',title = 'Overall development of the country',color = data_pca['class'])
fig.show()

"""# Hierarchical"""

#plotted dendrogram
linkage_data = linkage(data_pca.drop(['class','Country','Class'],axis = 1), method = 'ward', metric = 'euclidean')
dendrogram(linkage_data)
plt.show()

#Applied Agglomerative clustering
hierarchical_cluster = AgglomerativeClustering(n_clusters = 3, affinity = 'euclidean', linkage = 'ward')
labels = hierarchical_cluster.fit(data_pca.drop(['class','Country','Class'],axis = 1))

pred_agc = pd.Series(hierarchical_cluster.labels_)
data['Class'] = pred_agc; data_pca['Class'] = pred_agc

# Created 3D scatter plot
fig = px.scatter_3d(data_pca, x=0, y=1, z=2, color=hierarchical_cluster.labels_)
fig.show()

data_pca['clas'] = hierarchical_cluster.labels_

dataset['clas'] = hierarchical_cluster.labels_

plot(dataset,'clas','child_mort')

plot(dataset,'clas','exports')

plot(dataset,'clas','health')

plot(dataset,'clas','imports')

plot(dataset,'clas','income')

plot(dataset,'clas','inflation')

plot(dataset,'clas','life_expec')

plot(dataset,'clas','total_fer')

plot(dataset,'clas','gdpp')

#plotted chloropleth graph
data_pca['clas'].loc[data_pca['clas'] == 0] = 'High'
data_pca['clas'].loc[data_pca['clas'] == 1] = 'Low'
data_pca['clas'].loc[data_pca['clas'] == 2] = 'Middle'
fig = px.choropleth(data_pca[['Country','clas']],locationmode = 'country names',locations = 'Country',title = 'Overall development of the country',color = data_pca['clas'])
fig.show()

"""# Mean Shift Clustering"""

#dataset
data = dataset[continuous_data]

#applied mean shift
bandwidth = estimate_bandwidth(data_pca.drop(['class','Country','Class','clas'],axis = 1), quantile=0.2)
ms = MeanShift(bandwidth=bandwidth)
ms.fit(data_pca.drop(['class','Country','Class','clas'],axis = 1))

cluster_centers = ms.cluster_centers_
labels = ms.labels_

silhouette_score(data_pca.drop(['class','Country','Class','clas'],axis = 1), labels)

# plt.show()
fig = px.scatter_3d(data_pca.drop(['class','Country','Class','clas'],axis = 1), x=0, y=1, z=2, color=labels)
fig.show()

#plot clusters in 2D

plt.figure(figsize=(10,5))
data = data_pca.drop('Country',axis =1)
plt.scatter(data.iloc[labels == 0, 0], data.iloc[labels == 0, 1], s = 50, c = 'red', label = 'Class 0')
plt.scatter(data.iloc[labels == 1, 0], data.iloc[labels == 1, 1], s = 50, c = 'cyan', label = 'Class 1')
plt.scatter(data.iloc[labels == 2, 0], data.iloc[labels == 2, 1], s = 50, c = 'green', label = 'Class 2')
plt.scatter(data.iloc[labels == 3, 0], data.iloc[labels == 3, 1], s = 50, c = 'black', label = 'Class 3')
plt.scatter(data.iloc[labels == 4, 0], data.iloc[labels == 4, 1], s = 50, c = 'blue', label = 'Class 4')
plt.scatter(data.iloc[labels == 5, 0], data.iloc[labels == 5, 1], s = 50, c = 'purple', label = 'Class 5')
plt.scatter(data.iloc[labels == 6, 0], data.iloc[labels == 6, 1], s = 50, c = 'pink', label = 'Class 6')

plt.title('Clustering for number of clusters=6')
plt.legend()

"""Plotting the each feature with respect to our predicted spectral class labels"""

data_pca['Clas'] = labels

dataset['Clas'] = labels

plot(dataset,'Clas','child_mort')

plot(dataset,'Clas','exports')

plot(dataset,'Clas','imports')

plot(dataset,'Clas','health')

plot(dataset,'Clas','income')

plot(dataset,'Clas','inflation')

plot(dataset,'Clas','total_fer')

plot(dataset,'Clas','life_expec')

plot(dataset,'Clas','gdpp')

#plot choropleth graph

data_pca['Clas'].loc[data_pca['Clas'] == 0] = 'CLASS 0'
data_pca['Clas'].loc[data_pca['Clas'] == 1] = 'CLASS 1'
data_pca['Clas'].loc[data_pca['Clas'] == 2] = 'CLASS 2'
data_pca['Clas'].loc[data_pca['Clas'] == 3] = 'CLASS 3'
data_pca['Clas'].loc[data_pca['Clas'] == 4] = 'CLASS 4'
data_pca['Clas'].loc[data_pca['Clas'] == 5] = 'CLASS 5'
data_pca['Clas'].loc[data_pca['Clas'] == 6] = 'CLASS 6'
fig = px.choropleth(data_pca[['Country','Clas']],locationmode = 'country names',locations = 'Country',title = 'Overall development of the country',color = data_pca['Clas'])
fig.show()

"""# Spectral Clustering"""

#Dataset
X = data_pca.drop(['class','Country','Class','clas','Clas'],axis = 1)

# Apply spectral clustering
n_clusters = 4
clustering = SpectralClustering(n_clusters=n_clusters, assign_labels='kmeans', random_state=42)
labels = clustering.fit_predict(X)

# plt.show()
fig = px.scatter_3d(X, x=0, y=1, z=2, color=labels)
fig.show()

#Added spectral predicted class to data_pca
data_pca['Cla'] = labels

#Added spectral predicted class to dataset
dataset['Cla'] = labels

"""Plotting the each feature with respect to our predicted spectral class labels"""

plot(dataset,'Cla','child_mort')

plot(dataset,'Cla','income')

plot(dataset,'Cla','imports')

plot(dataset,'Cla','exports')

plot(dataset,'Cla','health')

plot(dataset,'Cla','inflation')

plot(dataset,'Cla','life_expec')

plot(dataset,'Cla','total_fer')

plot(dataset,'Cla','gdpp')

"""

*   Class 0: Lower Middle
*   Class 1: High
*   Class 2: Upper Middle
*   Class 3: Low

"""

#Plot the clusters in 2d
plt.figure(figsize=(10,5))
data = data_pca.drop('Country',axis =1)
plt.scatter(data.iloc[labels == 0, 0], data.iloc[labels == 0, 1], s = 50, c = 'red', label = 'Lower Middle')
plt.scatter(data.iloc[labels == 1, 0], data.iloc[labels == 1, 1], s = 50, c = 'cyan', label = 'High')
plt.scatter(data.iloc[labels == 2, 0], data.iloc[labels == 2, 1], s = 50, c = 'green', label = 'Upper Middle')
plt.scatter(data.iloc[labels == 3, 0], data.iloc[labels == 3, 1], s = 50, c = 'purple', label = 'Low')
plt.title('Clustering for number of clusters=4')
plt.legend()

#Plot choropleth
data_pca['Cla'].loc[data_pca['Cla'] == 0] = 'Lower Middle'
data_pca['Cla'].loc[data_pca['Cla'] == 1] = 'High'
data_pca['Cla'].loc[data_pca['Cla'] == 2] = 'Upper Middle'
data_pca['Cla'].loc[data_pca['Cla'] == 3] = 'Low'
fig = px.choropleth(data_pca[['Country','Cla']],locationmode = 'country names',locations = 'Country',title = 'Overall development of the country',color = data_pca['Cla'])
fig.show()

"""# Gaussian Mixture"""

# Apply Gaussian Mixture Model with 4 clusters
gmm = GaussianMixture(n_components=4, random_state=42)
gmm.fit(X)

# Print the cluster labels for each country
labels = gmm.predict(X)
print("Cluster Labels:\n", labels)

#Plot clusters in 3d
fig = px.scatter_3d(X, x=0, y=1, z=2, color=labels)
fig.show()

#Added gaussian mixture predicted class to data_pca
data_pca['claSS'] = labels

#Added gaussian mixture predicted class to dataset
dataset['claSS'] = labels

"""Plotting the each feature with respect to aur predicted gaussian mixture class labels"""

plot(dataset,'claSS','life_expec')

plot(dataset,'claSS','health')

plot(dataset,'claSS','child_mort')

plot(dataset,'claSS','income')

plot(dataset,'claSS','imports')

plot(dataset,'claSS','exports')

plot(dataset,'claSS','gdpp')

plot(dataset,'claSS','total_fer')

plot(dataset,'claSS','inflation')

#Plot the clusters in 2d
plt.figure(figsize=(10,5))
data = data_pca.drop('Country',axis =1)
plt.scatter(data.iloc[labels == 0, 0], data.iloc[labels == 0, 1], s = 50, c = 'red', label = 'Upper-Middle')
plt.scatter(data.iloc[labels == 1, 0], data.iloc[labels == 1, 1], s = 50, c = 'cyan', label = 'Low')
plt.scatter(data.iloc[labels == 2, 0], data.iloc[labels == 2, 1], s = 50, c = 'green', label = 'Lower-Middle')
plt.scatter(data.iloc[labels == 3, 0], data.iloc[labels == 3, 1], s = 50, c = 'yellow', label = 'High')
plt.title('Clustering for number of clusters=4')
plt.legend()

#Plot choropleth
data_pca['claSS'].loc[data_pca['claSS'] == 0] = 'Upper-Middle'
data_pca['claSS'].loc[data_pca['claSS'] == 1] = 'Low'
data_pca['claSS'].loc[data_pca['claSS'] == 2] = 'Lower-Middle'
data_pca['claSS'].loc[data_pca['claSS'] == 3] = 'High'
fig = px.choropleth(data_pca[['Country','claSS']],locationmode = 'country names',locations = 'Country',title = 'Overall development of the country',color = data_pca['claSS'])
fig.show()