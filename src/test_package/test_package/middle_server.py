import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse
from example_interfaces.action import Fibonacci
from example_interfaces.msg import Int32

class MiddleServer(Node):

    def __init__(self):
        super().__init__('middle_of_client_and_bridge')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback
        )
        # Publisher 생성
        self.goal_publisher = self.create_publisher(Int32, 'fibonacci_goal', 10)

    def goal_callback(self, goal_request):
        self.get_logger().info('Received goal request with order %d' % goal_request.order)
        # Goal을 퍼블리시
        goal_msg = Int32()
        goal_msg.data = goal_request.order
        self.goal_publisher.publish(goal_msg)
        self.get_logger().info('Published goal: %d' % goal_request.order)
        return GoalResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        feedback_msg = Fibonacci.Feedback()
        feedback_msg.partial_sequence = [0, 1]

        for i in range(2, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.partial_sequence.append(feedback_msg.partial_sequence[-1] + feedback_msg.partial_sequence[-2])
            self.get_logger().info('Publishing feedback: %s' % str(feedback_msg.partial_sequence))
            goal_handle.publish_feedback(feedback_msg)
            self.get_clock().sleep_for(rclpy.duration.Duration(seconds=1))

        goal_handle.succeed()

        result = Fibonacci.Result()
        result.sequence = feedback_msg.partial_sequence
        self.get_logger().info('Goal succeeded with result: %s' % str(result.sequence))
        return result

def main(args=None):
    rclpy.init(args=args)
    node = MiddleServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
