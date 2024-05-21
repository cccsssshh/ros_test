import rclpy as rp
from rclpy.node import Node

from test_package_msgs.srv import Navgoal, Navresult
from test_package_msgs.msg import Navfeedback


class MiddleNode(Node):

    def __init__(self):
        super().__init__("middle_node")

        self.goal_client = self.create_client(Navgoal, "/nav_goal")
        self.result_client = self.create_client(Navresult, "/nav_result")
        self.feedback_sub= self.create_subscription(Navfeedback, 
                                                    "/nav_feedback", 
                                                    self.nav_feedback_callback, 
                                                    10)

        self.goal_req = Navgoal.Request()    

    def nav_feedback_callback(self, msg):
        self.get_logger().info(f"distance remaining : {msg.distance_remaining}")

    def send_nav_goal(self, x, y, z):
        self.goal_req.x = x
        self.goal_req.y = y
        self.goal_req.z = z
        self.future = self.goal_client.call_async(self.goal_req)
        self.future.add_done_callback(self.nav_goal_response_callback)

    def nav_goal_response_callback(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info()("Goal successfully sent.")
            else:
                self.get_logger().info("Failed to send goal.")
        except Exception as e:
            self.get_logger().info(f"Service call failed: {e}")

        



def main(args = None):
    rp.init(args = args)
    node = MiddleNode()

    rp.spin(node)
    
    node.destroy_node()

    rp.shutdown()

if __name__ == "__main__":
    main()