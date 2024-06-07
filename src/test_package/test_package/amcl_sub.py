import matplotlib.pyplot as plt
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped

class AMCLListener(Node):
    def __init__(self):
        super().__init__('amcl_listener')
        self.subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            'amcl_pose',
            self.listener_callback,
            10
        )
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        # amcl_pose 메시지에서 covariance 필드만 추출
        covariance = msg.pose.covariance
        self.get_logger().info(f'Received covariance: {covariance}')

    def analyze_covariances(self):
        if not self.covariances:
            self.get_logger().info('No covariance data to analyze.')
            return

        cov_array = np.array(self.covariances)
        mean_cov = np.mean(cov_array, axis=0)
        std_cov = np.std(cov_array, axis=0)

        self.get_logger().info(f'Mean covariance: {mean_cov}')
        self.get_logger().info(f'Standard deviation of covariance: {std_cov}')

        # 그래프 시각화
        plt.figure()
        plt.errorbar(range(len(mean_cov)), mean_cov, yerr=std_cov, fmt='o', label='Covariance')
        plt.xlabel('Index')
        plt.ylabel('Covariance')
        plt.title('Covariance Analysis')
        plt.legend()
        plt.show()


def main(args=None):
    rclpy.init(args=args)
    node = AMCLListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.analyze_covariances()  # 분석 함수 호출
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
