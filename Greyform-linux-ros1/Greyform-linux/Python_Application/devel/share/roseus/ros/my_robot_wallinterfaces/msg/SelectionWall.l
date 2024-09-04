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
  :slots (_wallselection _typeselection _sectionselection _picked_position ))

(defmethod my_robot_wallinterfaces::SelectionWall
  (:init
   (&key
    ((:wallselection __wallselection) 0)
    ((:typeselection __typeselection) "")
    ((:sectionselection __sectionselection) 0)
    ((:picked_position __picked_position) (make-array 0 :initial-element 0 :element-type :integer))
    )
   (send-super :init)
   (setq _wallselection (round __wallselection))
   (setq _typeselection (string __typeselection))
   (setq _sectionselection (round __sectionselection))
   (setq _picked_position __picked_position)
   self)
  (:wallselection
   (&optional __wallselection)
   (if __wallselection (setq _wallselection __wallselection)) _wallselection)
  (:typeselection
   (&optional __typeselection)
   (if __typeselection (setq _typeselection __typeselection)) _typeselection)
  (:sectionselection
   (&optional __sectionselection)
   (if __sectionselection (setq _sectionselection __sectionselection)) _sectionselection)
  (:picked_position
   (&optional __picked_position)
   (if __picked_position (setq _picked_position __picked_position)) _picked_position)
  (:serialization-length
   ()
   (+
    ;; int32 _wallselection
    4
    ;; string _typeselection
    4 (length _typeselection)
    ;; int32 _sectionselection
    4
    ;; int32[] _picked_position
    (* 4    (length _picked_position)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; int32 _wallselection
       (write-long _wallselection s)
     ;; string _typeselection
       (write-long (length _typeselection) s) (princ _typeselection s)
     ;; int32 _sectionselection
       (write-long _sectionselection s)
     ;; int32[] _picked_position
     (write-long (length _picked_position) s)
     (dotimes (i (length _picked_position))
       (write-long (elt _picked_position i) s)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; int32 _wallselection
     (setq _wallselection (sys::peek buf ptr- :integer)) (incf ptr- 4)
   ;; string _typeselection
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _typeselection (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; int32 _sectionselection
     (setq _sectionselection (sys::peek buf ptr- :integer)) (incf ptr- 4)
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

(setf (get my_robot_wallinterfaces::SelectionWall :md5sum-) "f6985e46a2e326f422d9f77fb3681bba")
(setf (get my_robot_wallinterfaces::SelectionWall :datatype-) "my_robot_wallinterfaces/SelectionWall")
(setf (get my_robot_wallinterfaces::SelectionWall :definition-)
      "int32 wallselection
string typeselection
int32 sectionselection
int32[] picked_position
")



(provide :my_robot_wallinterfaces/SelectionWall "f6985e46a2e326f422d9f77fb3681bba")


