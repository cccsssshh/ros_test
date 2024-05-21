import rclpy
from rclpy.node import Node
from example_interfaces.msg import Float32, Float32MultiArray

class FeedbackResultSubscriber(Node):
    def __init__(self):
        super().__init__('goal_subscriber')
        self.feedback_subscription = self.create_subscription(
            Float32,
            "/turtle1/rotate_absolute/_action/feedback",
            self.feedback_callback,
            10
        )
        self.feedback_subscription  # prevent unused variable warning
        self.result_subscription = self.create_subscription(
            Float32MultiArray,
            "/result",
            self.result_callback,
            10
        )
        self.result_subscription  # prevent unused variable warning


    def feedback_callback(self, msg):
        self.get_logger().info(f"remained dist : {msg.data}")

    def result_callback(self, msg):
        self.get_logger().info(f"remained dist : {msg.data}")

        
def main(args=None):
    rclpy.init(args=args)
    subscriber = FeedbackResultSubscriber()
    rclpy.spin(subscriber)
    subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
