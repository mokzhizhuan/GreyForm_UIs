; Auto-generated. Do not edit!


(cl:in-package my_robot_wallinterfaces-msg)


;//! \htmlinclude FileExtractionMessage.msg.html

(cl:defclass <FileExtractionMessage> (roslisp-msg-protocol:ros-message)
  ((stl_data
    :reader stl_data
    :initarg :stl_data
    :type (cl:vector cl:fixnum)
   :initform (cl:make-array 0 :element-type 'cl:fixnum :initial-element 0))
   (excelfile
    :reader excelfile
    :initarg :excelfile
    :type cl:string
    :initform ""))
)

(cl:defclass FileExtractionMessage (<FileExtractionMessage>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <FileExtractionMessage>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'FileExtractionMessage)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name my_robot_wallinterfaces-msg:<FileExtractionMessage> is deprecated: use my_robot_wallinterfaces-msg:FileExtractionMessage instead.")))

(cl:ensure-generic-function 'stl_data-val :lambda-list '(m))
(cl:defmethod stl_data-val ((m <FileExtractionMessage>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:stl_data-val is deprecated.  Use my_robot_wallinterfaces-msg:stl_data instead.")
  (stl_data m))

(cl:ensure-generic-function 'excelfile-val :lambda-list '(m))
(cl:defmethod excelfile-val ((m <FileExtractionMessage>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:excelfile-val is deprecated.  Use my_robot_wallinterfaces-msg:excelfile instead.")
  (excelfile m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <FileExtractionMessage>) ostream)
  "Serializes a message object of type '<FileExtractionMessage>"
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'stl_data))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:write-byte (cl:ldb (cl:byte 8 0) ele) ostream))
   (cl:slot-value msg 'stl_data))
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'excelfile))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'excelfile))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <FileExtractionMessage>) istream)
  "Deserializes a message object of type '<FileExtractionMessage>"
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'stl_data) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'stl_data)))
    (cl:dotimes (i __ros_arr_len)
    (cl:setf (cl:ldb (cl:byte 8 0) (cl:aref vals i)) (cl:read-byte istream)))))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'excelfile) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'excelfile) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<FileExtractionMessage>)))
  "Returns string type for a message object of type '<FileExtractionMessage>"
  "my_robot_wallinterfaces/FileExtractionMessage")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'FileExtractionMessage)))
  "Returns string type for a message object of type 'FileExtractionMessage"
  "my_robot_wallinterfaces/FileExtractionMessage")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<FileExtractionMessage>)))
  "Returns md5sum for a message object of type '<FileExtractionMessage>"
  "81c918b74dbfb64e2d1abc77031a354e")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'FileExtractionMessage)))
  "Returns md5sum for a message object of type 'FileExtractionMessage"
  "81c918b74dbfb64e2d1abc77031a354e")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<FileExtractionMessage>)))
  "Returns full string definition for message of type '<FileExtractionMessage>"
  (cl:format cl:nil "uint8[] stl_data~%string excelfile~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'FileExtractionMessage)))
  "Returns full string definition for message of type 'FileExtractionMessage"
  (cl:format cl:nil "uint8[] stl_data~%string excelfile~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <FileExtractionMessage>))
  (cl:+ 0
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'stl_data) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 1)))
     4 (cl:length (cl:slot-value msg 'excelfile))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <FileExtractionMessage>))
  "Converts a ROS message object to a list"
  (cl:list 'FileExtractionMessage
    (cl:cons ':stl_data (stl_data msg))
    (cl:cons ':excelfile (excelfile msg))
))
