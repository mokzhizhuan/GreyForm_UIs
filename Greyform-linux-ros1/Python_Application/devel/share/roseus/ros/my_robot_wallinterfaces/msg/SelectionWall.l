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
  :slots (_wallselection _typeselection _sectionselection ))

(defmethod my_robot_wallinterfaces::SelectionWall
  (:init
   (&key
    ((:wallselection __wallselection) 0)
    ((:typeselection __typeselection) "")
    ((:sectionselection __sectionselection) 0)
    )
   (send-super :init)
   (setq _wallselection (round __wallselection))
   (setq _typeselection (string __typeselection))
   (setq _sectionselection (round __sectionselection))
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
  (:serialization-length
   ()
   (+
    ;; int32 _wallselection
    4
    ;; string _typeselection
    4 (length _typeselection)
    ;; int32 _sectionselection
    4
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
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::SelectionWall :md5sum-) "2878ec5f8dda738f8c5cf606a52c84a0")
(setf (get my_robot_wallinterfaces::SelectionWall :datatype-) "my_robot_wallinterfaces/SelectionWall")
(setf (get my_robot_wallinterfaces::SelectionWall :definition-)
      "int32 wallselection
string typeselection
int32 sectionselection
")



(provide :my_robot_wallinterfaces/SelectionWall "2878ec5f8dda738f8c5cf606a52c84a0")


