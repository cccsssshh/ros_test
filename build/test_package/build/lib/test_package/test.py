#!/usr/bin/env python3
import rclpy as rp
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf_transformations import euler_from_quaternion, quaternion_from_euler
from nav2_simple_commander.robot_navigator import TaskResult
from rclpy.duration import Duration
import numpy as np


class TestNode(Node):
    def __init__(self):
        super().__init__("test_node")
        self.subscription = self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.callback, 10)
        self.subscription

        self.nav = BasicNavigator()
        self.nav.waitUntilNav2Active()
        self.goal_pose = PoseStamped()
        self.pose_current = PoseWithCovarianceStamped()

    def callback(self, data):
        self.get_logger().info(f"Current Pose: {data.pose.pose}")
        self.pose_current = data


    def set_goal(self, x, y):
        """Set goal pose in the map frame."""
        self.goal_pose.header.frame_id = 'map'
        self.goal_pose.header.stamp = self.get_clock().now().to_msg()
        self.goal_pose.pose.position.x = x
        self.goal_pose.pose.position.y = y
        self.goal_pose.pose.orientation.x = 0.0
        self.goal_pose.pose.orientation.y = 0.0
        self.goal_pose.pose.orientation.z = 0.0
        self.goal_pose.pose.orientation.w = 1.0
        self.nav.goToPose(self.goal_pose)

        i = 0
        while not self.nav.isTaskComplete():
            i += 1
            feedback = self.nav.getFeedback()
            if feedback and i % 5 == 0:
                position = self.pose_current.pose.pose.position
                log_message = f"Position: x={position.x}, y={position.y}, z={position.z}"
                self.get_logger().info(log_message)
                self.get_logger().info("Distance remaining : " "{:.2f}".format(feedback.distance_remaining) + "meters.")
            
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds = 10.0):
                    self.nav.cancelTask()

        result = self.nav.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Goal succeeded!")
        elif result == TaskResult.CANCELED:
            self.get_logger().info("Goal was canceled!")
        elif result == TaskResult.FAILED:
            self.get_logger().info("Goal failed!")

def main(args=None):
    rp.init(args=args)
    node = TestNode()
    try:
        while rp.ok():
            x = float(input("Enter goal x: "))
            y = float(input("Enter goal y: "))
            node.set_goal(x, y)
            rp.spin_once(node, timeout_sec=1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rp.shutdown()

if __name__ == "__main__":
    main()