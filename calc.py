import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# Define the symbols
theta_alpha, v = sp.symbols('theta_alpha v')

# Given equation
x_dot = -v * sp.sin(theta_alpha)

# Partial derivative of x_dot with respect to theta_alpha
x_dot_deriv = sp.diff(x_dot, theta_alpha)

# Substitute v = 0.5
x_dot_deriv = x_dot_deriv.subs(v, 0.5)

# Convert the symbolic expression to a numerical function
x_dot_deriv_func = sp.lambdify(theta_alpha, x_dot_deriv, "numpy")

# Define a range of (theta + alpha) values in degrees, then convert to radians
theta_alpha_vals_deg = np.linspace(-180, 180, 400)
theta_alpha_vals_rad = np.deg2rad(theta_alpha_vals_deg)

# Evaluate the derivative over this range
x_dot_deriv_vals = x_dot_deriv_func(theta_alpha_vals_rad)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(theta_alpha_vals_deg, x_dot_deriv_vals, color='blue', label=r'$\frac{\partial \dot{x}}{\partial (\theta + \alpha)}$')
plt.axhline(0, color='black', linewidth=0.9)

# Highlighting the regions
plt.fill_between(theta_alpha_vals_deg, x_dot_deriv_vals, 0, where=(theta_alpha_vals_deg >= -90) & (theta_alpha_vals_deg <= 90),
                 color='lightgreen', alpha=0.3, label=r'$Q^-(\theta + \alpha)$')
plt.fill_between(theta_alpha_vals_deg, x_dot_deriv_vals, 0, where=(theta_alpha_vals_deg < -90) | (theta_alpha_vals_deg > 90),
                 color='lightcoral', alpha=0.3, label=r'$Q^+(\theta + \alpha)$')

# Custom x-axis ticks at 0, ±90, ±180 degrees
plt.xticks([-180, -90, 0, 90, 180], [r'$-180^\circ$', r'$-90^\circ$', r'$0^\circ$', r'$90^\circ$', r'$180^\circ$'])

# Custom y-axis ticks (if needed)
# plt.yticks([-0.5, 0.5], [r'$Q^-(\theta + \alpha)$', r'$Q^+(\theta + \alpha)$'])

plt.xlabel(r'$(\theta + \alpha)$ (degrees)')
plt.ylabel(r'$\frac{\partial \dot{x}}{\partial (\theta + \alpha)}$')
plt.axvline(-90, color='red', linestyle='--')
plt.axvline(90, color='red', linestyle='--')

plt.legend()
plt.grid(True)
plt.show()
