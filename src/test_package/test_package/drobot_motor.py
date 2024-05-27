import rclpy as rp
from rclpy.node import Node
from rclpy.action import ActionClient, ActionServer
from example_interfaces import String
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

class DrobotMotor(Node):

    def __ini__(self):
        super().__init__("drobot_motor")
        timer_period = 10.0
        self.create_timer = self.create_timer(timer_period, self.timer_callback)

        self.robot_status = ["RC", "DS", "DF", "RT"]
        # RC : RobotCall
        # DS : DeliveryStarted
        # DF : DeliveryFinished
        # RT : Return
        
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

                self.send_goals_pub = {
            1 : self.create_publisher(String, "/goal_1", qos_profile),
            2 : self.create_publisher(String, "/goal_2", qos_profile),
            3 : self.create_publisher(String, "/goal_3", qos_profile)
        }