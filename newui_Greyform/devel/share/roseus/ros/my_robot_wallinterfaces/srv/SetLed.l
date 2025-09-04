;; Auto-generated. Do not edit!


(when (boundp 'my_robot_wallinterfaces::SetLed)
  (if (not (find-package "MY_ROBOT_WALLINTERFACES"))
    (make-package "MY_ROBOT_WALLINTERFACES"))
  (shadow 'SetLed (find-package "MY_ROBOT_WALLINTERFACES")))
(unless (find-package "MY_ROBOT_WALLINTERFACES::SETLED")
  (make-package "MY_ROBOT_WALLINTERFACES::SETLED"))
(unless (find-package "MY_ROBOT_WALLINTERFACES::SETLEDREQUEST")
  (make-package "MY_ROBOT_WALLINTERFACES::SETLEDREQUEST"))
(unless (find-package "MY_ROBOT_WALLINTERFACES::SETLEDRESPONSE")
  (make-package "MY_ROBOT_WALLINTERFACES::SETLEDRESPONSE"))

(in-package "ROS")





(defclass my_robot_wallinterfaces::SetLedRequest
  :super ros::object
  :slots (_color ))

(defmethod my_robot_wallinterfaces::SetLedRequest
  (:init
   (&key
    ((:color __color) "")
    )
   (send-super :init)
   (setq _color (string __color))
   self)
  (:color
   (&optional __color)
   (if __color (setq _color __color)) _color)
  (:serialization-length
   ()
   (+
    ;; string _color
    4 (length _color)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _color
       (write-long (length _color) s) (princ _color s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _color
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _color (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(defclass my_robot_wallinterfaces::SetLedResponse
  :super ros::object
  :slots (_success ))

(defmethod my_robot_wallinterfaces::SetLedResponse
  (:init
   (&key
    ((:success __success) nil)
    )
   (send-super :init)
   (setq _success __success)
   self)
  (:success
   (&optional (__success :null))
   (if (not (eq __success :null)) (setq _success __success)) _success)
  (:serialization-length
   ()
   (+
    ;; bool _success
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _success
       (if _success (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _success
     (setq _success (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(defclass my_robot_wallinterfaces::SetLed
  :super ros::object
  :slots ())

(setf (get my_robot_wallinterfaces::SetLed :md5sum-) "c392f71e5178d9c3ca2a5905cf219411")
(setf (get my_robot_wallinterfaces::SetLed :datatype-) "my_robot_wallinterfaces/SetLed")
(setf (get my_robot_wallinterfaces::SetLed :request) my_robot_wallinterfaces::SetLedRequest)
(setf (get my_robot_wallinterfaces::SetLed :response) my_robot_wallinterfaces::SetLedResponse)

(defmethod my_robot_wallinterfaces::SetLedRequest
  (:response () (instance my_robot_wallinterfaces::SetLedResponse :init)))

(setf (get my_robot_wallinterfaces::SetLedRequest :md5sum-) "c392f71e5178d9c3ca2a5905cf219411")
(setf (get my_robot_wallinterfaces::SetLedRequest :datatype-) "my_robot_wallinterfaces/SetLedRequest")
(setf (get my_robot_wallinterfaces::SetLedRequest :definition-)
      "string color
---
bool success

")

(setf (get my_robot_wallinterfaces::SetLedResponse :md5sum-) "c392f71e5178d9c3ca2a5905cf219411")
(setf (get my_robot_wallinterfaces::SetLedResponse :datatype-) "my_robot_wallinterfaces/SetLedResponse")
(setf (get my_robot_wallinterfaces::SetLedResponse :definition-)
      "string color
---
bool success

")



(provide :my_robot_wallinterfaces/SetLed "c392f71e5178d9c3ca2a5905cf219411")


