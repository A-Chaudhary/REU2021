
from py2neo import Graph, Node, Relationship, Subgraph #,  NodeMatcher
import pandas as pd
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
import matplotlib.pyplot as plt
import numpy as np
import math



graph = Graph("http://localhost:7474", auth=("neo4j", "password"))
plt.yscale('linear')
plt.close()


nodes = graph.run(
    '''
        MATCH (i:Ingredient) 
        RETURN  i.name AS name, 
                i.degree AS degree, 
                i.weightedDegree AS weightedDegree,
                i.outDegree AS outDegree,
                i.weightedOutDegree AS weightedOutDegree, 
                i.pageRankScore as pageRankScore 
        ORDER BY i.degree ASC
    ''').to_data_frame()
# nodes = pd.DataFrame(nodes)
nodes['degree_ratio'] = nodes['weightedDegree'] / nodes['degree']
nodes['degree_out_ratio'] = nodes['weightedOutDegree'] / nodes['outDegree']
print(len(nodes))
nodes.head(5)
# print(nodes)


# maxv = -1
# for index,i in enumerate(nodes['outDegree']):
#     # print(i)
#     if i > maxv:
#         maxv = i
#         print(index)
# print(maxv)


nodes.loc[128200]


# cutoff = -10
fig, ax = plt.subplots(figsize=(40,40))  # Create a figure containing a single axes.
ax.scatter(nodes['degree'],nodes['weightedDegree'],s = (nodes['pageRankScore'] * 5) ,c = nodes['weightedDegree'], norm=colors.Normalize(True), marker='o')  # Plot some data on the axes.
ax.set_xlabel('Unweighted Degree In', fontsize=60)
ax.set_ylabel('Weighted Degree In', fontsize=60)
ax.set_title('Ingredient Weighted Degree In vs. Unweighted Degree In', fontsize=60)

# x =[ i for i in range(0,nodes['degree'][len(nodes['degree'])-1 ])]
# y =[ i for i in range(0,nodes['degree'][len(nodes['degree'])-1 ])]
# ax.plot(x,y)

# (m, b) = np.polyfit(nodes['degree'], nodes['weightedDegree'], deg=1)
# y1 = [(m*i + b) for i in x]
# ax.plot(x,y1)

# y2 = [2*value - index for (index, value) in enumerate(y1)]
# ax.plot(x,y2)

ax.grid(True)
fig.tight_layout()
plt.yscale('linear')
plt.savefig('img\Ingredient_Degree_Scatter_In.svg', transparent=False)
plt.close(fig)


fig, ax = plt.subplots(figsize=(40,40))  # Create a figure containing a single axes.
ax.scatter(nodes['outDegree'],nodes['weightedOutDegree'],s = (nodes['pageRankScore'] * 5) ,c = nodes['weightedOutDegree'], norm=colors.Normalize(True), marker='o')  # Plot some data on the axes.
ax.set_xlabel('Unweighted Degree Out', fontsize=60)
ax.set_ylabel('Weighted Degree Out', fontsize=60)
ax.set_title('Ingredient Weighted Degree Out vs. Unweighted Degree Out', fontsize=60)

# x =[ i for i in range(0,nodes['degree'][len(nodes) -1 + cutoff])]
# y =[ i for i in range(0,nodes['degree'][len(nodes) -1 + cutoff])]
# ax.plot(x,y)

# (m, b) = np.polyfit(nodes['degree'], nodes['weightedDegree'], deg=1)
# y1 = [(m*i + b) for i in x]
# ax.plot(x,y1)

# y2 = [2*value - index for (index, value) in enumerate(y1)]
# ax.plot(x,y2)

ax.grid(True)
fig.tight_layout()
plt.yscale('linear')
plt.savefig('img\Ingredient_Degree_Scatter_Out.svg', transparent=False)
plt.close(fig)


fig, ax = plt.subplots(figsize=(20,20))  # Create a figure containing a single axes.
ax.scatter(nodes['degree_ratio'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5) ,c=nodes['pageRankScore'], norm=colors.Normalize(True))
ax.set_xlabel('Weighted To Unweighted Degree In Ratio', fontsize=30)
ax.set_ylabel('PageRank Score', fontsize=30)
ax.set_title('Ingredient PageRank Score vs Weighted To Unweighted Degree In Ratio', fontsize=30)


ax.grid(True)
fig.tight_layout()
plt.yscale('linear')
plt.savefig('img\Ingredient_Degree_Scatter_PageRankVsDegreeInRatio.svg', transparent=False)
plt.close(fig)


fig, ax = plt.subplots(figsize=(20,20))  # Create a figure containing a single axes.
ax.scatter(nodes['degree_out_ratio'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5) ,c=nodes['pageRankScore'], norm=colors.Normalize(True))
ax.set_xlabel('Weighted To Unweighted Degree Out Ratio', fontsize=30)
ax.set_ylabel('PageRank Score', fontsize=30)
ax.set_title('Ingredient PageRank Score vs Weighted Out To Unweighted Degree Out Ratio', fontsize=30)


ax.grid(True)
fig.tight_layout()
plt.yscale('linear')
plt.savefig('img\Ingredient_Degree_Scatter_PageRankVsDegreeOutRatio.svg', transparent=False)
plt.close(fig)


fig, ax = plt.subplots(figsize=(20,20))  # Create a figure containing a single axes.
ax.hist(nodes['weightedDegree'][:300], bins=300)
ax.set_xlabel('Weighted Degree In', fontsize=30)
ax.set_ylabel('Count', fontsize=30)
ax.set_title('Ingredient Count vs. Weighted Degree In', fontsize=30)

ax.grid(True)
fig.tight_layout()
plt.yscale('log')
plt.savefig('img\Ingredient_Degree_Hist_Weighted_In.svg', transparent=False)
plt.close(fig)


fig, ax = plt.subplots(figsize=(20,20))  # Create a figure containing a single axes.
ax.hist(nodes['weightedOutDegree'], bins=300)
ax.set_xlabel('Weighted Degree Out', fontsize=30)
ax.set_ylabel('Count', fontsize=30)
ax.set_title('Ingredient Count vs. Weighted Degree Out', fontsize=30)

ax.grid(True)
fig.tight_layout()
plt.yscale('log')
plt.savefig('img\Ingredient_Degree_Hist_Weighted_Out.svg', transparent=False)
plt.close(fig)


scale = 3

fig, axs = plt.subplots(5, 5, figsize=(100,100))
axs[0, 0].scatter(nodes['degree'], nodes['degree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[1, 0].scatter(nodes['degree'], nodes['weightedDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[2, 0].scatter(nodes['degree'], nodes['outDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[3, 0].scatter(nodes['degree'], nodes['weightedOutDegree'], s = (nodes['pageRankScore'] * 5), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[4, 0].scatter(nodes['degree'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5), c=nodes['pageRankScore'], norm=colors.Normalize(True))

axs[0, 1].scatter(nodes['weightedDegree'], nodes['degree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[1, 1].scatter(nodes['weightedDegree'], nodes['weightedDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[2, 1].scatter(nodes['weightedDegree'], nodes['outDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[3, 1].scatter(nodes['weightedDegree'], nodes['weightedOutDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[4, 1].scatter(nodes['weightedDegree'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5), c=nodes['pageRankScore'], norm=colors.Normalize(True))


axs[0, 2].scatter(nodes['outDegree'], nodes['degree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[1, 2].scatter(nodes['outDegree'], nodes['weightedDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[2, 2].scatter(nodes['outDegree'], nodes['outDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[3, 2].scatter(nodes['outDegree'], nodes['weightedOutDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[4, 2].scatter(nodes['outDegree'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5), c=nodes['pageRankScore'], norm=colors.Normalize(True))

axs[0, 3].scatter(nodes['weightedOutDegree'], nodes['degree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[1, 3].scatter(nodes['weightedOutDegree'], nodes['weightedDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[2, 3].scatter(nodes['weightedOutDegree'], nodes['outDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[3, 3].scatter(nodes['weightedOutDegree'], nodes['weightedOutDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[4, 3].scatter(nodes['weightedOutDegree'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5), c=nodes['pageRankScore'], norm=colors.Normalize(True))


axs[0, 4].scatter(nodes['pageRankScore'], nodes['degree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[1, 4].scatter(nodes['pageRankScore'], nodes['weightedDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[2, 4].scatter(nodes['pageRankScore'], nodes['outDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[3, 4].scatter(nodes['pageRankScore'], nodes['weightedOutDegree'], s = (nodes['pageRankScore'] * scale), c=nodes['pageRankScore'], norm=colors.Normalize(True))
axs[4, 4].scatter(nodes['pageRankScore'], nodes['pageRankScore'], s = (nodes['pageRankScore'] * 5), c=nodes['pageRankScore'], norm=colors.Normalize(True))


# axs[0,0].xaxis.set_label_position('top')
# axs[0,1].xaxis.set_label_position('top') 
# axs[0,2].xaxis.set_label_position('top') 
# axs[0,3].xaxis.set_label_position('top') 

fontsize = 50
for i in range(0,5):
    axs[i,0].set_xlabel("Unweighted Degree In", fontsize=fontsize)
    axs[i,1].set_xlabel("Weighted Degree In", fontsize=fontsize)
    axs[i,2].set_xlabel("Unweighted Degree Out", fontsize=fontsize)
    axs[i,3].set_xlabel("Weighted Degree Out", fontsize=fontsize)
    axs[i,4].set_xlabel("PageRank Score", fontsize=fontsize)

    axs[0,i].set_ylabel("Unweighted Degree In", fontsize=fontsize)
    axs[1,i].set_ylabel("Weighted Degree In", fontsize=fontsize)
    axs[2,i].set_ylabel("Unweighted Degree Out", fontsize=fontsize)
    axs[3,i].set_ylabel("Weighted Degree Out", fontsize=fontsize)
    axs[4,i].set_ylabel("PageRank Score", fontsize=fontsize)


# axs.grid(True)
fig.tight_layout()
plt.yscale('linear')
plt.savefig('img\Ingredient_Degree_Scatter_Matrix.svg', transparent=False)
plt.close(fig)


food_nodes = graph.run('MATCH (f:Food) WHERE f.data_type = "branded_food" RETURN f.description AS name, f.numOfIngredients AS degree ORDER BY f.numOfIngredients DESC').to_data_frame()
print(len(food_nodes))
# nodes.head(5)
# print(nodes)


fig, ax = plt.subplots(figsize=(20,20))  # Create a figure containing a single axes.
(y,x,_)= ax.hist(food_nodes['degree'], bins=117)
ax.plot(x[:-1],y)
# print("")
ax.set_xlabel('Unweighted Degree In', fontsize=30)
ax.set_ylabel('Count', fontsize=30)
ax.set_title('Food Count vs. Unweighted Degree Out', fontsize=30)

plt.xticks(np.arange(min(x), max(x)+1, 5))
plt.yticks(np.arange(min(y), max(y)+1, 5000))
ax.grid(True)
fig.tight_layout()
plt.yscale('log')
plt.savefig('img\Food_Degree_Hist_Out.svg')
plt.close()


# df = graph.run('''
# CALL 
# {
#     MATCH (i:Ingredient) 
#     RETURN DISTINCT i.weightedLouvainCommunityId AS communityId
#     } 
# CALL {
#     WITH communityId
#     MATCH p=(i:Ingredient {weightedLouvainCommunityId: communityId})
#     RETURN count(p) AS numOfIngredients
# }
# RETURN communityId, numOfIngredients
# ORDER BY numOfIngredients DESC''').to_data_frame()

# df.head()
# df.to_csv("dict\communities.csv", index = False)


df = pd.read_csv('dict\communities.csv')


fig, ax = plt.subplots(figsize=(20,20))  # Create a figure containing a single axes.
ax.hist(df['numOfIngredients'], bins=150)


ax.set_xlabel('Community Degree In', fontsize=30)
ax.set_ylabel('Count', fontsize=30)
ax.set_title('Count vs. Community Degree In', fontsize=30)

ax.grid(True)
fig.tight_layout()
plt.yscale('log')
plt.savefig('img\Community_Degree_Hist_In.svg')
plt.close()


