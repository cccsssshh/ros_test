import rclpy as rp
from rclpy.node import Node
from test_package_msgs.msg import Navfeedback, Navgoal, Navresult


class RobotControl(Node):

    def __init__(self):
        super().__init__("robot_control")

        self.goal_pub = self.create_publisher(Navgoal, "nav_goal", 10)
        # self.result_client = self.create_client(Navresult, "/nav_result")
        self.feedback_sub = self.create_subscription(Navfeedback,
                                                     "nav_feedback",
                                                     self.nav_feedback_callback,
                                                     10)
        self.goal_msg = Navgoal()



    def nav_feedback_callback(self, msg):
        self.get_logger().info(f"Distance remaining: {msg.distance_remaining}")

    def send_nav_goal(self, x, y, z):
        self.goal_msg.x = x
        self.goal_msg.y = y
        self.goal_msg.z = z
        self.get_logger().info(f"Sending goal: x={x}, y={y}, z={z}")
        self.goal_pub.publish(self.goal_msg)
    


def main(args=None):
    rp.init(args=args)
    node = RobotControl()
    x = float(input("Enter the x coordinate: "))
    y = float(input("Enter the y coordinate: "))
    z = float(input("Enter the z coordinate: "))

    node.send_nav_goal(x, y, z)
    rp.spin(node)
    node.destroy_node()
    rp.shutdown()

if __name__ == "__main__":
    main()
