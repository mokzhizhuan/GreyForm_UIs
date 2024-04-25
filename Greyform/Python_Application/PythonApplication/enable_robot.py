"""import rclpy
from rclpy.action import ActionServer
from my_package.action import MoveCamera
import geometry_msgs.msg as geometry_msgs"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# enable the robot bim interpretor, will implement later. Need to research
class EnableRobotInterpreter(object):
    """def __init__(self):
            rclpy.init(args=args)
            move_camera_server = MoveCameraServer()
            rclpy.spin(move_camera_server.node)
            move_camera_server.node.destroy_node()
            rclpy.shutdown()

    class MoveCameraServer:
        def __init__(self):
            self.node = rclpy.create_node('move_camera_server')
            self.action_server = ActionServer(self.node, MoveCamera, 'move_camera', self.execute_callback)
            self.progress = 0.0

        def execute_callback(self, goal_handle):
            # Simulate camera movement
            while self.progress < 1.0:
                # Update camera position
                # Publish feedback
                feedback_msg = MoveCamera.Feedback()
                feedback_msg.progress = self.progress
                goal_handle.publish_feedback(feedback_msg)
                self.progress += 0.1  # Example progress increment
                self.node.get_logger().info('Moving camera, progress: %.2f', self.progress)
                self.node.sleep(1)  # Simulate processing time

            # Set result
            result = MoveCamera.Result()
            result.success = True
            goal_handle.succeed(result)"""
