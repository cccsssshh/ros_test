import sys
import os

# 현재 디렉토리를 PYTHONPATH에 추가
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
# ROBOT_NU MBER = "2"
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

        self.current_point = []
        self.next_point = []
        self.store_point = []
        self.kiosk_point = []

        self.position = None
        self.orientation = None
        self.diff_dist = 0.0

        self.short_goal_server = self.create_service(NodeNum, "shortGoal", self.short_goal_callback)
        self.robot_arrival_client = self.create_client(NodeNum, 'robotArrival')

        self.module_client = self.create_client(Module, "module")

        self.cmd_vel_pub = self.create_publisher(Twist, "/base_controller/cmd_vel_unstamped", 10)
        self.reset_sub = self.create_service(Trigger, '/reset', self.reset_callback)
        
        self.get_logger().info(f"R-{ROBOT_NUMBER} motor start")
    
    def set_parameters(self):
        self.declare_parameters(
            namespace='',
            parameters=[
                ('robot1', [-0.1, 2.5, 0.0]),
                ('robot2', [-0.1, 1.5, 0.0]),
                ('robot3', [-0.1, 0.3, 0.0]),
                ('store11', [1.7, 2.8, 160.0]),
                ('store12', [1.7, 1.7, 160.0]),
                ('store21', [1.7, 1.3, 160.0]),
                ('store22', [1.7, 0.3, 160.0]),
                ('kiosk11', [0.3, 3.2, 80.0]),
                ('kiosk12', [1.15, 2.8, 80.0]),
                ('kiosk21', [1.15, 0.5, -80.0]),
                ('kiosk22', [0.3, 0.5, -80.0]),
                ('way11', [0.5, 2.6, 0.0]),
                ('way12', [0.5, 2.6, 80.0]),
                ('way13', [0.5, 2.6, -80.0]),
                ('way14', [0.5, 2.6, 160.0]),
                ('way21', [0.5, 1.5, 0.0]),
                ('way22', [0.5, 1.5, 80.0]),
                ('way23', [0.5, 1.5, -80.0]),
                ('way24', [0.5, 1.5, 160.0]),
                ('way31', [0.5, 0.3, 0.0]),
                ('way32', [0.5, 0.3, 80.0]),
                ('way33', [0.5, 0.3, -80.0]),
                ('way34', [0.5, 0.3, 160.0]),
                ('way41', [1.15, 0.3, 0.0]),
                ('way42', [1.15, 0.3, 80.0]),
                ('way43', [1.15, 0.3, -80.0]),
                ('way44', [1.15, 0.3, 160.0]),
                ('way51', [1.15, 1.3, 0.0]),
                ('way52', [1.15, 1.3, 80.0]),
                ('way53', [1.15, 1.3, -80.0]),
                ('way54', [1.15, 1.3, 160.0]),
                ('way61', [1.15, 1.8, 0.0]),
                ('way62', [1.15, 1.8, 80.0]),
                ('way63', [1.15, 1.8, -80.0]),
                ('way64', [1.15, 1.8, 160.0]),
                ('way71', [1.15, 2.5, 0.0]),
                ('way72', [1.15, 2.5, 80.0]),
                ('way73', [1.15, 2.5, -80.0]),
                ('way74', [1.15, 2.5, 160.0]),
            ]
        )

        # Get parameters
        self.robot1 = self.get_parameter('robot1').value
        self.robot2 = self.get_parameter('robot2').value
        self.robot3 = self.get_parameter('robot3').value

        self.store11 = self.get_parameter('store11').value
        self.store12 = self.get_parameter('store12').value
        self.store21 = self.get_parameter('store21').value
        self.store22 = self.get_parameter('store22').value

        self.kiosk11 = self.get_parameter('kiosk11').value
        self.kiosk12 = self.get_parameter('kiosk12').value
        self.kiosk21 = self.get_parameter('kiosk21').value
        self.kiosk22 = self.get_parameter('kiosk22').value

        self.way11 = self.get_parameter('way11').value
        self.way12 = self.get_parameter('way12').value
        self.way13 = self.get_parameter('way13').value
        self.way14 = self.get_parameter('way14').value
        self.way21 = self.get_parameter('way21').value
        self.way22 = self.get_parameter('way22').value
        self.way23 = self.get_parameter('way23').value
        self.way24 = self.get_parameter('way24').value
        self.way31 = self.get_parameter('way31').value
        self.way32 = self.get_parameter('way32').value
        self.way33 = self.get_parameter('way33').value
        self.way34 = self.get_parameter('way34').value
        self.way41 = self.get_parameter('way41').value
        self.way42 = self.get_parameter('way42').value
        self.way43 = self.get_parameter('way43').value
        self.way44 = self.get_parameter('way44').value
        self.way51 = self.get_parameter('way51').value
        self.way52 = self.get_parameter('way52').value
        self.way53 = self.get_parameter('way53').value
        self.way54 = self.get_parameter('way54').value
        self.way61 = self.get_parameter('way61').value
        self.way62 = self.get_parameter('way62').value
        self.way63 = self.get_parameter('way63').value
        self.way64 = self.get_parameter('way64').value
        self.way71 = self.get_parameter('way71').value
        self.way72 = self.get_parameter('way72').value
        self.way73 = self.get_parameter('way73').value
        self.way74 = self.get_parameter('way74').value

        # Combine all positions into a single list for further processing
        wayList = [
            self.way11, self.way12, self.way13, self.way14,
            self.way21, self.way22, self.way23, self.way24,
            self.way31, self.way32, self.way33, self.way34,
            self.way41, self.way42, self.way43, self.way44,
            self.way51, self.way52, self.way53, self.way54,
            self.way61, self.way62, self.way63, self.way64,
            self.way71, self.way72, self.way73, self.way74,
        ]

        checkpoints = [
            self.robot1, self.robot2, self.robot3,
            self.store11, self.store12, self.store21, self.store22,
            self.kiosk11, self.kiosk12, self.kiosk21, self.kiosk22
        ]

        all_positions = wayList + checkpoints
        self.print_all_positions(all_positions)

    def print_all_positions(self, positions):
        for i, pos in enumerate(positions):
            self.get_logger().info(f"Position {i}: x = {pos[0]}, y = {pos[1]}, theta = {pos[2]}")

    def update_status(self):
        self.get_logger().info(f"Updating status from {self.status.name}")
        
        self.status = self.status_change[self.status]
        self.get_logger().info(f"Status updated to {self.status.name}")

        if self.status == RobotStatus.RETURNING:
            self.returning()
            self.get_logger().info("Returning to Home")    
        
        if self.status == RobotStatus.AT_HOME:
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


    def short_goal_callback(self, request, response):
        next_point =request.nodenum
        self.get_logger().info(f"next_point : {next_point}")

        ####파싱하는 부분


        self.get_logger().info(f"short goal: {self.next_point}, status : {self.status.value}")

        if self.status in [RobotStatus.HOME, RobotStatus.AT_STORE, RobotStatus.AT_KIOSK]:
            self.update_status()
        elif self.status in [RobotStatus.AT_HOME, RobotStatus. RETURNING]:
            if self.is_active:
                self.status = RobotStatus.TO_STORE
        elif self.status in [RobotStatus.TO_STORE, RobotStatus.TO_KIOSK]:
            pass
        # self.send_goal(next_point)
        self.is_checkpoint()
        self.request_robot_arrival(next_point) ### temp code

        # self.check_succeed(self.position)
        response.success = True
        
        return response

    
    def check_succeed(self, position):
        diff_dist, _, _ = self.calc_diff(position, self.current_goal, position)
        if diff_dist <= 0.02:
            self.get_logger().info("moving is succeed!")
            # self.request_robot_arrival("1")
            self.is_checkpoint()
        else:
            self.send_goal(self.current_goal)
            self.get_logger().debug("moving is failed!")


    def is_checkpoint(self):
        self.get_logger().info("check goal")
        if self.current_msg >= 31 and self.current_msg <= 34 and self.status == RobotStatus.TO_STORE:
            self.update_status()
            self.request_module("ST")
            self.get_logger().info(f"Status updated to {self.status.value} on goal check")
        elif self.current_msg >= 35 and self.current_msg <= 38 and self.status == RobotStatus.TO_KIOSK:
            self.update_status()
            self.request_module("KS")
            self.get_logger().info(f"Status updated to {self.status.value} on goal check")
        elif self.current_msg >= 28 and self.current_msg <= 30 and self.status == RobotStatus.RETURNING:
            self.update_status()
            self.get_logger().info(f"Status updated to {self.status.value} on goal check")


    def goalPose(self, p_x, p_y, degree):
        tmp = [0, 0, degree]
        orientation_val = quaternion_from_euler(tmp[0], tmp[1], tmp[2])
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
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
                print('Distance remaining: ' + '{:.2f}'.format(feedback.distance_remaining) + ' meters.')
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds=10.0):
                    self.nav.cancelTask()
        result = self.nav.getResult()

        if result == TaskResult.SUCCEEDED:
            print('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')


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

        self.current_msg = None
        self.before_msg = None
        self.current_goal = []
        self.position = None
        self.orientation = None
        self.store_point = []
        self.kiosk_point = []
        self.diff_dist = 0.0

        self.is_active = False
    
    def returning(self):
        self.get_logger().info("Robot returning")
        self.store_point = []
        self.kiosk_point = []
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

        self.motor_order_service = self.create_service(LocationInfo, 'location_info', self.motor_order_callback)

        self.timer_period = 1.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.status_pub = self.create_publisher(Int16, "/status", self.qos_profile)

    def motor_order_callback(self, request, response):
        store_id = request.store_id
        kiosk_id = request.kiosk_id

        self.motor_node.store_id = store_id
        self.motor_node.kiosk_id = kiosk_id
        self.motor_node.is_active = True
        response.success = True

        return response

    def status_publish(self, status):
        msg = Int16()
        msg.data = status.value
        self.status_pub.publish(msg)
        # self.get_logger().info(f"Published status: {msg.data}")

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

        self.get_logger().info(f'Received pose: position=({position.x}, {position.y}, {position.z}), orientation=(roll={roll}, pitch={pitch}, yaw={yaw})')
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


if __name__ == '__main__':
    main()


