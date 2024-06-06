import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enum import Enum
import rclpy as rp
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import Int16
from std_srvs.srv import Trigger
from interface_package.srv import Module, LocationInfo, NodeNum
from rclpy.executors import MultiThreadedExecutor
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Twist
from rclpy.duration import Duration
from tf_transformations import quaternion_from_euler, euler_from_quaternion

import math
from time import sleep
# import pathDict

# ROBOT_NUMBER = "1"
# ROBOT_NUMBER = "2"
ROBOT_NUMBER = "3"

class RobotStatus(Enum):
    HOME = 0  # waiting at Home
    TO_STORE = 1  # moving to Store
    AT_STORE = 2  # arrived at Store
    TO_KIOSK = 3  # moving to Kiosk
    AT_KIOSK = 4  # arrived at Kiosk
    RETURNING = 5  # returning to Home
    AT_HOME = 6  # Arrived at Home

class OrderStatus(Enum):
    DELIVERY_YET = "DY"
    DELIVERY_READY = "DR"  # Not used yet
    DELIVERY_START = "DS"
    DELIVERY_FINISH = "DF"


class DrobotMotor(Node):
    def __init__(self):
        super().__init__("drobot_motor")

        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        self.nav = BasicNavigator()
        # self.nav.waitUntilNav2Active()

        self.is_active = False
        self.store_id = ""
        self.kiosk_id = ""
        self.status = RobotStatus.HOME
        
        self.set_parameters()
        
        self.status_change = {
            RobotStatus.HOME: RobotStatus.TO_STORE,
            RobotStatus.TO_STORE: RobotStatus.AT_STORE,
            RobotStatus.AT_STORE: RobotStatus.TO_KIOSK,
            RobotStatus.TO_KIOSK: RobotStatus.AT_KIOSK,
            RobotStatus.AT_KIOSK: RobotStatus.RETURNING,
            RobotStatus.RETURNING: RobotStatus.AT_HOME,
            # RobotStatus.AT_HOME: RobotStatus.HOME
        }

        self.current_point = 0
        self.next_point = 0
        self.store_points = []
        self.kiosk_points = []

        self.position = None
        self.orientation = None
        self.diff_dist = 0.0

        self.short_goal_server = self.create_service(NodeNum, "shortGoal", self.short_goal_callback)
        self.robot_arrival_client = self.create_client(NodeNum, "robotArrival")

        self.module_client = self.create_client(Module, "module")

        self.cmd_vel_pub = self.create_publisher(Twist, "/base_controller/cmd_vel_unstamped", 10)
        self.reset_sub = self.create_service(Trigger, "/reset", self.reset_callback)
        
        self.get_logger().info(f"R-{ROBOT_NUMBER} motor start")
    
    def set_parameters(self):
        #waypoints : 0 ~ 27
        #robot_points : 28 ~30
        #store_points : 31 ~ 34
        #kiosk_points : 35 ~ 38
        parameters = [
            ("robot1", [-0.1, 2.5, 0.0]),
            ("robot2", [-0.1, 1.5, 0.0]),
            ("robot3", [-0.1, 0.3, 0.0]),
            ("store11", [1.7, 2.8, 160.0]),
            ("store12", [1.7, 1.7, 160.0]),
            ("store21", [1.7, 1.3, 160.0]),
            ("store22", [1.7, 0.3, 160.0]),
            ("kiosk11", [0.3, 3.2, 80.0]),
            ("kiosk12", [1.15, 2.8, 80.0]),
            ("kiosk21", [1.15, 0.5, -80.0]),
            ("kiosk22", [0.3, 0.5, -80.0]),
        ]
        for i in range(1, 8):
            for j in range(1, 5):
                parameters.append((f"way{i}{j}", [0.0, 0.0, 0.0]))

        self.declare_parameters(namespace="", parameters=parameters)

        # Get parameters
        self.robot_positions = [(name, self.get_parameter(name).value) for name in ["robot1", "robot2", "robot3"]]
        self.store_positions = [(name, self.get_parameter(name).value) for name in ["store11", "store12", "store21", "store22"]]
        self.kiosk_positions = [(name, self.get_parameter(name).value) for name in ["kiosk11", "kiosk12", "kiosk21", "kiosk22"]]
        
        self.waypoints = [
            (f"way{i}{j}", self.get_parameter(f"way{i}{j}").value) 
            for i in range(1, 8) 
            for j in range(1, 5)
        ]

        self.all_positions = self.waypoints + self.robot_positions + self.store_positions + self.kiosk_positions
        # self.print_all_positions(self.all_positions)

    # def print_all_positions(self, positons):
    #     for name, pos in positons:
    #         self.get_logger().info(f"Parameter {name}: x = {pos[0]}, y = {pos[1]}, theta = {pos[2]}")

    def get_indices_from_id(self, id):
        id_to_indices = {
            "S-1": [31, 32],
            "S-2": [33, 34],
            "K-1": [35, 36],
            "K-2": [37, 38]
        }
        return id_to_indices.get(id, [])

    def update_status(self):
        self.get_logger().info(f"Updating status from {self.status.name}")
        
        self.status = self.status_change[self.status]
        self.get_logger().info(f"Status updated to {self.status.name}")

        if self.status == RobotStatus.RETURNING:
            self.returning()
            self.get_logger().info("Returning to Home")    
        
        if self.status == RobotStatus.AT_HOME:
            self.reset()
            sleep(1)
            self.status = RobotStatus.HOME
            self.get_logger().info(f"Status updated to {self.status.name}")

    def request_robot_arrival(self, next_point):
        robot_arrival_request = NodeNum.Request()
        robot_arrival_request.nodenum = next_point
        future = self.robot_arrival_client.call_async(robot_arrival_request)
        future.add_done_callback(self.response_robot_arrival)

    def response_robot_arrival(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"response {response.success} from TM")
        except Exception as e:
            self.get_logger().error(f"arrival call failed : {e}")


    # def short_goal_callback(self, request, response):
    #     #잘못된 명령이 왔을 때 response false 보내면서 에러 보내야 한다.
    #     self.next_point =int(request.nodenum) # 0 ~ 38
    #     self.get_logger().info(f"next_position : {self.next_postitions[0]}, {self.next_postitions[1]}, status : {self.status.value}")        

    #     if self.status in [RobotStatus.HOME, RobotStatus.AT_STORE, RobotStatus.AT_KIOSK]:
    #         if 0 <= self.next_point <= 27:
    #             self.update_status()
    #         else:
    #             response.success =  False
    #     elif self.status in [RobotStatus.AT_HOME, RobotStatus. RETURNING]:
    #         if self.is_active:
    #             self.status = RobotStatus.TO_STORE
            
    #     elif self.status in [RobotStatus.TO_STORE, RobotStatus.TO_KIOSK]:
    #         pass
    #     # self.send_goal(self.next_postitions[1])
    #     self.verify_checkpoint()
    #     self.request_robot_arrival(str(self.next_point)) ### temp code

    #     # self.check_succeed(self.position)
    #     response.success = True
        
    #     return response

    def short_goal_callback(self, request, response):
        #waypoints : 0 ~ 27
        #robot_positions : 28 ~30
        #store_points : 31 ~ 34
        #kiosk_points : 35 ~ 38
        #잘못된 명령이 왔을 때 response false 보내면서 에러 보내야 한다.
        self.next_point =int(request.nodenum) # 0 ~ 38

        if 0 <= self.next_point <= 38:
            self.next_postitions = self.all_positions[self.next_point]
            self.get_logger().info(f"next_position : {self.next_postitions[0]}, {self.next_postitions[1]}, status : {self.status.value}, active :{self.is_active}") 
        else:
            self.get_logger().warn(f"Invalid point!!")
            response.success = False
            return response 

        if self.is_active:
            if self.status in [RobotStatus.HOME, RobotStatus.AT_HOME, RobotStatus.AT_STORE, RobotStatus.AT_KIOSK]:
                if 0 <= self.next_point <= 27:
                    self.update_status()
                    # self.send_goal(self.next_postitions[1])
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.next_postitions}")
                    response.success =  False
            elif self.status in [RobotStatus.TO_STORE]:
                if 0 <= self.next_point <= 27 or self.next_point in self.store_points:
                    # self.send_goal(self.next_postitions[1])
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.next_postitions}")
                    response.success =  False
            elif self.status == RobotStatus.TO_KIOSK:
                if 0 <= self.next_point <= 27 or self.next_point in self.kiosk_points:
                    # self.send_goal(self.next_postitions[1])
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.next_postitions}")
                    response.success =  False
        else:
            self.get_logger().info(f"status : {self.status}, next_point : {self.next_point}, active : {self.is_active}")
            if self.status == RobotStatus.RETURNING:
                if 0 <= self.next_point <= 27 or self.next_point == (27 + int(ROBOT_NUMBER)):
                    # self.send_goal(self.next_postitions[1])
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.next_postitions}")
                    response.success =  False
            else:
                self.get_logger().warn("There is not order!!")
                response.success =  False

        if response.success == True:
            self.request_robot_arrival(str(self.next_point)) ### temp code
            self.verify_checkpoint()

        return response

    def check_succeed(self, position):
        diff_dist, _, _ = self.calc_diff(self.next_postitions[1], position)
        if diff_dist <= 0.02:
            self.get_logger().info("moving is succeed!")
            # self.request_robot_arrival(int(ROBOT_NUMBER))
            self.verify_checkpoint()
        else:
            self.send_goal(self.current_goal)
            self.get_logger().warn("moving is failed!")


    def verify_checkpoint(self):
        if self.next_point in self.store_points and self.status == RobotStatus.TO_STORE:
            self.update_status()
            self.request_module("ST")
            self.get_logger().info(f"R-{ROBOT_NUMBER} arrived at Store. So, status updated to {self.status.value}")
        elif self.next_point in self.kiosk_points and self.status == RobotStatus.TO_KIOSK:
            self.update_status()
            self.request_module("KS")
            self.get_logger().info(f"R-{ROBOT_NUMBER} arrived at Kiosk. So, status updated to {self.status.value}")
        elif self.next_point == (27 + int(ROBOT_NUMBER)) and self.status == RobotStatus.RETURNING:
            self.update_status()
            self.get_logger().info(f"R-{ROBOT_NUMBER} arrived at Home. So, status updated to {self.status.value}")
        else:
            self.get_logger().info("On waypoints")

    def goalPose(self, p_x, p_y, degree):
        tmp = [0, 0, degree]
        orientation_val = quaternion_from_euler(tmp[0], tmp[1], tmp[2])
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = self.nav.get_clock().now().to_msg()
        goal_pose.pose.position.x = p_x
        goal_pose.pose.position.y = p_y
        goal_pose.pose.position.z = 0.0
        goal_pose.pose.orientation.x = 0.0
        goal_pose.pose.orientation.y = 0.0
        goal_pose.pose.orientation.z = orientation_val[2]
        goal_pose.pose.orientation.w = orientation_val[3]

        return goal_pose

    def send_goal(self, goal):
        x = goal[0]
        y = goal[1]
        degree = goal[2]
        gp = self.goalPose(x, y, degree)
        self.nav.goToPose(gp)
        i = 0
        while not self.nav.isTaskComplete():
            # i = i + 1
            feedback = self.nav.getFeedback()
            if feedback and i % 5 == 0:
                print("Distance remaining: " + "{:.2f}".format(feedback.distance_remaining) + " meters.")
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds=10.0):
                    self.nav.cancelTask()
        result = self.nav.getResult()

        if result == TaskResult.SUCCEEDED:
            print("Goal succeeded!")
        elif result == TaskResult.CANCELED:
            print("Goal was canceled!")
        elif result == TaskResult.FAILED:
            print("Goal failed!")


    # def angle_command(self, diff_angle, goal_yaw):
    #     msg = Twist()
    #     msg.

    # def go_command(self, diff_x, diff_y):


    def calc_diff(self, goal, current):
        goal_x = goal[0]
        goal_y = goal[1]
        goal_yaw = goal[2]
        current_x = current.x
        current_y = current.y
        current_yaw = current.yaw
        self.diff_x = goal_x - current_x
        self.diff_y = goal_y - current_y
        diff_dist = math.sqrt((self.diff_x) ** 2 + (self.diff_y) ** 2)

        dx = goal_x - current_x
        dy = goal_y - current_y

        goal_angle = math.atan2(dy, dx)
        rotation_angle = goal_angle - current_yaw
        rotation_angle = (rotation_angle + math.pi) % (2 * math.pi) - math.pi

        return diff_dist, rotation_angle, goal_yaw
    

    def request_module(self, location):
        module_request = Module.Request()
        module_request.data = location
        future = self.module_client.call_async(module_request)
        future.add_done_callback(self.response_module)

    def response_module(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"module response : {response.success}")

        except Exception as e:
            self.get_logger().error(f"module call failed {e}")

    def reset_callback(self, request, response):
        self.reset()
        response.success = True
        response.message = "reset"

        return response
    
    def reset(self):
        self.get_logger().info("Robot reset")
        self.status = RobotStatus.HOME

        self.next_point = None
        self.current_goal = []
        self.position = None
        self.orientation = None
        self.store_points = []
        self.kiosk_points = []
        self.diff_dist = 0.0

        self.is_active = False
    
    def returning(self):
        self.get_logger().info("Robot returning")
        self.store_points = []
        self.kiosk_points = []
        self.store_id = ""
        self.kiosk_id = ""
        self.is_active = False

class DrobotStatus(Node):
    def __init__(self, motor_node):
        super().__init__("drobot_status")
        self.motor_node = motor_node
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        self.motor_order_service = self.create_service(LocationInfo, "location_info", self.motor_order_callback)

        self.timer_period = 10.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.status_pub = self.create_publisher(Int16, "/status", self.qos_profile)

    def motor_order_callback(self, request, response):
        store_id = request.store_id
        kiosk_id = request.kiosk_id

        self.get_logger().info("Get motor order request")

        self.motor_node.store_id = store_id
        self.motor_node.kiosk_id = kiosk_id
        self.motor_node.store_points = self.motor_node.get_indices_from_id(store_id)
        self.motor_node.kiosk_points = self.motor_node.get_indices_from_id(kiosk_id)
        self.motor_node.is_active = True
        if self.motor_node.status == RobotStatus.RETURNING:
            self.motor_node.status == RobotStatus.TO_STORE
        response.success = True

        return response

    def status_publish(self, status):
        msg = Int16()
        msg.data = status.value
        self.status_pub.publish(msg)
        self.get_logger().info(f"Published status: {msg.data}")

    def timer_callback(self):
        self.status_publish(self.motor_node.status)

class AmclSub(Node):
    def __init__(self, motor_node):
        super().__init__("amcl_sub_node")
        self.motor_node = motor_node
        self.amcl_sub = self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self.listener_callback, 10)

    def listener_callback(self, msg):
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation

        quaternion = (orientation.x, orientation.y, orientation.z, orientation.w)
        euler = euler_from_quaternion(quaternion)
        roll, pitch, yaw = euler

        self.get_logger().info(f"Received pose: position=({position.x}, {position.y}, {position.z}), orientation=(roll={roll}, pitch={pitch}, yaw={yaw})")
        self.motor_node.position = position
        self.motor_node.orientation = orientation

def main(args=None):
    rp.init(args=args)
    executor = MultiThreadedExecutor()

    drobot_motor = DrobotMotor()
    drobot_status = DrobotStatus(motor_node= drobot_motor)
    amcl_sub = AmclSub(motor_node= drobot_motor)

    executor.add_node(drobot_motor)
    executor.add_node(drobot_status)
    executor.add_node(amcl_sub)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        if rp.ok():
            executor.shutdown()
            drobot_motor.destroy_node()
            drobot_status.destroy_node()
            amcl_sub.destroy_node()
            rp.shutdown()


if __name__ == "__main__":
    main()


