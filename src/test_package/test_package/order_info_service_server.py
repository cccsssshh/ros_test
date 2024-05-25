import rclpy
from rclpy.node import Node
from interface_package.srv import OrderInfo

class OrderInfoService(Node):
    def __init__(self):
        super().__init__('order_info_service')
        self.srv = self.create_service(OrderInfo, 'order_info', self.handle_order_info)

    def handle_order_info(self, request, response):
        self.get_logger().info(f'Received order request: uid={request.uid}, order_id={request.order_id}')
        # 실제 로직을 추가하여 요청을 처리합니다.
        response.success = True  # 예시로 항상 성공으로 설정합니다.
        return response

def main(args=None):
    rclpy.init(args=args)
    node = OrderInfoService()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
