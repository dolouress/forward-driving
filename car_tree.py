import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.tree import export_text
import pade
#from explore_car1 import data

# Load data from CSV
data = np.loadtxt('car_samples.csv', delimiter=',')
#print(data)
target = data[:, 4]
#print(target)
#theta = data[:, 4]
data = data[:, :4]
print(data)

# Train the qualitative model using PADE
q_table = pade.pade(data, target, nNeighbours=10)
print(q_table)
q_labels = pade.create_q_labels(q_table[:, 3:4], ['gamma'])

classes, class_names = pade.enumerate_q_labels(q_labels)

classifier = tree.DecisionTreeClassifier(min_impurity_decrease=0.02)
model = classifier.fit(data[:, :3], classes)

# Display feature importance
importance = model.feature_importances_
print("Feature importances:", importance)

tree_rules = export_text(model, feature_names=['theta', 'x', 'dx'])

tree.plot_tree(model, feature_names=['theta', 'x', 'dx'], class_names=class_names, filled=True)
plt.show()