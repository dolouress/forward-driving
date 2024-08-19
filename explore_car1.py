import numpy as np
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.tree import export_text
import pade

# Load data from CSV
data = np.loadtxt('car_samples.csv', delimiter=',')
print("Data shape:", data.shape)

# Assign target and features
target = data[:, 4]
features = data[:, [0, 2, 3]]  # Exclude 'x' to focus on 'theta'

print("Features shape:", features.shape)
print("Target shape:", target.shape)

# Train the qualitative model using PADE
q_table = pade.pade(features, target, nNeighbours=10)
print("Q-table:", q_table)
q_labels = pade.create_q_labels(q_table[:, 2:3], ['gamma'])

classes, class_names = pade.enumerate_q_labels(q_labels)

# Train decision tree
classifier = tree.DecisionTreeClassifier(min_impurity_decrease=0.02)
model = classifier.fit(features, classes)

# Display feature importance
importance = model.feature_importances_
print("Feature importances:", importance)

# Plot tree
tree_rules = export_text(model, feature_names=['theta', 'dx', 'gamma'])
print(tree_rules)

tree.plot_tree(model, feature_names=['theta', 'dx', 'gamma'], class_names=class_names, filled=True)
plt.show()
