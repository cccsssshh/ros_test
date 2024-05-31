from enum import Enum

import rclpy as rp
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from std_msgs.msg import Int16
from std_msgs.msg import String
from time import sleep

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
from tf_transformations import quaternion_from_euler


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


class DrobotMotor(Node):
    def __init__(self):
        super().__init__("drobot_motor")

        self.nav = BasicNavigator()
        self.nav.waitUntilNav2Active()

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        self.timer_period = 1.0
        self.status = RobotStatus.HOME
        self.before_msg = ""
        self.result = None
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.status_pub = self.create_publisher(Int16, "/status", qos_profile)
        self.move = self.create_subscription(String, "/move", self.move_callback, qos_profile)

        self.get_logger().info("motor start")

        self.robot1 = [0.0, 2.5, 0]
        self.robot2 = [0.0, 1.5, 0]
        self.robot3 = [0.0, 0.3, 0]

        self.kiosk11 = [0.3, 3.0, 80]
        self.kiosk12 = [1.15, 2.8, 80]
        self.kiosk21 = [1.15, 0.5, -80]
        self.kiosk22 = [0.3, 0.5, -80]

        self.store11 = [1.3, 2.6, 0]
        self.store12 = [1.3, 1.7, 0]
        self.store21 = [1.3, 1.3, 0]
        self.store22 = [1.3, 0.3, 0]

        self.way1 = [0.3, 2.6, 0]
        self.way2 = [0.3, 1.5, -80]
        self.way3 = [0.3, 0.3, -80]
        self.way4 = [1.15, 0.3, 160]
        self.way5 = [1.15, 1.5, 160]
        self.way6 = [1.15, 2.5, 80]

    def move_callback(self, msg):
        if self.before_msg != msg.data:
            if self.status == RobotStatus.HOME:
                self.status = RobotStatus.TO_STORE
                if msg.data == RobotGoal.STORE_1.value:
                    self.send_goal(self.way2)  # degree 값을 추가로 전달
                    self.get_logger().info('send : S-1')
                elif msg.data == RobotGoal.STORE_2.value:
                    self.get_logger().info('send : S-2')
                    self.send_goal(self.way5)  # degree 값을 추가로 전달
                # # 도착 했다는 조건
                # if self.result == TaskResult.SUCCEEDED:
                self.status = RobotStatus.AT_STORE
            elif self.status == RobotStatus.AT_STORE:
                self.status = RobotStatus.TO_KIOSK  # 수정: TO_STORE -> TO_KIOSK
                if msg.data == RobotGoal.KIOSK_1.value:
                    self.send_goal(self.kiosk21)  # degree 값을 추가로 전달
                    self.get_logger().info('send : K-1')
                elif msg.data == RobotGoal.KIOSK_2.value:
                    self.get_logger().info('send : K-2')

                # # 도착 했다는 조건
                # if self.result == TaskResult.SUCCEEDED:
                self.status = RobotStatus.AT_KIOSK
            elif self.status == RobotStatus.AT_KIOSK:
                self.status = RobotStatus.RETURNING
                if msg.data == RobotGoal.HOME.value:
                    self.send_goal(self.robot3)  # degree 값을 추가로 전달
                    self.get_logger().info('send : H-1')

                # # 도착 했다는 조건
                # if self.result == TaskResult.SUCCEEDED:
                self.status = RobotStatus.AT_HOME  # 수정: RobotGoal.HOME -> RobotStatus.AT_HOME

            self.before_msg = msg.data

    def status_publish(self, status):
        msg = Int16()
        msg.data = status.value
        self.status_pub.publish(msg)
        print(msg.data)

    def timer_callback(self):
        self.status_publish(self.status)

    def goalPose(self, p_x, p_y, degree):  # 수정: self 추가
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

    def send_goal(self, goal):  # degree 인자를 추가로 받도록 수정
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
                if Duration.from_msg(feedback.navigation_time) > Duration(seconds=20.0):
                    self.nav.cancelTask()
        result = self.nav.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')


def main(args=None):
    rp.init(args=args)
    drobot_motor = DrobotMotor()
    try:
        rp.spin(drobot_motor)
    except KeyboardInterrupt:
        pass
    finally:
        if rp.ok():
            drobot_motor.destroy_node()
            rp.shutdown()


if __name__ == '__main__':
    main()


