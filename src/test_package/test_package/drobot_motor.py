from enum import Enum

import rclpy as rp
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import Int16, String, Float32MultiArray
from interface_package.srv import Module
from rclpy.executors import MultiThreadedExecutor
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped, Twist
from rclpy.duration import Duration
from tf_transformations import quaternion_from_euler, euler_from_quaternion

import math
from time import sleep

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


class RobotGoal(Enum):
    STORE_1 = "S-1"
    STORE_2 = "S-2"
    KIOSK_1 = "K-1"
    KIOSK_2 = "K-2"
    HOME = "H-1"

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

class DrobotMotor(Node):
    def __init__(self):
        super().__init__("drobot_motor")

        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        self.nav = BasicNavigator()
        self.nav.waitUntilNav2Active()

        self.status = RobotStatus.HOME
        self.before_msg = []
        self.stores = []
        self.kiosks = []

        self.position = None
        self.orientation = None
        #서비스 주고 받아야 함
        self.store_goal = None
        self.kiosk_goal = None
        self.waypoint = None
        self.diff_dist = 0.0
        self.is_succeed = False

        self.short_goal = self.create_subscription(Float32MultiArray, "/short_goal", self.short_goal_callback, self.qos_profile)
        self.module_client = self.create_client(Module, "module")
        self.cmd_vel_pub = self.create_publisher(Twist, "/base_controller/cmd_vel_unstamped", 10)

        self.get_logger().info("motor start")

        # self.declare_parameters(
        #     namespace="",
        #     parameters=[
        #         ("robot_coordinates.robot1", [0.0, 2.5, 0.0]),
        #         ("robot_coordinates.robot2", [0.0, 1.6, 0.0]),
        #         ("robot_coordinates.robot3", [0.0, 0.6, 0.0]),
        #         ("store_coordinates.store11", [1.4, 2.6, 0.0]),
        #         ("store_coordinates.store12", [1.4, 1.7, 0.0]),
        #         ("store_coordinates.store21", [1.4, 1.2, 0.0]),
        #         ("store_coordinates.store22", [1.4, 0.4, 0.0]),
        #         ("kiosk_coordinates.kiosk11", [0.3, 2.8, 80.0]),
        #         ("kiosk_coordinates.kiosk12", [1.0, 2.8, 80.0]),
        #         ("kiosk_coordinates.kiosk21", [1.0, 0.1, -80.0]),
        #         ("kiosk_coordinates.kiosk22", [0.3, 0.1, -80.0]),
        #         ("waypoints.way1", [0.3, 2.6, 0.0]),
        #         ("waypoints.way2", [0.3, 1.5, -80.0]),
        #         ("waypoints.way3", [0.3, 0.3, -80.0]),
        #         ("waypoints.way4", [1.15, 0.3, 160.0]),
        #         ("waypoints.way5", [1.15, 1.5, 160.0]),
        #         ("waypoints.way6", [1.15, 2.5, 80.0]),
        #     ]
        # )

        # self.robot1 = self.get_parameter("robot_coordinates.robot1").value
        # self.robot2 = self.get_parameter("robot_coordinates.robot2").value
        # self.robot3 = self.get_parameter("robot_coordinates.robot3").value
        
        # self.store11 = self.get_parameter("store_coordinates.store11").value
        # self.store12 = self.get_parameter("store_coordinates.store12").value
        # self.store21 = self.get_parameter("store_coordinates.store21").value
        # self.store22 = self.get_parameter("store_coordinates.store22").value

        # self.kiosk11 = self.get_parameter("kiosk_coordinates.kiosk11").value
        # self.kiosk12 = self.get_parameter("kiosk_coordinates.kiosk12").value
        # self.kiosk21 = self.get_parameter("kiosk_coordinates.kiosk21").value
        # self.kiosk22 = self.get_parameter("kiosk_coordinates.kiosk22").value

        # self.way1 = self.get_parameter("waypoints.way1").value
        # self.way2 = self.get_parameter("waypoints.way2").value
        # self.way3 = self.get_parameter("waypoints.way3").value
        # self.way4 = self.get_parameter("waypoints.way4").value
        # self.way5 = self.get_parameter("waypoints.way5").value
        # self.way6 = self.get_parameter("waypoints.way6").value

    def short_goal_callback(self, msg):
        current_msg = msg.data

        if self.before_msg != current_msg:
            if self.status == RobotStatus.HOME:
                self.status = RobotStatus.TO_STORE
                self.request_module("ST")
                self.send_goal(current_msg)
                self.is_goal()
            elif self.status == RobotStatus.TO_STORE:
                self.send_goal(current_msg)
                self.is_goal()
            elif self.status == RobotStatus.AT_STORE:
                self.status = RobotStatus.TO_KIOSK
                self.request_module("KS")
                self.send_goal(current_msg)
                self.is_goal()
            elif self.status == RobotStatus.AT_KIOSK:
                self.send_goal(current_msg)
                self.is_goal()
            elif self.status == RobotStatus.AT_KIOSK:
                self.status = RobotStatus.RETURNING
                self.send_goal(current_msg)
                self.is_goal()
            elif self.status == RobotStatus.RETURNING:
                self.send_goal(current_msg)
                self.is_goal()

        self.before_msg = current_msg
        
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
            i = i + 1
            feedback = self.nav.getFeedback()
            if feedback and i % 5 == 0:
                print('Distance remaining: ' + '{:.2f}'.format(feedback.distance_remaining) + ' meters.')
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds=30.0):
                    self.nav.cancelTask()
        result = self.nav.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Goal succeeded!')
            self.diff_dist = self.calc_diff_pose(goal, self.position)
            if self.diff_dist >= 0.02:
                return True
            else:
                self.cmd_vel_pub.publish(self.dist)
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')




    def calc_diff_pose(self, goal, current):
        goal_x = goal[0]
        goal_y = goal[1]
        goal_yaw = goal[2]
        current_x = current.x
        current_y = current.y
        current_yaw = current.yaw
        self.diff_x = goal_x - current_x
        self.diff_y = goal_y - current_y
        diff_dist = math.sqrt((self.diff_x) ** 2 + (self.diff_y) ** 2)


        return diff_dist

    def is_goal(self, robot_goal, current_position):
        if self.status == RobotStatus.TO_STORE:
            #robot이 도착
            self.status == RobotStatus.AT_STORE
        elif self.status == RobotStatus.TO_KIOSK:
            #robot이 도착
            self.status == RobotStatus.AT_KIOSK
        elif self.status == RobotStatus.RETURNING:
            #robot이 도착
            self.status == RobotStatus.AT_HOME




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


class DrobotStatus(Node):
    def __init__(self, motor_node):
        super().__init__("drobot_status")
        self.motor_node = motor_node
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        self.timer_period = 1.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.status_pub = self.create_publisher(Int16, "/status", self.qos_profile)

    def status_publish(self, status):
        msg = Int16()
        msg.data = status.value
        self.status_pub.publish(msg)
        self.get_logger().info(f"Published status: {msg.data}")

    def timer_callback(self):
        self.status_publish(self.motor_node.status)


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


