import sys
import os
import csv

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


ROBOT_NUMBER = "1"
# ROBOT_NUMBER = "2"
# ROBOT_NUMBER = "3"

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
        self.nav.waitUntilNav2Active()

        self.is_active = False
        self.store_id = ""
        self.kiosk_id = ""
        self.status = RobotStatus.HOME
        self.is_moving = 0

        self.declare_parameters_from_yaml()
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
        self.goal_point = 0
        self.store_points = []
        self.kiosk_points = []

        self.initial_position = [-0.01277, 0.57464, 0]
        self.before_position = self.initial_position
        self.current_position = [0, 0, 0]
        self.goal_position = ()
        self.diff_dist = 0.0

        self.module_client = self.create_client(Module, "module")

        self.cmd_vel_pub = self.create_publisher(Twist, "/base_controller/cmd_vel_unstamped", 10)
        self.reset_sub = self.create_service(Trigger, "/reset", self.reset_callback)
        
        self.moivig_timer = self.create_timer(1.0, self.moving_timer_callback)
        self.robot_arrival_client = self.create_client(NodeNum, "robotArrival")

        self.get_logger().info(f"R-{ROBOT_NUMBER} motor start")


        self.csv_file = open('pose_data.csv', 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)

        self.navigation_time = None
        self.is_task_complete = None
        self.result = None


    
    def declare_parameters_from_yaml(self):
        self.declare_parameters(
            namespace='',
            parameters=[
                ("robot1", [0.0, 0.0, 0.0]),
                ("robot2", [0.0, 0.0, 0.0]),
                ("robot3", [0.0, 0.0, 0.0]),
                ("store11", [0.0, 0.0, 0.0]),
                ("store12", [0.0, 0.0, 0.0]),
                ("store21", [0.0, 0.0, 0.0]),
                ("store22", [0.0, 0.0, 0.0]),
                ("kiosk11", [0.0, 0.0, 0.0]),
                ("kiosk12", [0.0, 0.0, 0.0]),
                ("kiosk21", [0.0, 0.0, 0.0]),
                ("kiosk22", [0.0, 0.0, 0.0]),
                *[(f"way{i}{j}", [0.0, 0.0, 0.0]) for i in range(1, 8) for j in range(1, 5)]
            ]
        )

    def set_parameters(self):
        #waypoints : 0 ~ 27
        #robot_points : 28 ~30
        #store_points : 31 ~ 34
        #kiosk_points : 35 ~ 38

        self.robot_positions = [(name, self.get_parameter(name).value) for name in ["robot1", "robot2", "robot3"]]
        self.store_positions = [(name, self.get_parameter(name).value) for name in ["store11", "store12", "store21", "store22"]]
        self.kiosk_positions = [(name, self.get_parameter(name).value) for name in ["kiosk11", "kiosk12", "kiosk21", "kiosk22"]]
        
        self.waypoints = [
            (f"way{i}{j}", self.get_parameter(f"way{i}{j}").value)
            for i in range(1, 8)
            for j in range(1, 5)
        ]

        self.all_positions = self.waypoints + self.robot_positions + self.store_positions + self.kiosk_positions
    #     self.print_all_positions(self.all_positions)

    # def print_all_positions(self, positions):
    #     for name, pos in positions:
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

    def moving_timer_callback(self):
        if self.is_moving == 1:
            self.get_logger().info(f"move to {self.goal_position}")
            self.is_moving = 0
            self.send_goal(self.goal_position[1])

    def send_goal(self, goal):
        x = goal[0]
        y = goal[1]
        yaw = goal[2]
        goal_pose = self.goalPose(x, y, yaw)

        diff_x = self.before_position[0] - self.goal_position[1][0]
        diff_y = self.before_position[1] - self.goal_position[1][1]

        self.distance = math.sqrt((diff_x) ** 2 + (diff_y) ** 2)

        if self.distance * 13 >= 5.0:
            nav_time = self.distance * 13
        else:
            nav_time = 5.0

        self.nav.goToPose(goal_pose)
        i = 0
        while not self.nav.isTaskComplete():
            self.feedback = self.nav.getFeedback()
            if self.feedback and i % 5 == 0:
                if Duration.from_msg(self.feedback.navigation_time) > Duration(seconds= (nav_time)):
                    self.nav.cancelTask()
            i += 1

        self.result = self.nav.getResult()

        self.is_task_complete = self.result == TaskResult.SUCCEEDED
        if self.is_task_complete:
            self.get_logger().info("Goal succeeded!")
        elif self.result == TaskResult.CANCELED:
            self.get_logger().info("Goal was canceled!")
        elif self.result == TaskResult.FAILED:
            self.get_logger().info("Goal failed!")

        # 네비게이션 시간 저장
        self.navigation_time = self.feedback.navigation_time._sec if self.feedback else None

        self.request_robot_arrival(self.goal_point)
        self.check_succeed(self.current_position)



    def check_succeed(self, current_position):
        diff_dist, _, _ = self.calc_diff(current_position, self.goal_position[1])
        if diff_dist <= 0.5:
            self.get_logger().info("moving is succeed!")
            # self.request_robot_arrival(int(ROBOT_NUMBER))
            self.verify_checkpoint()
        else:
            self.get_logger().warn("moving is failed!")
            self.send_goal(self.goal_position[1])

    def verify_checkpoint(self):
        if self.goal_point in self.store_points and self.status == RobotStatus.TO_STORE:
            self.update_status()
            self.request_module("ST")
            self.get_logger().info(f"R-{ROBOT_NUMBER} arrived at Store. So, status updated to {self.status.value}")
        elif self.goal_point in self.kiosk_points and self.status == RobotStatus.TO_KIOSK:
            self.update_status()
            self.request_module("KS")
            self.get_logger().info(f"R-{ROBOT_NUMBER} arrived at Kiosk. So, status updated to {self.status.value}")
        elif self.goal_point == (27 + int(ROBOT_NUMBER)) and self.status == RobotStatus.RETURNING:
            self.update_status()
            self.get_logger().info(f"R-{ROBOT_NUMBER} arrived at Home. So, status updated to {self.status.value}")
        else:
            self.get_logger().info("On waypoints")

    def goalPose(self, x, y, yaw):
        #euler
        roll_angle = 0.0
        pitch_angle = 0.0
        yaw_angle = yaw

        quaternion = quaternion_from_euler(roll_angle, pitch_angle, yaw_angle)

        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = self.nav.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.position.z = 0.0
        goal_pose.pose.orientation.x = quaternion[0]
        goal_pose.pose.orientation.y = quaternion[1]
        goal_pose.pose.orientation.z = quaternion[2]
        goal_pose.pose.orientation.w = quaternion[3]

        return goal_pose

    def calc_diff(self, current_position, goal_position):
        if current_position == [0, 0, 0]:
            self.get_logger().warn("Nothing in current position!!!")
            return float('inf', 'inf', 'inf')
    
        current_x = current_position[0]
        current_y = current_position[1]
        current_yaw = current_position[2]

        goal_x = goal_position[0]
        goal_y = goal_position[1]
        goal_yaw = goal_position[2]
        self.diff_x = goal_x - current_x
        self.diff_y = goal_y - current_y
        diff_dist = math.sqrt((self.diff_x) ** 2 + (self.diff_y) ** 2)

        dx = goal_x - current_x
        dy = goal_y - current_y

        yaw_ref = math.atan2(dy, dx)
        diff_yaw = yaw_ref - current_yaw
        diff_yaw = (diff_yaw + math.pi) % (2 * math.pi) - math.pi
        # Assume self.get_logger() is defined or use print statements instead
        print(f"current x : {current_x}, current y : {current_y}, current yaw : {current_yaw}")
        print(f"goal x : {goal_x}, goal y : {goal_y}, goal yaw : {goal_yaw}")
        print(f"diff dist : {diff_dist}, diff yaw : {diff_yaw}")


        self.csv_writer.writerow([
            self.goal_position[0], goal_x, goal_y, goal_yaw,
            current_x, current_y, current_yaw,
            self.before_position[0], self.before_position[1], self.before_position[2],
            diff_dist, diff_yaw,
            self.distance,
            self.navigation_time,
            self.is_task_complete
        ])
        self.csv_file.flush()

        return diff_dist, diff_yaw, yaw_ref
    
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

    def request_robot_arrival(self, goal_point):
        self.get_logger().info(f"{ROBOT_NUMBER} is arrived")
        robot_arrival_request = NodeNum.Request()
        robot_arrival_request.nodenum = goal_point
        future = self.robot_arrival_client.call_async(robot_arrival_request)
        future.add_done_callback(self.response_robot_arrival)

    def response_robot_arrival(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"response {response.success} from TM")
        except Exception as e:
            self.get_logger().error(f"arrival call failed : {e}")

    def reset_callback(self, request, response):
        self.reset()
        response.success = True
        response.message = "reset"

        return response
    
    def reset(self):
        self.get_logger().info("Robot reset")
        self.is_active = False
        self.store_id = ""
        self.kiosk_id = ""
        self.status = RobotStatus.HOME
        self.is_moving = 0
        self.current_point = 0
        self.goal_point = 0
        self.store_points = []
        self.kiosk_points = []
        self.goal_position = ()
        self.current_position = None
        self.diff_dist = 0.0
    
    def returning(self):
        self.get_logger().info("Robot returning")
        self.store_points = []
        self.kiosk_points = []
        self.store_id = ""
        self.kiosk_id = ""
        self.is_active = False

    def __del__(self):
        if self.csv_file:
            self.csv_file.close()

class DrobotTask(Node):
    def __init__(self, motor_node):
        super().__init__("drobot_task")
        self.motor_node = motor_node
        
        self.short_goal_server = self.create_service(NodeNum, "shortGoal", self.short_goal_callback)

        self.motor_order_service = self.create_service(LocationInfo, "location_info", self.motor_order_callback)

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

    def short_goal_callback(self, request, response):
        #waypoints : 0 ~ 27
        #robot_positions : 28 ~30
        #store_points : 31 ~ 34
        #kiosk_points : 35 ~ 38
        self.motor_node.goal_point =request.nodenum # 0 ~ 38
        if 0 <= self.motor_node.goal_point <= 38:
            self.motor_node.goal_position = self.motor_node.all_positions[self.motor_node.goal_point]
            self.get_logger().info(f"goal_position : {self.motor_node.goal_position[0]}, {self.motor_node.goal_position[1]}, status : {self.motor_node.status.value}, active :{self.motor_node.is_active}") 
        else:
            self.get_logger().warn(f"Invalid point!!")
            response.success = False
            return response

        if self.motor_node.is_active:
            if self.motor_node.status in [RobotStatus.HOME, RobotStatus.AT_HOME, RobotStatus.AT_STORE, RobotStatus.AT_KIOSK]:
                if self.motor_node.status == RobotStatus.HOME:
                    if 0 <= self.motor_node.goal_point <= 27:
                        self.motor_node.update_status()
                        self.motor_node.is_moving = 1
                        response.success =  True
                    else:
                        self.get_logger().warn(f"Invalid positions get : {self.motor_node.goal_position}")
                        response.success =  False
                elif self.motor_node.status == RobotStatus.AT_STORE:
                    if 0 <= self.motor_node.goal_point <= 27 or self.motor_node.goal_point in self.motor_node.kiosk_points:
                        self.motor_node.update_status()
                        self.motor_node.is_moving = 1
                        response.success =  True
                    else:
                        self.get_logger().warn(f"Invalid positions get : {self.motor_node.goal_position}")
                        response.success =  False
                elif self.motor_node.status == RobotStatus.AT_KIOSK:
                    if 0 <= self.motor_node.goal_point <= 27 or self.motor_node.goal_point == (27 + int(ROBOT_NUMBER)):
                        self.motor_node.update_status()
                        self.motor_node.is_moving = 1
                        response.success =  True
                    else:
                        self.get_logger().warn(f"Invalid positions get : {self.motor_node.goal_position}")
                        response.success =  False
            elif self.motor_node.status in [RobotStatus.TO_STORE]:
                if 0 <= self.motor_node.goal_point <= 27 or self.motor_node.goal_point in self.motor_node.store_points:
                    self.motor_node.is_moving = 1
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.motor_node.goal_position}")
                    response.success =  False
            elif self.motor_node.status == RobotStatus.TO_KIOSK:
                if 0 <= self.motor_node.goal_point <= 27 or self.motor_node.goal_point in self.motor_node.kiosk_points:
                    self.motor_node.is_moving = 1
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.motor_node.goal_position}")
                    response.success =  False
        else:
            self.motor_node.get_logger().info(f"status : {self.motor_node.status}, goal_point : {self.motor_node.goal_point}, active : {self.motor_node.is_active}")
            if self.motor_node.status == RobotStatus.RETURNING:
                if 0 <= self.motor_node.goal_point <= 27 or self.motor_node.goal_point == (27 + int(ROBOT_NUMBER)):
                    self.motor_node.is_moving = 1
                    response.success =  True
                else:
                    self.get_logger().warn(f"Invalid positions get : {self.motor_node.goal_position}")
                    response.success =  False
            else:
                self.get_logger().warn("There is not order!!")
                response.success =  False

        # if response.success == True:

        #     self.motor_node.verify_checkpoint()

        return response
    
class DrobotStatus(Node):
    def __init__(self, motor_node):
        super().__init__("drobot_status")
        self.motor_node = motor_node
        self.qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.status_pub = self.create_publisher(Int16, "/status", self.qos_profile)

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
        self.motor_node.before_position[0] = self.motor_node.current_position[0]
        self.motor_node.before_position[1] = self.motor_node.current_position[1]
        self.motor_node.before_position[2] = self.motor_node.current_position[2]


        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation

        quaternion = (orientation.x, orientation.y, orientation.z, orientation.w)
        euler = euler_from_quaternion(quaternion)
        roll, pitch, yaw = euler

        x = position.x
        y = position.y

        # self.get_logger().info(f"Received pose: x={x}, y={y}, yaw={yaw}")
        
        # motor_node에 x, y, yaw 값을 전달
        self.motor_node.current_position[0] = x
        self.motor_node.current_position[1] = y
        self.motor_node.current_position[2] = yaw
        print(self.motor_node.before_position)
        print(self.motor_node.current_position)

def main(args=None):
    rp.init(args=args)
    executor = MultiThreadedExecutor()

    drobot_motor = DrobotMotor()
    drobot_status = DrobotStatus(motor_node= drobot_motor)
    amcl_sub = AmclSub(motor_node= drobot_motor)
    drobot_task = DrobotTask(motor_node= drobot_motor)

    executor.add_node(drobot_motor)
    executor.add_node(drobot_status)
    executor.add_node(drobot_task)
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
            drobot_task.destroy_node()
            rp.shutdown()


if __name__ == "__main__":
    main()

