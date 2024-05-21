import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int32

class GoalSubscriber(Node):

    def __init__(self):
        super().__init__('goal_subscriber')
        self.subscription = self.create_subscription(
            Int32,
            'fibonacci_goal',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('Received goal: %d' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    goal_subscriber = GoalSubscriber()
    rclpy.spin(goal_subscriber)
    goal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
