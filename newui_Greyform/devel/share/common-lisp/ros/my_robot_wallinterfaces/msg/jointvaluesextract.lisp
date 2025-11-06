; Auto-generated. Do not edit!


(cl:in-package my_robot_wallinterfaces-msg)


;//! \htmlinclude jointvaluesextract.msg.html

(cl:defclass <jointvaluesextract> (roslisp-msg-protocol:ros-message)
  ((joint_values
    :reader joint_values
    :initarg :joint_values
    :type (cl:vector cl:float)
   :initform (cl:make-array 0 :element-type 'cl:float :initial-element 0.0))
   (placementcoord
    :reader placementcoord
    :initarg :placementcoord
    :type (cl:vector cl:integer)
   :initform (cl:make-array 0 :element-type 'cl:integer :initial-element 0)))
)

(cl:defclass jointvaluesextract (<jointvaluesextract>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <jointvaluesextract>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'jointvaluesextract)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name my_robot_wallinterfaces-msg:<jointvaluesextract> is deprecated: use my_robot_wallinterfaces-msg:jointvaluesextract instead.")))

(cl:ensure-generic-function 'joint_values-val :lambda-list '(m))
(cl:defmethod joint_values-val ((m <jointvaluesextract>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:joint_values-val is deprecated.  Use my_robot_wallinterfaces-msg:joint_values instead.")
  (joint_values m))

(cl:ensure-generic-function 'placementcoord-val :lambda-list '(m))
(cl:defmethod placementcoord-val ((m <jointvaluesextract>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader my_robot_wallinterfaces-msg:placementcoord-val is deprecated.  Use my_robot_wallinterfaces-msg:placementcoord instead.")
  (placementcoord m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <jointvaluesextract>) ostream)
  "Serializes a message object of type '<jointvaluesextract>"
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'joint_values))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-double-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 32) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 40) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 48) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 56) bits) ostream)))
   (cl:slot-value msg 'joint_values))
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'placementcoord))))
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
   (cl:slot-value msg 'placementcoord))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <jointvaluesextract>) istream)
  "Deserializes a message object of type '<jointvaluesextract>"
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'joint_values) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'joint_values)))
    (cl:dotimes (i __ros_arr_len)
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 32) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 40) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 48) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 56) bits) (cl:read-byte istream))
    (cl:setf (cl:aref vals i) (roslisp-utils:decode-double-float-bits bits))))))
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'placementcoord) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'placementcoord)))
    (cl:dotimes (i __ros_arr_len)
    (cl:let ((unsigned 0))
      (cl:setf (cl:ldb (cl:byte 8 0) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) unsigned) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) unsigned) (cl:read-byte istream))
      (cl:setf (cl:aref vals i) (cl:if (cl:< unsigned 2147483648) unsigned (cl:- unsigned 4294967296)))))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<jointvaluesextract>)))
  "Returns string type for a message object of type '<jointvaluesextract>"
  "my_robot_wallinterfaces/jointvaluesextract")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'jointvaluesextract)))
  "Returns string type for a message object of type 'jointvaluesextract"
  "my_robot_wallinterfaces/jointvaluesextract")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<jointvaluesextract>)))
  "Returns md5sum for a message object of type '<jointvaluesextract>"
  "bde6b642b6d906e5d1da1cf7db201cda")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'jointvaluesextract)))
  "Returns md5sum for a message object of type 'jointvaluesextract"
  "bde6b642b6d906e5d1da1cf7db201cda")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<jointvaluesextract>)))
  "Returns full string definition for message of type '<jointvaluesextract>"
  (cl:format cl:nil "float64[] joint_values~%int32[] placementcoord~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'jointvaluesextract)))
  "Returns full string definition for message of type 'jointvaluesextract"
  (cl:format cl:nil "float64[] joint_values~%int32[] placementcoord~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <jointvaluesextract>))
  (cl:+ 0
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'joint_values) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 8)))
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'placementcoord) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <jointvaluesextract>))
  "Converts a ROS message object to a list"
  (cl:list 'jointvaluesextract
    (cl:cons ':joint_values (joint_values msg))
    (cl:cons ':placementcoord (placementcoord msg))
))
