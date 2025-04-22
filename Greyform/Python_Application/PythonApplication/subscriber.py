import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


def image_callback(msg):
    bridge = CvBridge()
    frame = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    # Your logic using the frame
    cv2.imshow("Received", frame)
    cv2.waitKey(1)


rospy.init_node("image_subscriber")
rospy.Subscriber("/camera/image_raw", Image, image_callback)
rospy.spin()
