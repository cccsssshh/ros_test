import rclpy as rp
from rclpy.node import Node
from example_interfaces.msg import Int16
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy


class RobotStatus(Node):
    
    def __init__(self):
        super().__init__("robot_status")

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        
        self.status_1 = self.create_subscription(Int16, "robot_status_1", self.status_callback_1, qos_profile)
        self.status_2 = self.create_subscription(Int16, "robot_status_2", self.status_callback_2, qos_profile)
        self.status_3 = self.create_subscription(Int16, "robot_status_3", self.status_callback_3, qos_profile)

    def status_callback_1(self, msg):
        #로봇 상태 : 0, 1, 2
        # 0 : 대기중
        # 1 : 배달중
        status = msg.data

        # if status == 0:
            
        # elif status == 1:
