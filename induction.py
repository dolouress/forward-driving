import random
import numpy as np
from sklearn import tree
import matplotlib.pyplot as plt
from parking_simulator import ParkingSimulator
import pade

def get_sample(theta, alpha, v):
    parking = ParkingSimulator(
        initial_state=(0, 0, theta),
        goal_state=(0, 0, 0),
        goal_tolerance=(0, 0, 0),
        visualize=False,
        fps=50,
        window_size=(1280, 720),
        use_dqn_image=False
    )

    parking._car._alpha = alpha
    parking._car._v = v
    parking.run(frames=50)

    (x, y, a, v, w) = parking.get_state()

    dtheta = a - theta
    if dtheta > 180:
        dtheta -= 360
    if dtheta < -180:
        dtheta += 360

    parking.reset()
    return (x, y, dtheta)

data = []
for _ in range(1000):
    theta = random.uniform(-180, 180)
    alpha = random.uniform(-30, 30)
    v = 50

    gamma = theta + alpha
    if gamma > 180:
        gamma -= 360
    if gamma < -180:
        gamma += 360

    (dx, dy, dtheta) = get_sample(theta, alpha, v)
    data.append([theta, alpha, gamma, v, dx, dy, dtheta])

data = np.array(data)

# Compute Pade values.
#q_table = pade.pade(data[:,[0,1]], data[:,6]) # dtheta
q_table = pade.pade(data[:,[0,2]], data[:,4]) # dx
#q_table = pade.pade(data[:,[0,2]], data[:,5]) # dy

# Translate Pade values to readable Q-labels.
q_labels = pade.create_q_labels(q_table[:, [1]], ['alpha'])

# Enumerate Q-labels so they can be used with scikit-learn.
classes, class_names = pade.enumerate_q_labels(q_labels)

# Build a qualitative model in the form of a decision tree.
classifier = tree.DecisionTreeClassifier(min_impurity_decrease=0.1)
model = classifier.fit(data[:, [0, 2]], classes)

# Visualize the learned model.
tree.plot_tree(model, feature_names=['theta', 'theta+alpha'], class_names=class_names, filled=True)
plt.show()

# Plotting without a colormap using different markers
markers = {0: 's', 1: 'o', 2: 'D', 3: '^'}  # Define markers for different classes
for class_label in np.unique(classes):
    plt.scatter(
        x=data[classes == class_label, 0],
        y=data[classes == class_label, 1],
        marker=markers[class_label],
        label=f"Class {'1' if class_label == 0 else '-1'}"
    )

plt.title('Samples')
plt.xlabel('theta')
plt.ylabel('alpha')
plt.legend()
plt.show()
