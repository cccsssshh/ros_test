import rclpy as rp
from rclpy.node import Node
from interface_package.srv import OrderInfo, OrderTracking

class RobotControl(Node):
    def __init__(self):
        super().__init__("robot_control")


        # self.order_service = self.create_service(Order, 'oreder', self.handle_order)
        self.order_client = self.create_client(OrderInfo, 'order_info_1')
        self.order_tracking_service = self.create_service(OrderTracking,
                                                          'order_tracking',
                                                          self.handle_order_tracking)
        self.order_client_2 = self.create_client(OrderInfo, 'order_info_2')
        self.order_tracking_service_2 = self.create_service(OrderTracking,
                                                          'order_tracking_2',
                                                          self.handle_order_tracking_2)

        while not self.order_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        while not self.order_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service_2 not available, waiting again...')

        self.order_req = OrderInfo.Request()
        self.order_req_2 = OrderInfo.Request()
 
    
    # def handle_order(self, request, response):
    #     robot_id = 


    def handle_order_tracking(self, request, response):
        state = request.state

        if state == "DS":
            self.get_logger().info(f"Received state : {state}")
            #모터한테 action 주기
            response.success = True
        elif state == "DF":
            self.get_logger().info(f"Received state : {state}")
            response.success = True
            #모터한테 action 주기
        else:
            response.success = False
        #state = 스토어로 가는 중, 대기 중
        
        return response
    
    def handle_order_tracking_2(self, request, response):
        state = request.state

        if state == "DS":
            self.get_logger().info(f"Received state : {state}")
            #모터한테 action 주기
            response.success = True
        elif state == "DF":
            self.get_logger().info(f"Received state : {state}")
            response.success = True
            #모터한테 action 주기
        else:
            response.success = False
        #state = 스토어로 가는 중, 대기 중
        
        return response
        

    def send_order_request(self, uid, order_id):
        self.order_req.uid = uid
        self.order_req.order_id = order_id
        self.future = self.order_client.call_async(self.order_req)
        self.future.add_done_callback(self.handle_order_response)

    def send_order_request_2(self, uid, order_id):
        self.order_req_2.uid = uid
        self.order_req_2.order_id = order_id
        self.future = self.order_client_2.call_async(self.order_req_2)
        self.future.add_done_callback(self.handle_order_response_2)

    def handle_order_response(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Received order response: {response.success}")
        except Exception as e:
            self.get_logger().info(f"Service call failed: {e}")


    def handle_order_response_2(self, future):
        try:
            response = future.result()
            self.get_logger().info(f"Received order response: {response.success}")
        except Exception as e:
            self.get_logger().info(f"Service call failed: {e}")


def main(args=None):
    rp.init(args=args)
    node = RobotControl()
    node.send_order_request('43 09 0F F8', '1')
    rp.spin(node)
    node.destroy_node()
    rp.shutdown()

if __name__ == '__main__':
    main()
