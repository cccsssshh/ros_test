import rclpy as rp
import numpy as np

from rclpy.duration import Duration
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from tf_transformations import euler_from_quaternion, quaternion_from_euler
from test_package_msgs.srv import Navgoal, Navresult
from test_package_msgs.msg import Navfeedback



class AmclClient(BasicNavigator):
    def __init__(self):
        super().__init__("amcl_server")
        
        self.waitUntilNav2Active()
        
        self.pose_sub = self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self.amcl_callback, 10)
        
        self.goal_service = self.create_service(Navgoal, "/nav_goal", self.nav_goal_callback)
        self.result_service = self.create_service(Navresult, "/nav_result", self.nav_result.callback)
        self.feedback_pub= self.create_publisher(Navfeedback, "/nav_feedback", 10)

    def nav_goal_callback(self, request, response):
        x = request.x
        y = request.y
        z = request.z 
        self.send_goal(x, y, z)

        response.sucess = True
        
        return response

    def send_goal(self, x, y, z):
        target =  quaternion_from_euler(x, y, z)
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.orientation.x = target[0]
        goal_pose.pose.orientation.y = target[1]
        goal_pose.pose.orientation.z = target[2]
        goal_pose.pose.orientation.w = target[3]

        self.goToPose(goal_pose)

        i = 0
        while not self.isTaskComplete():
            i= i + 1
            feedback = self.getFeedback()
            self.get_logger().info(f"Distance remaining : {feedback.distance_remaining:.2f}")
            msg = Navfeedback()
            msg.distance_remaining = round(feedback.distance_remaining, 2)
            self.feedback_pub.publish(msg)

            #Some navigation timeout to demo cancellation
            if Duration.from_msg(feedback.navigation_time) > Duration(seconds= 10.0):
                self.cancelTask()

    # def amcl_callback(self, msg):
    #     self.get_logger().info('Received pose: Position (%f, %f, %f)' % (
    #         msg.pose.pose.position.x,
    #         msg.pose.pose.position.y,
    #         msg.pose.pose.position.z))
    #     pose__current = msg
    #     q =[0, 0, 0, 0]
    #     q[0] = pose__current.pose.pose.orientation.x
    #     q[1] = pose__current.pose.pose.orientation.y
    #     q[2] = pose__current.pose.pose.orientation.z
    #     q[3] = pose__current.pose.pose.orientation.w
        
    #     self.convert_degree(euler_from_quaternion(q))



    # def convert_degree(self, input):
    #     return np.array(input) * 180. / np.pi
    

def main(args = None):
    rp.init(args = args)
    nav = AmclClient()

    rp.spin(nav)
    
    nav.destroy_node()

    rp.shutdown()

if __name__ == "__main__":
    main()