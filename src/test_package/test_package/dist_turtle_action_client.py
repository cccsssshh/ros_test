import rclpy as rp
from rclpy.node import Node
from rclpy.action import ActionClient
from example_interfaces.msg import Float32MultiArray, Float32
from my_first_package_msgs.action import DistTurtle

import sys

class DistTurtleClient(Node):

    def __init__(self):
        super().__init__("dist_turtle_action_client")

        self._action_client = ActionClient(self, DistTurtle, "dist_turtle")
        self.goal_sub = self.create_subscription(
            Float32MultiArray,
            "goal",
            self.listener_callback,
            10)

        self.feedback_pub = self.create_publisher(Float32 ,"/turtle1/rotate_absolute/_action/feedback", 10)
        self.result_pub = self.create_publisher(Float32MultiArray,"/result", 10)


    def listener_callback(self, msg):
        self.get_logger().info(f'Received goal: linear_x={msg.data[0]}, angular_z={msg.data[1]}, dist={msg.data[2]}')
        self.send_goal(msg.data[0], msg.data[1], msg.data[2])


    def send_goal(self, linear_x, angular_z, dist):
        self.get_logger().info("waiting for action server...")

        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Action server not available after waiting')
            return

        goal_msg = DistTurtle.Goal()
        goal_msg.linear_x = linear_x
        goal_msg.angular_z = angular_z
        goal_msg.dist = dist

        self.get_logger().info(f'Sending goal request: linear_x={linear_x}, angular_z={angular_z}, dist={dist}')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg,feedback_callback= self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().info('Goal rejected :(')
                return
            
            self.get_logger().info('Goal accepted :)')
            self._get_result_future = goal_handle.get_result_async()
            self._get_result_future.add_done_callback(self.get_result_callback)
        except Exception as e:
            self.get_logger().error(f'Exception in goal_response_callback: {e}')

    def feedback_callback(self, feedback_msg):
        # self.get_logger().info(f'Received feedback: {feedback_msg.feedback.remained_dist}')
        msg = Float32()
        msg.data = feedback_msg.feedback.remained_dist
        self.feedback_pub.publish(msg)


    def get_result_callback(self, future):
        try:
            result = future.result().result
            # self.get_logger().info(f'Result: pos_x={result.pos_x}, pos_y={result.pos_y}, pos_theta={result.pos_theta}, result_dist={result.result_dist}')
            msg = Float32MultiArray()
            msg.data = [result.pos_x, result.pos_y, result.pos_theta, result.result_dist]
            self.result_pub.publish(msg)
        except Exception as e:
            self.get_logger().error(f'Exception in get_result_callback: {e}')



def main(args=None):
    rp.init(args=args)
    client = DistTurtleClient()

    rp.spin(client)

    client.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()