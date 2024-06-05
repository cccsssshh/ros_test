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

        self.current_msg = []
        self.before_msg = []
        self.stores = []
        self.kiosks = []

        self.position = None
        self.orientation = None
        #서비스 주고 받아야 함
        self.current_goal = None
        self.store_goal = None
        self.kiosk_goal = None
        self.home = []
        self.waypoint = None
        self.diff_dist = 0.0
        self.moving_status = 0

        self.short_goal = self.create_subscription(Float32MultiArray, "/short_goal", self.short_goal_callback, self.qos_profile)
        self.module_client = self.create_client(Module, "module")
        self.cmd_vel_pub = self.create_publisher(Twist, "/base_controller/cmd_vel_unstamped", 10)


        self.get_logger().info("motor start")


    def short_goal_callback(self, msg):
        self.current_msg = msg.data

        if self.before_msg != self.current_msg:
            self.moving_status = 1

            if self.status == RobotStatus.HOME:
                self.current_goal = self.store_goal
                self.status = RobotStatus.TO_STORE
                self.request_module("ST")
                self.send_goal(self.current_msg)
                self.check_goal()
            elif self.status == RobotStatus.TO_STORE:
                self.send_goal(self.current_msg)
                self.check_goal()
            elif self.status == RobotStatus.AT_STORE:
                self.current_goal = self.kiosk_goal
                self.status = RobotStatus.TO_KIOSK
                self.request_module("KS")
                self.send_goal(self.current_msg)
                self.check_goal()
            elif self.status == RobotStatus.AT_KIOSK:
                self.send_goal(self.current_msg)
                self.check_goal()
            elif self.status == RobotStatus.AT_KIOSK:
                self.current_goal = self.home
                self.status = RobotStatus.RETURNING
                self.send_goal(self.current_msg)
                self.check_goal()
            elif self.status == RobotStatus.RETURNING:
                self.send_goal(self.current_msg)
                self.check_goal()

        self.before_msg = self.current_msg
        
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
            self.check_point(self.position)
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')

    
    def check_point(self, position):
        diff_dist, _, _ = self.calc_diff(position, self.current_goal, position)
        if diff_dist <= 0.02:
            return True
        else:
            self.send_goal(self.current_msg)

    def angle_command(self, diff_angle, goal_yaw):
        msg = Twist()


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
    

    def check_goal(self, robot_goal, current_position):
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


