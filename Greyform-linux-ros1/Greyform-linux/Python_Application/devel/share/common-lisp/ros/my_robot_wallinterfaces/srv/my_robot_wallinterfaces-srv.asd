
(cl:in-package :asdf)

(defsystem "my_robot_wallinterfaces-srv"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "SetLed" :depends-on ("_package_SetLed"))
    (:file "_package_SetLed" :depends-on ("_package"))
  ))