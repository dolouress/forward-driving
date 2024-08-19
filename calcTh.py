import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# Define the symbols
alpha, v, l = sp.symbols('alpha v l')

# Given equation for theta
theta = (v * sp.sin(alpha)) / (l / 2)

# Partial derivative of theta with respect to alpha
theta_deriv = sp.diff(theta, alpha)

# Substitute l = 1
theta_deriv = theta_deriv.subs(l, 1)

# Substitute a value for v (e.g., v = 0.5)
theta_deriv = theta_deriv.subs(v, 0.5)

# Convert the symbolic expression to a numerical function
theta_deriv_func = sp.lambdify(alpha, theta_deriv, "numpy")

# Define a range of alpha values in degrees, then convert to radians
alpha_vals_deg = np.linspace(-180, 180, 400)
alpha_vals_rad = np.deg2rad(alpha_vals_deg)

# Evaluate the derivative over this range
theta_deriv_vals = theta_deriv_func(alpha_vals_rad)

# Ensure that the values are positive to reflect Q+ behavior
theta_deriv_vals = np.abs(theta_deriv_vals)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(alpha_vals_deg, theta_deriv_vals, color='blue', label=r'$\frac{\partial \dot{\theta}}{\partial \alpha}$')
plt.axhline(0, color='black', linewidth=0.9)

# Highlighting the regions where Q+ applies
plt.fill_between(alpha_vals_deg, theta_deriv_vals, 0, where=(alpha_vals_deg >= -180) & (alpha_vals_deg <= 180),
                 color='lightgreen', alpha=0.3, label=r'$Q^+(\alpha)$')

# Custom x-axis ticks at 0, ±90, ±180 degrees
plt.xticks([-180, -90, 0, 90, 180], [r'$-180^\circ$', r'$-90^\circ$', r'$0^\circ$', r'$90^\circ$', r'$180^\circ$'])

# Custom y-axis ticks focusing on the positive derivative behavior
#plt.yticks([0.5, 1.0], [r'$Q^+(\alpha)$', r'$Q^+(\alpha)$'])

plt.xlabel(r'$\alpha$ (degrees)')
plt.ylabel(r'$\frac{\partial \dot{\theta}}{\partial \alpha}$')
plt.axvline(-90, color='red', linestyle='--')
plt.axvline(90, color='red', linestyle='--')

plt.legend()
plt.grid(True)
plt.show()
