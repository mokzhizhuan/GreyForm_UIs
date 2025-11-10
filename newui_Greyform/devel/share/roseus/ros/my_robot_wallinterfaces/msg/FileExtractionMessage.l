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
  :slots (_directory _excelfile ))

(defmethod my_robot_wallinterfaces::FileExtractionMessage
  (:init
   (&key
    ((:directory __directory) "")
    ((:excelfile __excelfile) "")
    )
   (send-super :init)
   (setq _directory (string __directory))
   (setq _excelfile (string __excelfile))
   self)
  (:directory
   (&optional __directory)
   (if __directory (setq _directory __directory)) _directory)
  (:excelfile
   (&optional __excelfile)
   (if __excelfile (setq _excelfile __excelfile)) _excelfile)
  (:serialization-length
   ()
   (+
    ;; string _directory
    4 (length _directory)
    ;; string _excelfile
    4 (length _excelfile)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _directory
       (write-long (length _directory) s) (princ _directory s)
     ;; string _excelfile
       (write-long (length _excelfile) s) (princ _excelfile s)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _directory
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _directory (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; string _excelfile
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _excelfile (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;;
   self)
  )

(setf (get my_robot_wallinterfaces::FileExtractionMessage :md5sum-) "d217064ce75170f28ac78f629dbe4223")
(setf (get my_robot_wallinterfaces::FileExtractionMessage :datatype-) "my_robot_wallinterfaces/FileExtractionMessage")
(setf (get my_robot_wallinterfaces::FileExtractionMessage :definition-)
      "string directory
string excelfile

")



(provide :my_robot_wallinterfaces/FileExtractionMessage "d217064ce75170f28ac78f629dbe4223")


