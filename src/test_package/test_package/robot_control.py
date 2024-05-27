import rclpy as rp
from rclpy.node import Node
from interface_package.srv import OrderInfo, OrderTracking, RobotCall, GoalArrival, DeliveryBox
from rclpy.executors import MultiThreadedExecutor

class RobotControl(Node):
    def __init__(self):
        super().__init__("robot_control")
        self.robot_call_service = self.create_service(RobotCall, "robot_call", self.robot_call_callback)
        self.get_logger().info("Robot call service created.")

        self.module_call_client = self.create_client(RobotCall, "module_call")
        self.motor_call_client = self.create_client(RobotCall, "motor_call")
        
        self.delivery_box_client = self.create_client(DeliveryBox,"delivery_box")
        # self.order_tracking_server = self.create_service(OrderTracking,"order_tracking", self.order_tracking_callback)

        self.order_info = {}
        self.robot_info = {}


    def update_robot_info(self, robot_id, order_id, store_id, kiosk_id, uid):
        self.robot_info[robot_id] = {
            "order_id": order_id,
            "store_id": store_id,
            "kiosk_id": kiosk_id,
            "uid": uid
        }
    
    def update_order_info(self, robot_id, order_id, store_id, kiosk_id, uid):
        self.order_info[order_id] = {
            "robot_id": robot_id,
            "store_id": store_id,
            "kiosk_id": kiosk_id,
            "uid": uid
        }

    def robot_call_callback(self, request, response):
        self.get_logger().info("Received Robot Call")

        robot_id = request.robot_id
        order_id = request.order_id
        store_id = request.store_id
        kiosk_id = request.kiosk_id
        uid = request.uid

        self.get_logger().info(f"robot_id : {robot_id}, order_id : {order_id}, store_id : {store_id}, kiosk_id : {kiosk_id}, uid : {uid}")
        self.update_robot_info(robot_id, order_id, store_id, kiosk_id, uid)
        self.update_order_info(robot_id, order_id, store_id, kiosk_id, uid)

        if not robot_id or not order_id or not uid or not store_id or not kiosk_id:
            self.get_logger().error("Missing required fields in the request.")
            response.success = False
        else:
            self.get_logger().info(f"Request Module call : robot_id {robot_id}, order_id : {order_id}, uid : {uid}")
            self.get_logger().info(f"Request Motor call : robot_id {robot_id}, store_id: {store_id}, kiosk_id : {kiosk_id}")

            self.request_module_call(robot_id, order_id, uid)
            # self.request_motor_call(robot_id, store_id, kiosk_id)
            response.success = True

        return response
    
    def request_module_call(self, robot_id, order_id, uid):
        module_call_request = RobotCall.Request()
        module_call_request.robot_id = robot_id
        module_call_request.order_id = order_id
        module_call_request.store_id = ""
        module_call_request.kiosk_id = ""
        module_call_request.uid = uid
        
        future = self.module_call_client.call_async(module_call_request)
        future.add_done_callback(self.response_module_call)

    def request_motor_call(self, robot_id, store_id, kiosk_id):
        motor_call_request = RobotCall.Request()
        motor_call_request.robot_id = robot_id
        motor_call_request.order_id = ""
        motor_call_request.store_id = store_id
        motor_call_request.kiosk_id = kiosk_id
        motor_call_request.uid = ""
        
        future = self.motor_call_client.call_async(motor_call_request)
        future.add_done_callback(self.response_motor_call)

    def response_module_call(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("Module call succeeded.")
            else:
                self.get_logger().info("Module call failed.")
        except Exception as e:
            self.get_logger().error(f"Module call failed with exception: {e}")
    
    def response_motor_call(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("Motor call succeeded.")
            else:
                self.get_logger().info("Motor call failed.")
        except Exception as e:
            self.get_logger().error(f"Motor call failed with exception: {e}")

    def order_tracking_callback(self, request, response):
        self.get_logger().info("Received order tracking from module_control")
    
        delivery_box = DeliveryBox.Request()
        order_id = request.order_id
        robot_id = self.order_info[order_id]["robot_id"]
        delivery_box.robot_id = robot_id
        delivery_box.order_id = request.order_id
        delivery_box.status = request.status
        
        future = self.delivery_box_client.call_async(delivery_box)
        future.add_done_callback(self.response_delivery_box)

        # if request.status = "DF"

        response.success = True

        return response
    
    def response_delivery_box(self, future):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info("Delivery box request succeeded.")
            else:
                self.get_logger().info("Delivery box request failed.")
        except Exception as e:
            self.get_logger().error(f"Delivery box request failed with exception: {e}")

class ModuleControl(Node):
    def __init__(self):
        super().__init__("module_control")

        self.module_call_service = self.create_service(RobotCall, "module_call", self.module_call_callback)
        # self.order_tracking_client = self.create_client(OrderTracking, "order_tracking")

        self.order_clients = {
            '1' : self.create_client(OrderInfo, "order_info_1"),
            '2' : self.create_client(OrderInfo, "order_info_2")
        }
        self.order_tracking_services = {
            '1' : self.create_service(OrderTracking, "order_tracking_1", self.order_tracking_callback_1),
            '2' : self.create_service(OrderTracking, "order_tracking_2", self.order_tracking_callback_2)
        }
        self.get_logger().info("Order clients and tracking services created.")

        self.order_status = ["DS", "DF"] #state 더 추가 예정

        # for client_id, client in self.order_clients.items():
        #     while not client.wait_for_service(timeout_sec= 1.0):
        #         self.get_logger().info(f'Service {client_id} not available, waiting again...')
        while not self.order_clients['1'].wait_for_service(timeout_sec= 1.0):
            self.get_logger().info('Service 1 not available, waiting again...')

    def module_call_callback(self, request, response):
        self.get_logger().info("Received module Call")

        robot_id = request.robot_id
        order_id = request.order_id
        uid = request.uid

        self.get_logger().info(f"robot_id : {robot_id}, order_id : {order_id}, uid : {uid}")

        if robot_id in self.order_clients:
            self.request_order(robot_id, uid, order_id)
            response.success = True
        else:
            response.success = False

        return response
    
    def order_tracking_callback_1(self, request, response):
        return self.order_tracking_callback(1, request, response)
    
    def order_tracking_callback_2(self, request, response):
        return self.order_tracking_callback(2, request, response)

    def order_tracking_callback(self, robot_id, request, response):
        try:
            self.get_logger().info(f"Received status update: {request.status} for order_id: {request.order_id} from robot_id: {robot_id}")
            
            order_id = request.order_id
            status = request.status

            if status in self.order_status:
                self.get_logger().info(f"Valid status received: {status} for robot_id: {robot_id}")
                response.success = True
            else:
                self.get_logger().info(f"Invalid status received: {status} for robot_id: {robot_id}")
                response.success = False
        except Exception as e:
            self.get_logger().error(f"Exception in order_tracking_callback: {e}")
            response.success = False

        return response

        
    def request_order(self, robot_id, uid, order_id): #함수명 변경 필요할 듯
        self.get_logger().info(f"send to {robot_id}")
        order_request = OrderInfo.Request()
        order_request.uid = uid
        order_request.order_id = order_id
        future = self.order_clients[robot_id].call_async(order_request)
        future.add_done_callback(self.response_order_callback(robot_id))


    def response_order_callback(self, robot_id):
        def response_order(future):
            try:
                response = future.result()
                self.get_logger().info(f"Received order response from {robot_id} : {response.success}")

            except Exception as e:
                self.get_logger().info(f"Service call failed for {robot_id} : {e}")
        
        return response_order
    
    def request_order_id(self, order_id, status):
        order_tracking = OrderTracking.Request()
        order_tracking.order_id = order_id
        order_tracking.status = status
        future = self.order_tracking_client.call_async(order_tracking)
        future.add_done_callback(self.response_order_tracking)

    # def response_order_tracking(self, future):
    #     try:
    #         response = future.result()
    #         if response.success:
    #             self.get_logger().info("Order tracking succeeded.")
    #         else:
    #             self.get_logger().info("Order tracking failed.")
    #     except Exception as e:
    #         self.get_logger().error(f"Order tracking failed with exception: {e}")

# class MotorControl(Node):

#     def __init__(self):
#         super()._init__("motor_control")

#         self.goal_arrival_client = self.create_client(GoalArrival, "arrival_status")

#         # self.request_arrival_status(robot_id, order_id, status)


#         # Received from robots and send to RC
#     def request_arrival_status(self, robot_id, order_id, status):
#         # 1 : 매장 도착
#         # 2 : 키오스크 도착
#         # 3 : 충전장소 복귀 완료
#         self.get_logger().info(f"send {robot_id} {status} to Robotcontrol")
#         arrival_status_request = GoalArrival.Request()
#         arrival_status_request.status = status
#         arrival_status_request.robot_id = robot_id
#         arrival_status_request.order_id = order_id

#         future = self.order_tracking_client.call_async(arrival_status_request)
#         future.add_done_callback(self.response_arrival_status)
#     # (Received from robots and send to RM)'s response
#     def response_arrival_status(self, future):
#         try:
#             response = future.result()
#             robot_id = response.robot_id
#             self.get_logger().info(f"Received order response from {robot_id} : {response.success}")
#         except Exception as e:
#             self.get_logger().info(f"Service call failed for {robot_id} : {e}")


def main(args=None):

    rp.init(args=args)

    robot_control = RobotControl()
    module_control = ModuleControl()

    executor = MultiThreadedExecutor()

    executor.add_node(robot_control)
    executor.add_node(module_control)
    
    # rfid_control.request_order(2, '43 09 0F F8', '1')
    
    try:
        executor.spin()
    finally:
        executor.shutdown()
        robot_control.destroy_node()
        module_control.destroy_node()
        rp.shutdown()

if __name__ == '__main__':
    main()
