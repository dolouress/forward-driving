from parking_simulator import ParkingSimulator

# Repeat with different initial theta to cover all the space for theta in [-180, 180].
initial_theta = 180

parking = ParkingSimulator(
    initial_state = (640, 300, initial_theta),
    goal_state = (640, 300, 0),
    goal_tolerance = (10, 10, 5),
    visualize = True,              # Set to False to run as console application (maximum speed, Pygame not used).
    fps = 50,                      # Frames per second. The time to render one frame is fixed by this parameter.
    window_size = (1280, 720),     # Set custom window size.
    use_dqn_image = False          # For each frame construct a small 84x84 monochrome image to be used with DQN.
)

(x, y, theta, v, alpha) = (0, 0, 0, 0, 0)
parking.reset()

direction = 1
steering = 1

i = 0
while parking.run():
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
        print(theta, dx, dy, dtheta, alpha0)

    # Execute an action
    if abs(alpha) >= 30:
        steering *= -1 # Change steering direction
    parking.execute_action((direction, steering))
    
    i += 1
    if i >= 200:
        parking.stop() # Stops the simulation. The run() function will return False in the next iteration.