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
  :slots (_wallselection _typeselection _sectionselection _picked_position _default_position ))

(defmethod my_robot_wallinterfaces::SelectionWall
  (:init
   (&key
    ((:wallselection __wallselection) "")
    ((:typeselection __typeselection) "")
    ((:sectionselection __sectionselection) 0)
    ((:picked_position __picked_position) (make-array 0 :initial-element 0 :element-type :integer))
    ((:default_position __default_position) (make-array 0 :initial-element 0 :element-type :integer))
    )
   (send-super :init)
   (setq _wallselection (string __wallselection))
   (setq _typeselection (string __typeselection))
   (setq _sectionselection (round __sectionselection))
   (setq _picked_position __picked_position)
   (setq _default_position __default_position)
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
  (:default_position
   (&optional __default_position)
   (if __default_position (setq _default_position __default_position)) _default_position)
  (:serialization-length
   ()
   (+
    ;; string _wallselection
    4 (length _wallselection)
    ;; string _typeselection
    4 (length _typeselection)
    ;; int32 _sectionselection
    4
    ;; int32[] _picked_position
    (* 4    (length _picked_position)) 4
    ;; int32[] _default_position
    (* 4    (length _default_position)) 4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _wallselection
       (write-long (length _wallselection) s) (princ _wallselection s)
     ;; string _typeselection
       (write-long (length _typeselection) s) (princ _typeselection s)
     ;; int32 _sectionselection
       (write-long _sectionselection s)
     ;; int32[] _picked_position
     (write-long (length _picked_position) s)
     (dotimes (i (length _picked_position))
       (write-long (elt _picked_position i) s)
       )
     ;; int32[] _default_position
     (write-long (length _default_position) s)
     (dotimes (i (length _default_position))
       (write-long (elt _default_position i) s)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _wallselection
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _wallselection (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
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
   ;; int32[] _default_position
   (let (n)
     (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4)
     (setq _default_position (instantiate integer-vector n))
     (dotimes (i n)
     (setf (elt _default_position i) (sys::peek buf ptr- :integer)) (incf ptr- 4)
     ))
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::SelectionWall :md5sum-) "3018aa4e69906a564df217c351a9673e")
(setf (get my_robot_wallinterfaces::SelectionWall :datatype-) "my_robot_wallinterfaces/SelectionWall")
(setf (get my_robot_wallinterfaces::SelectionWall :definition-)
      "string wallselection
string typeselection
int32 sectionselection
int32[] picked_position
int32[] default_position

")



(provide :my_robot_wallinterfaces/SelectionWall "3018aa4e69906a564df217c351a9673e")


