;; Auto-generated. Do not edit!


(when (boundp 'my_robot_wallinterfaces::FileExtractionMessage)
  (if (not (find-package "MY_ROBOT_WALLINTERFACES"))
    (make-package "MY_ROBOT_WALLINTERFACES"))
  (shadow 'FileExtractionMessage (find-package "MY_ROBOT_WALLINTERFACES")))
(unless (find-package "MY_ROBOT_WALLINTERFACES::FILEEXTRACTIONMESSAGE")
  (make-package "MY_ROBOT_WALLINTERFACES::FILEEXTRACTIONMESSAGE"))

(in-package "ROS")
;;//! \htmlinclude FileExtractionMessage.msg.html


(defclass my_robot_wallinterfaces::FileExtractionMessage
  :super ros::object
  :slots (_excelfile _stl_data _status ))

(defmethod my_robot_wallinterfaces::FileExtractionMessage
  (:init
   (&key
    ((:excelfile __excelfile) "")
    ((:stl_data __stl_data) (make-array 0 :initial-element 0 :element-type :char))
    ((:status __status) "")
    )
   (send-super :init)
   (setq _excelfile (string __excelfile))
   (setq _stl_data __stl_data)
   (setq _status (string __status))
   self)
  (:excelfile
   (&optional __excelfile)
   (if __excelfile (setq _excelfile __excelfile)) _excelfile)
  (:stl_data
   (&optional __stl_data)
   (if __stl_data (setq _stl_data __stl_data)) _stl_data)
  (:status
   (&optional __status)
   (if __status (setq _status __status)) _status)
  (:serialization-length
   ()
   (+
    ;; string _excelfile
    4 (length _excelfile)
    ;; uint8[] _stl_data
    (* 1    (length _stl_data)) 4
    ;; string _status
    4 (length _status)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _excelfile
       (write-long (length _excelfile) s) (princ _excelfile s)
     ;; uint8[] _stl_data
     (write-long (length _stl_data) s)
     (princ _stl_data s)
     ;; string _status
       (write-long (length _status) s) (princ _status s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _excelfile
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _excelfile (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; uint8[] _stl_data
   (let ((n (sys::peek buf ptr- :integer))) (incf ptr- 4)
     (setq _stl_data (make-array n :element-type :char))
     (replace _stl_data buf :start2 ptr-) (incf ptr- n))
   ;; string _status
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _status (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::FileExtractionMessage :md5sum-) "be99b8b69cd2a117a0a8d177509a0dff")
(setf (get my_robot_wallinterfaces::FileExtractionMessage :datatype-) "my_robot_wallinterfaces/FileExtractionMessage")
(setf (get my_robot_wallinterfaces::FileExtractionMessage :definition-)
      "string excelfile
uint8[] stl_data
string status
")



(provide :my_robot_wallinterfaces/FileExtractionMessage "be99b8b69cd2a117a0a8d177509a0dff")


