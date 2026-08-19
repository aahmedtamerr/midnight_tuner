import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from turtlesim.msg import Color
from std_msgs.msg import String


class MidnightTuner(Node):

    def __init__(self):
        super().__init__('midnight_tuner')

        # =========================
        # Parameters
        # =========================

        self.declare_parameter(
            'cmd_vel_topic',
            '/turtle1/cmd_vel'
        )

        self.declare_parameter(
            'color_topic',
            '/turtle1/color_sensor'
        )

        self.declare_parameter(
            'dominant_color_topic',
            '/dominant_color'
        )

        # Get parameters
        cmd_vel_topic = self.get_parameter(
            'cmd_vel_topic'
        ).value

        color_topic = self.get_parameter(
            'color_topic'
        ).value

        dominant_color_topic = self.get_parameter(
            'dominant_color_topic'
        ).value

        # =========================
        # Publisher
        # =========================

        self.cmd_vel_pub = self.create_publisher(
            Twist,
            cmd_vel_topic,
            10
        )

        self.color_pub = self.create_publisher(
            String,
            dominant_color_topic,
            10
        )

        # =========================
        # Subscriber
        # =========================

        self.color_sub = self.create_subscription(
            Color,
            color_topic,
            self.color_callback,
            10
        )

        self.settings = None

        if sys.stdin.isatty():
            self.settings = termios.tcgetattr(sys.stdin)

        self.timer = self.create_timer(
            0.05,
            self.keyboard_callback
        )

        self.get_logger().info(
            'Midnight Tuner started!'
        )

        self.get_logger().info(
            'Controls: W=Forward, S=Backward, '
            'A=Left, D=Right'
        )

    # =========================
    # Color perception
    # =========================

    def color_callback(self, msg):

        r = msg.r
        g = msg.g
        b = msg.b

        if r >= g and r >= b:
            dominant = 'RED'

        elif g >= r and g >= b:
            dominant = 'GREEN'

        else:
            dominant = 'BLUE'

        self.get_logger().info(
            f'Dominant color: {dominant}'
        )

        color_msg = String()
        color_msg.data = dominant

        self.color_pub.publish(color_msg)

    # =========================
    # Keyboard movement
    # =========================

    def get_key(self):
        if not sys.stdin.isatty():
            return ''

        tty.setraw(sys.stdin.fileno())

        key = ''
        if select.select([sys.stdin], [], [], 0.05)[0]:
            key = sys.stdin.read(1)

        termios.tcsetattr(
            sys.stdin,
            termios.TCSADRAIN,
            self.settings
        )

        return key
    def keyboard_callback(self):

        key = self.get_key()

        msg = Twist()

        # W -> Forward
        if key.lower() == 'w':

            msg.linear.x = 2.0
            msg.angular.z = 0.0

        # S -> Backward
        elif key.lower() == 's':

            msg.linear.x = -2.0
            msg.angular.z = 0.0

        # A -> Rotate Left
        elif key.lower() == 'a':

            msg.linear.x = 0.0
            msg.angular.z = 2.0

        # D -> Rotate Right
        elif key.lower() == 'd':

            msg.linear.x = 0.0
            msg.angular.z = -2.0

        # Q -> Stop
        elif key.lower() == 'q':

            msg.linear.x = 0.0
            msg.angular.z = 0.0

        else:

            return

        self.cmd_vel_pub.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = MidnightTuner()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node.settings is not None:
            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                node.settings
            )

        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
