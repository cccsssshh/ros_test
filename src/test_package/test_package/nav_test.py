import rclpy as rp
from rclpy.node import Node
from rclpy.duration import Duration
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from interface_package.msg import Navfeedback, Navgoal
from tf_transformations import euler_from_quaternion, quaternion_from_euler


class AmclClient(BasicNavigator):
    def __init__(self):
        super().__init__("nav_client")
        

        self.waitUntilNav2Active()
        
        # self.pose_sub = self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self.amcl_callback, 10)
        self.goal_sub = self.create_subscription(Navgoal, "nav_goal", self.nav_goal_callback, 10)
        self.feedback_pub = self.create_publisher(Navfeedback, "nav_feedback", 10)

    # def amcl_callback(self, msg):
    #     # AMCL Pose 정보를 처리하는 콜백
    #     pass

    def nav_goal_callback(self, msg):
        x = msg.x
        y = msg.y
        z = msg.z

        self.get_logger().info(f"Received goal: x: {x}, y: {y}, z: {z}")
        self.send_goal(x, y, z)

    def send_goal(self, x, y, z):
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.position.z = z
        goal_pose.pose.orientation.x = 0.0
        goal_pose.pose.orientation.y = 0.0
        goal_pose.pose.orientation.z = 1.0
        goal_pose.pose.orientation.w = 1.0

        self.goToPose(goal_pose)
        self.get_logger().info(f"Goal sent to navigator: x: {x}, y: {y}, z: {z}")

        i = 0
        while not self.isTaskComplete():
            i = i + 1
            feedback = self.getFeedback()
            if feedback and i % 5 == 0:
                self.get_logger().info('Distance remaining: ' + '{:.2f}'.format(feedback.distance_remaining) + ' meters.')
                msg = Navfeedback()
                msg.distance_remaining = round(feedback.distance_remaining, 2)
                self.feedback_pub.publish(msg)
                # Some navigation timeout to demo cancellation
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds=50.0):
                    self.cancelTask()
        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')

class PoseSub(Node):
    def __init__(self):
        super().__init__("pose_sub")

        self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self.amcl_pose_callback, 10)
        self.amcl_pose = PoseWithCovarianceStamped()

    def amcl_pose_callback(self, msg):
        self.amcl_pose.pose.pose.position.x = msg.pose.pose.position.x
        self.amcl_pose.pose.pose.position.y = msg.pose.pose.position.y
        self.amcl_pose.pose.pose.position.z = msg.pose.pose.position.z
        self.amcl_pose.pose.pose.orientation.x = msg.pose.pose.orientation.x
        self.amcl_pose.pose.pose.orientation.y = msg.pose.pose.orientation.y
        self.amcl_pose.pose.pose.orientation.z = msg.pose.pose.orientation.z
        self.amcl_pose.pose.pose.orientation.w = msg.pose.pose.orientation.w

        pose_info = (
            f"Position - x: {self.amcl_pose.pose.pose.position.x}, "
            f"y: {self.amcl_pose.pose.pose.position.y}, "
            f"z: {self.amcl_pose.pose.pose.position.z}\n"
            f"Orientation - x: {self.amcl_pose.pose.pose.orientation.x}, "
            f"y: {self.amcl_pose.pose.pose.orientation.y}, "
            f"z: {self.amcl_pose.pose.pose.orientation.z}, "
            f"w: {self.amcl_pose.pose.pose.orientation.w}"
        )

        self.get_logger().info(pose_info)


def main(args=None):
    rp.init(args=args)
    # node = AmclClient()
    node = PoseSub()
    rp.spin(node)
    node.destroy_node()
    rp.shutdown()

if __name__ == "__main__":
    main()


