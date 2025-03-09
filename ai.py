import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, pi

class Robot2D:
    def __init__(self):
        # Robot physical parameters
        self.wheel_radius = 0.05  # meters
        self.wheel_base_width = 0.2  # meters (distance between left and right wheels)
        self.wheel_base_length = 0.2  # meters (distance between front and back wheels)
        
        # Encoder resolution (ticks per full wheel rotation)
        self.encoder_resolution = 1024
        
        # Initial state
        self.true_x = 0.0
        self.true_y = 0.0
        self.true_theta = 0.0  # radians
        
        # Estimated state
        self.est_x = 0.0
        self.est_y = 0.0
        self.est_theta = 0.0
        
        # Previous encoder values for each wheel
        self.prev_encoder_values = [0, 0, 0, 0]
        
        # Noise parameters
        self.slip_factor = 0.02  # Wheel slip factor
        self.encoder_noise_std = 1  # Standard deviation of encoder noise (in ticks)
        
        # Movement state
        self.is_moving = False
        self.is_rotating = False
        
        # History for plotting
        self.true_path = []
        self.estimated_path = []
    
    def measure_encoder(self, wheel_idx, quadrature=False):
        """
        Simulates reading from a wheel encoder
        
        Args:
            wheel_idx (int): Index of the wheel (0=top left, 1=top right, 2=bottom left, 3=bottom right)
            quadrature (bool): If True, returns the value from the second sensor in quadrature
        
        Returns:
            int: Encoder tick value
        """
        # In a real robot, this would read actual encoder values
        # For simulation, we calculate expected encoder values based on the true position
        
        # Calculate expected encoder ticks (with noise and slip)
        expected_ticks = self._calculate_expected_ticks(wheel_idx)
        
        # Add some noise to the encoder reading
        noise = np.random.normal(0, self.encoder_noise_std)
        encoder_value = int(expected_ticks + noise)
        
        # If quadrature is requested, offset by 1/4 of a cycle
        if quadrature:
            phase_offset = self.encoder_resolution / 4
            encoder_value = int((expected_ticks + phase_offset + noise) % self.encoder_resolution)
        
        return encoder_value
    
    def _calculate_expected_ticks(self, wheel_idx):
        """Calculate expected encoder ticks based on true position (for simulation)"""
        # This is just for simulation - in reality, encoders would provide actual readings
        if self.is_moving:
            # When moving forward, all wheels should turn at the same rate
            # Apply different slip factors to each wheel to simulate real-world conditions
            slip = np.random.normal(1.0, self.slip_factor)
            distance_traveled = abs(self.true_x) + abs(self.true_y)  # Simplified
            wheel_rotation = distance_traveled / self.wheel_radius
            ticks = wheel_rotation * self.encoder_resolution * slip
            
        elif self.is_rotating:
            # When rotating, wheels on opposite sides turn in opposite directions
            is_left = wheel_idx == 0 or wheel_idx == 2
            direction = -1 if is_left else 1  # Left wheels go backward, right wheels go forward
            rotation_circumference = self.wheel_base_width * abs(self.true_theta)
            wheel_rotation = rotation_circumference / self.wheel_radius
            slip = np.random.normal(1.0, self.slip_factor)
            ticks = direction * wheel_rotation * self.encoder_resolution * slip
            
        else:
            # Robot is stopped
            ticks = 0
        
        return ticks
    
    def update_dead_reckoning(self):
        """
        Update the estimated position and orientation using dead reckoning
        from wheel encoder measurements.
        """
        # Get current encoder values for all wheels
        current_encoders = [self.measure_encoder(i) for i in range(4)]
        
        # Calculate encoder differences (how much each wheel has turned)
        encoder_diffs = [current - prev for current, prev in zip(current_encoders, self.prev_encoder_values)]
        
        # Store current encoder values for next update
        self.prev_encoder_values = current_encoders
        
        # Skip update if there's no significant movement
        if all(abs(diff) < 2 for diff in encoder_diffs):  # Noise threshold
            return
        
        # Determine if the robot is moving straight or rotating
        left_wheel_avg = (encoder_diffs[0] + encoder_diffs[2]) / 2
        right_wheel_avg = (encoder_diffs[1] + encoder_diffs[3]) / 2
        
        # If signs are opposite, we're rotating
        if left_wheel_avg * right_wheel_avg < 0:
            # Rotation detected
            # Convert encoder ticks to wheel rotation
            left_rotation = left_wheel_avg / self.encoder_resolution * 2 * pi
            right_rotation = right_wheel_avg / self.encoder_resolution * 2 * pi
            
            # Calculate the rotation angle
            left_arc = left_rotation * self.wheel_radius
            right_arc = right_rotation * self.wheel_radius
            theta_change = (right_arc - left_arc) / self.wheel_base_width
            
            # Update estimated orientation
            self.est_theta += theta_change
            
            # Normalize theta to [-pi, pi]
            self.est_theta = (self.est_theta + pi) % (2 * pi) - pi
            
        else:
            # Forward/backward movement detected
            # Average the encoder differences to get a more accurate estimate
            avg_ticks = sum(encoder_diffs) / 4
            
            # Convert ticks to distance
            distance = avg_ticks / self.encoder_resolution * 2 * pi * self.wheel_radius
            
            # Update position based on current orientation
            self.est_x += distance * cos(self.est_theta)
            self.est_y += distance * sin(self.est_theta)
        
        # Record estimated position for visualization
        self.estimated_path.append((self.est_x, self.est_y, self.est_theta))
    
    def simulate_move(self, distance):
        """Simulate a straight-line movement (for testing)"""
        self.is_moving = True
        self.is_rotating = False
        
        # Update true position
        self.true_x += distance * cos(self.true_theta)
        self.true_y += distance * sin(self.true_theta)
        
        # Record for visualization
        self.true_path.append((self.true_x, self.true_y, self.true_theta))
        
        # Update estimated position using dead reckoning
        self.update_dead_reckoning()
        
        self.is_moving = False
    
    def simulate_rotate(self, angle):
        """Simulate a rotation (for testing)"""
        self.is_moving = False
        self.is_rotating = True
        
        # Update true orientation
        self.true_theta += angle
        
        # Normalize theta to [-pi, pi]
        self.true_theta = (self.true_theta + pi) % (2 * pi) - pi
        
        # Record for visualization
        self.true_path.append((self.true_x, self.true_y, self.true_theta))
        
        # Update estimated position using dead reckoning
        self.update_dead_reckoning()
        
        self.is_rotating = False
    
    def visualize_paths(self):
        """Visualize the true and estimated paths"""
        if not self.true_path or not self.estimated_path:
            print("No path data to visualize")
            return
            
        true_path = np.array(self.true_path)
        est_path = np.array(self.estimated_path)
        
        plt.figure(figsize=(10, 8))
        
        # Plot true path
        plt.plot(true_path[:, 0], true_path[:, 1], 'b-', label='True Path')
        
        # Plot estimated path
        plt.plot(est_path[:, 0], est_path[:, 1], 'r--', label='Estimated Path')
        
        # Plot start and end points
        plt.plot(true_path[0, 0], true_path[0, 1], 'go', markersize=10, label='Start')
        plt.plot(true_path[-1, 0], true_path[-1, 1], 'ro', markersize=10, label='True End')
        plt.plot(est_path[-1, 0], est_path[-1, 1], 'mo', markersize=10, label='Estimated End')
        
        # Plot orientation arrows at regular intervals
        arrow_indices = np.linspace(0, len(true_path)-1, min(10, len(true_path))).astype(int)
        
        for i in arrow_indices:
            # True orientation
            plt.arrow(true_path[i, 0], true_path[i, 1], 
                      0.1*cos(true_path[i, 2]), 0.1*sin(true_path[i, 2]),
                      head_width=0.05, head_length=0.1, fc='blue', ec='blue')
            
            # Estimated orientation
            if i < len(est_path):
                plt.arrow(est_path[i, 0], est_path[i, 1], 
                          0.1*cos(est_path[i, 2]), 0.1*sin(est_path[i, 2]),
                          head_width=0.05, head_length=0.1, fc='red', ec='red')
        
        plt.grid(True)
        plt.axis('equal')
        plt.legend()
        plt.title('Robot Path: True vs Estimated (Dead Reckoning)')
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.show()

# Example usage
def test_robot_positioning():
    robot = Robot2D()
    
    # Simulate a sequence of movements
    robot.simulate_move(1.0)  # Move forward 1 meter
    robot.simulate_rotate(pi/4)  # Rotate 45 degrees
    robot.simulate_move(2.0)  # Move forward 2 meters
    robot.simulate_rotate(-pi/2)  # Rotate -90 degrees
    robot.simulate_move(1.5)  # Move forward 1.5 meters
    
    # Print final positions
    print(f"True position: ({robot.true_x:.2f}, {robot.true_y:.2f}, {robot.true_theta*180/pi:.2f}°)")
    print(f"Estimated position: ({robot.est_x:.2f}, {robot.est_y:.2f}, {robot.est_theta*180/pi:.2f}°)")
    
    # Calculate error
    pos_error = np.sqrt((robot.true_x - robot.est_x)**2 + (robot.true_y - robot.est_y)**2)
    angle_error = abs(robot.true_theta - robot.est_theta) % (2*pi)
    angle_error = min(angle_error, 2*pi - angle_error) * 180/pi  # Convert to degrees
    
    print(f"Position error: {pos_error:.2f} meters")
    print(f"Angle error: {angle_error:.2f} degrees")
    
    # Visualize the paths
    robot.visualize_paths()

if __name__ == "__main__":
    test_robot_positioning()