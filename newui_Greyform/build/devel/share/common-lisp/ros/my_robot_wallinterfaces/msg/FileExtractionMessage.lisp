; Auto-generated. Do not edit!


(cl:in-package my_robot_wallinterfaces-msg)


;//! \htmlinclude FileExtractionMessage.msg.html

(cl:defclass <FileExtractionMessage> (roslisp-msg-protocol:ros-message)
  ((directory
    :reader directory
    :initarg :directory
    :type cl:string
    :initform "")
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

(cl:ensure-generic-function 'directory-val :lambda-list '(m))
(cl:defmethod directory-val ((m <FileExtractionMessage>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:directory-val is deprecated.  Use my_robot_wallinterfaces-msg:directory instead.")
  (directory m))

(cl:ensure-generic-function 'excelfile-val :lambda-list '(m))
(cl:defmethod excelfile-val ((m <FileExtractionMessage>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:excelfile-val is deprecated.  Use my_robot_wallinterfaces-msg:excelfile instead.")
  (excelfile m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <FileExtractionMessage>) ostream)
  "Serializes a message object of type '<FileExtractionMessage>"
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'directory))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'directory))
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'excelfile))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'excelfile))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <FileExtractionMessage>) istream)
  "Deserializes a message object of type '<FileExtractionMessage>"
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'directory) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'directory) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
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
  "d217064ce75170f28ac78f629dbe4223")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'FileExtractionMessage)))
  "Returns md5sum for a message object of type 'FileExtractionMessage"
  "d217064ce75170f28ac78f629dbe4223")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<FileExtractionMessage>)))
  "Returns full string definition for message of type '<FileExtractionMessage>"
  (cl:format cl:nil "string directory~%string excelfile~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'FileExtractionMessage)))
  "Returns full string definition for message of type 'FileExtractionMessage"
  (cl:format cl:nil "string directory~%string excelfile~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <FileExtractionMessage>))
  (cl:+ 0
     4 (cl:length (cl:slot-value msg 'directory))
     4 (cl:length (cl:slot-value msg 'excelfile))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <FileExtractionMessage>))
  "Converts a ROS message object to a list"
  (cl:list 'FileExtractionMessage
    (cl:cons ':directory (directory msg))
    (cl:cons ':excelfile (excelfile msg))
))
