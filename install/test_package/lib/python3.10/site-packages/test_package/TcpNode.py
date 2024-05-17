import rclpy as rp
from rclpy.qos import QoSProfile
from rclpy.node import Node
from std_msgs.msg import String

from test_package_msg.srv import Tcp

class TcpNode(Node):
    def __init__(self):
        super().__init__('tcp_node')

        qos_profile = QoSProfile(depth=10)
        self.tcp_publisher = self.create_client(String, '/t', qos_profile)
        self.timer = self.create_timer(1.0, self.tcp_publish)

        self.data = None

    def tcp_client(self):
        if self.data is not None:
            msg = String()
            msg.data = self.data  # 데이터가 문자열인지 확인하고 변환
            self.tcp_publisher.publish(msg)
            self.get_logger().info(f"Published message: {self.data}")
            # self.data = None  # 데이터가 한 번 발행된 후 초기화

    def set_data(self, data):
        self.data = data
        self.get_logger().info(f"received data : {data}")
        


def main(args=None):
    rp.init(args=args)
    node = TcpNode()

    rp.spin(node)
    rp.shutdown()

if __name__ == "__main__":
    main()
