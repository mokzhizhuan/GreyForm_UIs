;; Auto-generated. Do not edit!


(when (boundp 'my_robot_wallinterfaces::jointvaluesextract)
  (if (not (find-package "MY_ROBOT_WALLINTERFACES"))
    (make-package "MY_ROBOT_WALLINTERFACES"))
  (shadow 'jointvaluesextract (find-package "MY_ROBOT_WALLINTERFACES")))
(unless (find-package "MY_ROBOT_WALLINTERFACES::JOINTVALUESEXTRACT")
  (make-package "MY_ROBOT_WALLINTERFACES::JOINTVALUESEXTRACT"))

(in-package "ROS")
;;//! \htmlinclude jointvaluesextract.msg.html


(defclass my_robot_wallinterfaces::jointvaluesextract
  :super ros::object
  :slots (_joint_values _placementcoord ))

(defmethod my_robot_wallinterfaces::jointvaluesextract
  (:init
   (&key
    ((:joint_values __joint_values) (make-array 0 :initial-element 0.0 :element-type :float))
    ((:placementcoord __placementcoord) (make-array 0 :initial-element 0 :element-type :integer))
    )
   (send-super :init)
   (setq _joint_values __joint_values)
   (setq _placementcoord __placementcoord)
   self)
  (:joint_values
   (&optional __joint_values)
   (if __joint_values (setq _joint_values __joint_values)) _joint_values)
  (:placementcoord
   (&optional __placementcoord)
   (if __placementcoord (setq _placementcoord __placementcoord)) _placementcoord)
  (:serialization-length
   ()
   (+
    ;; float64[] _joint_values
    (* 8    (length _joint_values)) 4
    ;; int32[] _placementcoord
    (* 4    (length _placementcoord)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float64[] _joint_values
     (write-long (length _joint_values) s)
     (dotimes (i (length _joint_values))
       (sys::poke (elt _joint_values i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; int32[] _placementcoord
     (write-long (length _placementcoord) s)
     (dotimes (i (length _placementcoord))
       (write-long (elt _placementcoord i) s)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float64[] _joint_values
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _joint_values (instantiate float-vector n))
     (dotimes (i n)
     (setf (elt _joint_values i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     ))
   ;; int32[] _placementcoord
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _placementcoord (instantiate integer-vector n))
     (dotimes (i n)
     (setf (elt _placementcoord i) (sys::peek buf ptr- :integer)) (incf ptr- 4)
     ))
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::jointvaluesextract :md5sum-) "bde6b642b6d906e5d1da1cf7db201cda")
(setf (get my_robot_wallinterfaces::jointvaluesextract :datatype-) "my_robot_wallinterfaces/jointvaluesextract")
(setf (get my_robot_wallinterfaces::jointvaluesextract :definition-)
      "float64[] joint_values
int32[] placementcoord
")



(provide :my_robot_wallinterfaces/jointvaluesextract "bde6b642b6d906e5d1da1cf7db201cda")


