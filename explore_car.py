import numpy as np

from parking_simulator import ParkingSimulator

# Repeat with different initial theta to cover all the space for theta in [-180, 180].
#initial_theta = 180
initial_thetas = [-90, 0, 90, 180]

# Define the number of samples you want for each theta value
samples_per_theta = 180  # For a total of 900 samples
total_samples = samples_per_theta * len(initial_thetas)

data = np.zeros((total_samples, 5))  # To store (theta, alpha, dx, dy, dtheta)

# Loop through each initial theta value and collect samples
current_sample_index = 0

for initial_theta in initial_thetas:
    parking = ParkingSimulator(
        initial_state=(640, 300, initial_theta),
        goal_state=(640, 300, 0),
        goal_tolerance=(10, 10, 5),
        visualize=False,  # Set to False to run as console application (maximum speed, Pygame not used).
        fps=50,  # Frames per second. The time to render one frame is fixed by this parameter.
        window_size=(1280, 720),  # Set custom window size.
        use_dqn_image=False  # For each frame construct a small 84x84 monochrome image to be used with DQN.
    )

    (x, y, theta, v, alpha) = (0, 0, 0, 0, 0)
    parking.reset()

    direction = 1
    steering = 1

    i = 0
    while parking.run() and i<samples_per_theta:
        (x0, y0, theta0, v0, alpha0) = (x, y, theta, v, alpha)
        (x, y, theta, v, alpha) = parking.get_state(egocentric=False)

        if i > 0:
            dx = x - x0
            dy = y - y0
            dtheta = theta - theta0

            # Be careful with transitions between -180 and 180.
            if dtheta > 180:
                dtheta -= 360
            elif dtheta < -180:
                dtheta += 360

            # For Pade, theta will determine operating regions.
            # Citical points should be at theta = -90, 0, 90, 180.
            print(theta, theta, x, dx, v)
            #data[i, :] = [theta, alpha, x, dx, y, dy, dtheta]
            gamma = alpha + theta
            data[i, :] = [theta, x, dx, gamma, v]
            # data[i, :] = [theta, y, dy, gamma, v]
            # data[i, :] = [theta, dtheta, alpha, v]

        # Execute an action
        if abs(alpha) >= 30:
            steering *= -1  # Change steering direction
        parking.execute_action((direction, steering))

        i += 1
        if current_sample_index >= total_samples:
            parking.stop()  # Stops the simulation. The run() function will return False in the next iteration.

# Save data to CSV
np.savetxt('car_samples.csv', data, delimiter=',')

print("Data collection complete.")