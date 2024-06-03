import rclpy as rp
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped

class AmclSub(Node):
    def __init__(self):
        super().__init__("amcl_sub_node")

        self.amcl_sub = self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info(f'Received pose: {msg.pose.pose.position.x}, {msg.pose.pose.position.y}, {msg.pose.pose.position.z}')



def main(args=None):
    rp.init(args=args)
    node = AmclSub()
    rp.spin(node)
    node.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()