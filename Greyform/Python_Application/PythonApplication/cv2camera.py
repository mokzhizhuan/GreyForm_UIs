#!/usr/bin/env python3

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


def main():
    rospy.init_node("cv2_camera_publisher")
    pub = rospy.Publisher("/camera/image_raw", Image, queue_size=10)
    bridge = CvBridge()

    cap = cv2.VideoCapture(0)  # or your camera index or video stream

    if not cap.isOpened():
        rospy.logerr("Could not open video source")
        return

    rate = rospy.Rate(10)  # 10 Hz

    while not rospy.is_shutdown():
        ret, frame = cap.read()
        if not ret:
            rospy.logwarn("Failed to capture frame")
            continue

        # Convert to ROS Image message
        ros_image = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        pub.publish(ros_image)

        # Optional: Show for debug
        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        rate.sleep()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
