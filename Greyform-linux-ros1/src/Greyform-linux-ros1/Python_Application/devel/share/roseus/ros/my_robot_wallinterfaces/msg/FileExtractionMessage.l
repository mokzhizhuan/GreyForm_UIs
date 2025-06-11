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
  :slots (_stl_data _excelfile ))

(defmethod my_robot_wallinterfaces::FileExtractionMessage
  (:init
   (&key
    ((:stl_data __stl_data) (make-array 0 :initial-element 0 :element-type :char))
    ((:excelfile __excelfile) "")
    )
   (send-super :init)
   (setq _stl_data __stl_data)
   (setq _excelfile (string __excelfile))
   self)
  (:stl_data
   (&optional __stl_data)
   (if __stl_data (setq _stl_data __stl_data)) _stl_data)
  (:excelfile
   (&optional __excelfile)
   (if __excelfile (setq _excelfile __excelfile)) _excelfile)
  (:serialization-length
   ()
   (+
    ;; uint8[] _stl_data
    (* 1    (length _stl_data)) 4
    ;; string _excelfile
    4 (length _excelfile)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; uint8[] _stl_data
     (write-long (length _stl_data) s)
     (princ _stl_data s)
     ;; string _excelfile
       (write-long (length _excelfile) s) (princ _excelfile s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; uint8[] _stl_data
   (let ((n (sys::peek buf ptr- :integer))) (incf ptr- 4)
     (setq _stl_data (make-array n :element-type :char))
     (replace _stl_data buf :start2 ptr-) (incf ptr- n))
   ;; string _excelfile
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _excelfile (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::FileExtractionMessage :md5sum-) "81c918b74dbfb64e2d1abc77031a354e")
(setf (get my_robot_wallinterfaces::FileExtractionMessage :datatype-) "my_robot_wallinterfaces/FileExtractionMessage")
(setf (get my_robot_wallinterfaces::FileExtractionMessage :definition-)
      "uint8[] stl_data
string excelfile

")



(provide :my_robot_wallinterfaces/FileExtractionMessage "81c918b74dbfb64e2d1abc77031a354e")


