import rclpy as rp
from rclpy.node import Node
from interface_package.srv import OrderInfo, OrderTracking, RobotCall
from example_interfaces import String
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy


class RobotControl(Node):
    def __init__(self):
        super().__init__("robot_control")

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


        self.order_service = self.create_service(RobotCall, 'robot_call', self.handle_order)

        self.order_clients = {
            1 : self.create_client(OrderInfo, "order_info_1"),
            2 : self.create_client(OrderInfo, "order_info_2")
        }
        self.order_tracking_services = {
            1 : self.create_service(OrderTracking, "order_tracking_1", self.handle_order_tracking_1),
            2 : self.create_service(OrderTracking, "order_tracking_2", self.handle_order_tracking_2)
        }

        self.order_requests = {
            1 : OrderInfo.Request(),
            2 : OrderInfo.Request()
        }

        self.robot_state = ["DS", "DF"] #state 더 추가 예정

        for client_id, client in self.order_clients.items():
            while not client.wait_for_service(timeout_sec= 1.0):
                self.get_logger().info(f'Service {client_id} not available, waiting again...')

    def handle_order(self, request, response):
        self.get_logger().info("Recieved Robot Call")

        robot_id = request.robot_id
        order_id = request.order_id
        store_id = request.store_id
        kiosk_id = request.kiosk_id
        uid = request.uid

        self.get_logger().info(f"robot_id : {robot_id}, order_id : {order_id}, store_id : {store_id}, kiosk_id : {kiosk_id}, uid : {uid}")

        if robot_id in self.order_clients:
            self.send_order_request(robot_id, uid, order_id)
            response.success = True
        else:
            response.success = False

        return response
    
    def handle_order_tracking_1(self, request, response):
        return self.handle_order_tracking(1, request, response)
    
    def handle_order_tracking_2(self, request, response):
        return self.handle_order_tracking(2, request, response)

    def handle_order_tracking(self, robot_id, request, response):
        state = request.state

        if state in self.robot_state:
            self.get_logger().info(f"Received state from robot_id {robot_id} : {state}")
            #모터한테 action 주기
            response.success = True
        else:
            response.success = False

        return response
    
    def send_order_request(self, robot_id, uid, order_id): #함수명 변경 필요할 듯
        self.get_logger().info(f"send to {robot_id}")
        order_request = self.order_requests[robot_id]
        order_request.uid = uid
        order_request.order_id = order_id
        future = self.order_clients[robot_id].call_async(order_request)
        future.add_done_callback(self.handle_order_response_callback(robot_id))

    def handle_order_response_callback(self, robot_id):
        def handle_order_response(future):
            try:
                response = future.result()
                self.get_logger().info(f"Received order response from {robot_id} : {response.success}")
            except Exception as e:
                self.get_logger().info(f"Service call failed for {robot_id} : {e}")
        
        return handle_order_response

def main(args=None):
    rp.init(args=args)
    node = RobotControl()
    rp.spin(node)
    node.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()
