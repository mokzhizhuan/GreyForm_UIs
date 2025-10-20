# talker_node.py
"""
Talker (publisher) utilities for the wall-processing workflow.

This module provides TalkerNode, a lightweight publisher helper that:
- publishes FileExtractionMessage messages containing STL bytes and an Excel path,
- publishes SelectionWall messages to request processing of a wall,
- publishes UI status messages on /ui/wall_started, /ui/wall_done and /ui/all_done.

The class does not subscribe to any topics or run a spin loop; it is intended
to be instantiated by a controller/UI component which calls its publish_* methods.
"""
import rospy
from std_msgs.msg import String, Int32, Bool
from my_robot_wallinterfaces.msg import FileExtractionMessage, SelectionWall

class TalkerNode:
    def __init__(self):
        """
        Initialize the TalkerNode.

        - Ensures a ROS node is initialized (calls rospy.init_node if necessary).
        - Creates publishers for:
          - /file_extraction_topic : FileExtractionMessage
          - /selection_wall_topic   : SelectionWall
          - /ui/wall_started        : String (latched)
          - /ui/wall_done           : String (latched)
          - /ui/all_done            : Bool   (latched)

        Notes:
        - anonymous=True is used when initializing the node so multiple instances
          can run without name collisions.
        - disable_signals=True is set to avoid rospy installing a SIGINT handler,
          which is useful if this class is used inside a larger application that
          manages signals itself.
        """
        if not rospy.core.is_initialized():
            rospy.init_node("talker_node", anonymous=True, disable_signals=True)
        self.file_pub = rospy.Publisher("/file_extraction_topic", FileExtractionMessage, queue_size=10)
        self.sel_pub  = rospy.Publisher("/selection_wall_topic",   SelectionWall,        queue_size=10)
        self.ui_wall_started_pub = rospy.Publisher("/ui/wall_started", String, queue_size=10, latch=True)
        self.ui_wall_done_pub    = rospy.Publisher("/ui/wall_done",    String, queue_size=10, latch=True)
        self.ui_all_done_pub     = rospy.Publisher("/ui/all_done",     Bool,   queue_size=10, latch=True)

    def _wait_for_subscribers(self, pubs, timeout=1.0):
        """
        Wait until the given publishers have at least one subscriber or until timeout.

        This helper polls p.get_num_connections() for each publisher and sleeps in
        short increments until either all publishers have at least one connection
        or the timeout elapses.

        Parameters:
        - pubs: iterable of rospy.Publisher objects to check for subscribers.
        - timeout: float seconds to wait before returning. If 0 or negative, the
                   loop will still check at least once and then return.

        Returns:
        - None (returns early if subscribers are present; otherwise exits after timeout).

        Side effects:
        - Sleeps using rospy.sleep; returns earlier if rospy.is_shutdown() becomes True.
        """
        start = rospy.Time.now().to_sec()
        while not rospy.is_shutdown() and (rospy.Time.now().to_sec() - start) < timeout:
            if all(p.get_num_connections() > 0 for p in pubs):
                return
            rospy.sleep(0.05)

    def publish_file_message(self, stl_file_path: str, excel_path: str):
        """
        Publish a FileExtractionMessage containing the binary STL data and an Excel path.

        Parameters:
        - stl_file_path: path to an STL (or other binary) file to be embedded in the message.
        - excel_path: path (string) to the Excel file that the listener should read/write.

        Behavior:
        - Reads the entire file at stl_file_path in binary mode and places the bytes into
          msg.stl_data. Sets msg.excelfile to excel_path and publishes the message on
          /file_extraction_topic.

        Notes / Exceptions:
        - If the file does not exist or cannot be opened, this method will raise the
          underlying IOError/Exception (no internal try/except). Consider catching errors
          at the caller if you need more graceful handling.
        - Embedding full file bytes into a ROS message can be heavy for large files.
        """
        with open(stl_file_path, "rb") as f:
            ifc_bytes = f.read()
        msg = FileExtractionMessage()
        msg.stl_data  = ifc_bytes
        msg.excelfile = excel_path
        self.file_pub.publish(msg)

    def publish_selection_message(self, wallselection, picked_position, typeselection):
        """
        Publish a SelectionWall message to request processing of a selected wall.

        Workflow:
        - Publish a /ui/wall_started String message (wrapped in try/except for robustness).
        - Wait briefly for subscribers on the selection publisher to connect.
        - Build a SelectionWall message and publish it on /selection_wall_topic.

        Parameters:
        - wallselection: object convertible to str; identifies the wall (e.g., '1', 'F').
        - picked_position: iterable of values that can be cast to int for picked_position field;
                           if conversion fails, an empty list will be used.
        - typeselection: object convertible to str; optional type or sheet name metadata.

        Message fields set:
        - msg.wallselection   : str(wallselection)
        - msg.typeselection   : str(typeselection)
        - msg.sectionselection: set to 0 where supported (try/except tolerant)
        - msg.picked_position : list of ints parsed from picked_position where possible
        - msg.default_position: set to [] where supported (try/except tolerant)

        Notes:
        - The method is robust to small schema differences (uses try/except when setting
          optional fields), so it will not fail if SelectionWall does not include a specific
          optional field.
        """
        lab = str(wallselection)
        try:
            self.ui_wall_started_pub.publish(String(data=lab))
        except Exception:
            pass
        self._wait_for_subscribers([self.sel_pub], timeout=0.5)
        msg = SelectionWall()
        msg.wallselection = lab
        msg.typeselection = str(typeselection)
        try:    msg.sectionselection = 0
        except: pass
        try:    msg.picked_position = [int(v) for v in picked_position]
        except: msg.picked_position = []
        try:    msg.default_position = []
        except: pass
        self.sel_pub.publish(msg)

    def publish_wall_done(self, wallselection):
        """
        Publish a /ui/wall_done String indicating that the given wall is completed.

        Parameters:
        - wallselection: object convertible to str that identifies the completed wall.

        Notes:
        - The publish is wrapped in try/except to avoid raising if publisher is not available.
        - This topic is latched, so late subscribers will receive the last published value.
        """
        lab = str(wallselection)
        try:
            self.ui_wall_done_pub.publish(String(data=lab))
        except Exception:
            pass

    def publish_all_done(self, is_done: bool):
        """
        Publish a /ui/all_done Bool indicating whether all walls are done.

        Parameters:
        - is_done: boolean-like value; will be coerced to bool and published.

        Notes:
        - The publish is wrapped in try/except to avoid raising if publisher is not available.
        - This topic is latched so late subscribers will receive the final state.
        """
        try:
            self.ui_all_done_pub.publish(Bool(data=bool(is_done)))
        except Exception:
            pass
