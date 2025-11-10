
(cl:in-package :asdf)

(defsystem "my_robot_wallinterfaces-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "FileExtractionMessage" :depends-on ("_package_FileExtractionMessage"))
    (:file "_package_FileExtractionMessage" :depends-on ("_package"))
    (:file "SelectionWall" :depends-on ("_package_SelectionWall"))
    (:file "_package_SelectionWall" :depends-on ("_package"))
  ))