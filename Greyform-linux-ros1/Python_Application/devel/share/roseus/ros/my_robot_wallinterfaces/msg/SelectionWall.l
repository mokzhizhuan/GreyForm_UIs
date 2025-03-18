;; Auto-generated. Do not edit!


(when (boundp 'my_robot_wallinterfaces::SelectionWall)
  (if (not (find-package "MY_ROBOT_WALLINTERFACES"))
    (make-package "MY_ROBOT_WALLINTERFACES"))
  (shadow 'SelectionWall (find-package "MY_ROBOT_WALLINTERFACES")))
(unless (find-package "MY_ROBOT_WALLINTERFACES::SELECTIONWALL")
  (make-package "MY_ROBOT_WALLINTERFACES::SELECTIONWALL"))

(in-package "ROS")
;;//! \htmlinclude SelectionWall.msg.html


(defclass my_robot_wallinterfaces::SelectionWall
  :super ros::object
  :slots (_wallselection _typeselection _picked_position ))

(defmethod my_robot_wallinterfaces::SelectionWall
  (:init
   (&key
    ((:wallselection __wallselection) "")
    ((:typeselection __typeselection) "")
    ((:picked_position __picked_position) (make-array 0 :initial-element 0 :element-type :integer))
    )
   (send-super :init)
   (setq _wallselection (string __wallselection))
   (setq _typeselection (string __typeselection))
   (setq _picked_position __picked_position)
   self)
  (:wallselection
   (&optional __wallselection)
   (if __wallselection (setq _wallselection __wallselection)) _wallselection)
  (:typeselection
   (&optional __typeselection)
   (if __typeselection (setq _typeselection __typeselection)) _typeselection)
  (:picked_position
   (&optional __picked_position)
   (if __picked_position (setq _picked_position __picked_position)) _picked_position)
  (:serialization-length
   ()
   (+
    ;; string _wallselection
    4 (length _wallselection)
    ;; string _typeselection
    4 (length _typeselection)
    ;; int32[] _picked_position
    (* 4    (length _picked_position)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _wallselection
       (write-long (length _wallselection) s) (princ _wallselection s)
     ;; string _typeselection
       (write-long (length _typeselection) s) (princ _typeselection s)
     ;; int32[] _picked_position
     (write-long (length _picked_position) s)
     (dotimes (i (length _picked_position))
       (write-long (elt _picked_position i) s)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _wallselection
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _wallselection (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; string _typeselection
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _typeselection (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; int32[] _picked_position
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _picked_position (instantiate integer-vector n))
     (dotimes (i n)
     (setf (elt _picked_position i) (sys::peek buf ptr- :integer)) (incf ptr- 4)
     ))
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::SelectionWall :md5sum-) "cec1748b8474fc5db64b113998095031")
(setf (get my_robot_wallinterfaces::SelectionWall :datatype-) "my_robot_wallinterfaces/SelectionWall")
(setf (get my_robot_wallinterfaces::SelectionWall :definition-)
      "string wallselection
string typeselection
int32[] picked_position

")



(provide :my_robot_wallinterfaces/SelectionWall "cec1748b8474fc5db64b113998095031")


