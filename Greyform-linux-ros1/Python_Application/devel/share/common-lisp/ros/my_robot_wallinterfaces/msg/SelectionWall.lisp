; Auto-generated. Do not edit!


(cl:in-package my_robot_wallinterfaces-msg)


;//! \htmlinclude SelectionWall.msg.html

(cl:defclass <SelectionWall> (roslisp-msg-protocol:ros-message)
  ((wallselection
    :reader wallselection
    :initarg :wallselection
    :type cl:integer
    :initform 0)
   (typeselection
    :reader typeselection
    :initarg :typeselection
    :type cl:string
    :initform "")
   (sectionselection
    :reader sectionselection
    :initarg :sectionselection
    :type cl:integer
    :initform 0)
   (picked_position
    :reader picked_position
    :initarg :picked_position
    :type (cl:vector cl:integer)
   :initform (cl:make-array 0 :element-type 'cl:integer :initial-element 0))
   (default_position
    :reader default_position
    :initarg :default_position
    :type (cl:vector cl:integer)
   :initform (cl:make-array 0 :element-type 'cl:integer :initial-element 0)))
)

(cl:defclass SelectionWall (<SelectionWall>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <SelectionWall>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'SelectionWall)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name my_robot_wallinterfaces-msg:<SelectionWall> is deprecated: use my_robot_wallinterfaces-msg:SelectionWall instead.")))

(cl:ensure-generic-function 'wallselection-val :lambda-list '(m))
(cl:defmethod wallselection-val ((m <SelectionWall>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:wallselection-val is deprecated.  Use my_robot_wallinterfaces-msg:wallselection instead.")
  (wallselection m))

(cl:ensure-generic-function 'typeselection-val :lambda-list '(m))
(cl:defmethod typeselection-val ((m <SelectionWall>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:typeselection-val is deprecated.  Use my_robot_wallinterfaces-msg:typeselection instead.")
  (typeselection m))

(cl:ensure-generic-function 'sectionselection-val :lambda-list '(m))
(cl:defmethod sectionselection-val ((m <SelectionWall>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:sectionselection-val is deprecated.  Use my_robot_wallinterfaces-msg:sectionselection instead.")
  (sectionselection m))

(cl:ensure-generic-function 'picked_position-val :lambda-list '(m))
(cl:defmethod picked_position-val ((m <SelectionWall>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:picked_position-val is deprecated.  Use my_robot_wallinterfaces-msg:picked_position instead.")
  (picked_position m))

(cl:ensure-generic-function 'default_position-val :lambda-list '(m))
(cl:defmethod default_position-val ((m <SelectionWall>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:default_position-val is deprecated.  Use my_robot_wallinterfaces-msg:default_position instead.")
  (default_position m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <SelectionWall>) ostream)
  "Serializes a message object of type '<SelectionWall>"
  (cl:let* ((signed (cl:slot-value msg 'wallselection)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'typeselection))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'typeselection))
  (cl:let* ((signed (cl:slot-value msg 'sectionselection)) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    )
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'picked_position))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let* ((signed ele) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    ))
   (cl:slot-value msg 'picked_position))
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'default_position))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let* ((signed ele) (unsigned (cl:if (cl:< signed 0) (cl:+ signed 4294967296) signed)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) unsigned) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) unsigned) ostream)
    ))
   (cl:slot-value msg 'default_position))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <SelectionWall>) istream)
  "Deserializes a message object of type '<SelectionWall>"
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'wallselection) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'typeselection) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'typeselection) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'sectionselection) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296))))
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'picked_position) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'picked_position)))
    (cl:dotimes (i __ros_arr_len)
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:aref vals i) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296)))))))
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'default_position) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'default_position)))
    (cl:dotimes (i __ros_arr_len)
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:aref vals i) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296)))))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<SelectionWall>)))
  "Returns string type for a message object of type '<SelectionWall>"
  "my_robot_wallinterfaces/SelectionWall")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'SelectionWall)))
  "Returns string type for a message object of type 'SelectionWall"
  "my_robot_wallinterfaces/SelectionWall")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<SelectionWall>)))
  "Returns md5sum for a message object of type '<SelectionWall>"
  "58c6387955db224451fe1a297bbab86a")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'SelectionWall)))
  "Returns md5sum for a message object of type 'SelectionWall"
  "58c6387955db224451fe1a297bbab86a")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<SelectionWall>)))
  "Returns full string definition for message of type '<SelectionWall>"
  (cl:format cl:nil "int32 wallselection~%string typeselection~%int32 sectionselection~%int32[] picked_position~%int32[] default_position~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'SelectionWall)))
  "Returns full string definition for message of type 'SelectionWall"
  (cl:format cl:nil "int32 wallselection~%string typeselection~%int32 sectionselection~%int32[] picked_position~%int32[] default_position~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <SelectionWall>))
  (cl:+ 0
     4
     4 (cl:length (cl:slot-value msg 'typeselection))
     4
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'picked_position) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'default_position) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <SelectionWall>))
  "Converts a ROS message object to a list"
  (cl:list 'SelectionWall
    (cl:cons ':wallselection (wallselection msg))
    (cl:cons ':typeselection (typeselection msg))
    (cl:cons ':sectionselection (sectionselection msg))
    (cl:cons ':picked_position (picked_position msg))
    (cl:cons ':default_position (default_position msg))
))
