import sys
if sys.prefix == '/home/winsys/ros2_ws/src/Greyform-linux/Python_Application/env':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/winsys/ros2_ws/src/Greyform-linux/Python_Application/install/my-test-package'
