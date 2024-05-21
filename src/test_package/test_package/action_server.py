import rclpy
from rclpy.action import ActionServer, ActionClient
from rclpy.node import Node

from test_package_msgs.action import Fibonacci

class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__("fibonacci_action_server")

        self._action_server = ActionServer(
            self,
            Fibonacci,
            "fibonacci",
            self.execute_callback
        )

        # self.create_publisher()

    def execute_callback(self, goal_handle):
        self.get_logger().info("Executing goal...")

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = []

        sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()
            
            sequence.append(sequence[-1] + sequence[-2])
            feedback_msg.partial_sequence = sequence
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info('Publishing feedback: {0}'.format(sequence))

        goal_handle.succeed()
        result= Fibonacci.Result()
        result.sequence = sequence
        return result

class MiddleServer(Node):
    def __init__(self):
        super().__init__("middle_of_server_and_bridge")
    

def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()