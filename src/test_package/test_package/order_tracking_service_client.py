import rclpy
from rclpy.node import Node
from interface_package.srv import OrderTracking

class OrderTrackingClient(Node):

    def __init__(self):
        super().__init__('order_tracking_client')
        self.client_1 = self.create_client(OrderTracking, 'order_tracking_1')
        self.client_2 = self.create_client(OrderTracking, 'order_tracking_2')

        while not self.client_1.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service order_tracking_1 not available, waiting again...')
        while not self.client_2.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service order_tracking_2 not available, waiting again...')

    def send_request_1(self, state):
        request = OrderTracking.Request()
        request.state = state
        self.future_1 = self.client_1.call_async(request)
        self.future_1.add_done_callback(self.handle_response_1)

    def send_request_2(self, state):
        request = OrderTracking.Request()
        request.state = state
        self.future_2 = self.client_2.call_async(request)
        self.future_2.add_done_callback(self.handle_response_2)

    def handle_response_1(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'Received order_tracking_1 response: {response.success}')
        except Exception as e:
            self.get_logger().info(f'Service call failed: {e}')

    def handle_response_2(self, future):
        try:
            response = future.result()
            self.get_logger().info(f'Received order_tracking_2 response: {response.success}')
        except Exception as e:
            self.get_logger().info(f'Service call failed: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = OrderTrackingClient()

    # 예시로 요청을 보냅니다.
    node.send_request_1('DS')
    node.send_request_2('DF')

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
