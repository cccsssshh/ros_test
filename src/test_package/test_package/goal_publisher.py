import rclpy
from rclpy.node import Node
from example_interfaces.msg import Float32MultiArray
import time

class GoalPublisher(Node):

    def __init__(self):
        super().__init__('goal_publisher')
        self.publisher_ = self.create_publisher(Float32MultiArray, 'goal', 10)
        timer_period = 10.0  # 퍼블리시 주기 (초)
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Float32MultiArray()
        # 예제 데이터 설정
        msg.data = [1.0, 0.5, 5.0]  # linear_x, angular_z, dist
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = GoalPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
