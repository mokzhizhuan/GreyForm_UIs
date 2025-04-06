import rclpy
import threading
from rclpy.node import Node
from my_robot_wallinterfaces.msg import (
    SelectionWall,
    FileExtractionMessage,
)
import pandas as pd


# listenerNode
class ListenerNode(Node):
    def __init__(self):
        # starting initialize
        super().__init__("listener_node")
        self.file_subscription_ = self.create_subscription(
            FileExtractionMessage,  # Correct message type
            "file_extraction_topic",  # Correct topic
            self.file_listener_callback,
            10,
        )
        self.selection_subscription_ = self.create_subscription(
            SelectionWall,  # Correct message type
            "selection_wall_topic",  # Correct topic
            self.selection_listener_callback,
            10,
        )
        self.file_callback = None
        self.selection_callback = None
        self.wallselection = None
        self.typeselection = None
        self.sectionselection = None
        self.picked_position = []
        self.message = ""
        self.spacing = "\n"
        self.title = "Listener Node"
        self.active_dialog = None
        self.log_buffer = []


    def file_listener_callback(self, msg):
        """ Process STL and Excel file messages but DO NOT show logs yet """
        try:
            # Process the Excel file
            self.process_excel_data(msg.excelfile)
        except Exception as e:
            self.log_buffer.append(f"❌ Error processing STL file: {e}")

    def selection_listener_callback(self, msg):
        """ Process selection messages but DO NOT show logs yet """
        self.wallselection = msg.wallselection
        self.typeselection = msg.typeselection
        self.picked_position = msg.picked_position

    def process_excel_data(self, excel_filepath):
        """ Process Excel data and update all matching walls and stages """

        # Load the entire Excel file
        self.excelitems = pd.read_excel(excel_filepath, sheet_name=None)
        processed_data = {}

        for stage, data in self.excelitems.items():
            df = pd.DataFrame(data)

            # ✅ Convert all values to string to prevent mismatches
            df["Wall Number"] = df["Wall Number"].astype(str)

            for index, row in df.iterrows():
                df_wall_number = str(df.at[index, "Wall Number"])
                df_stage = stage

                # Debug prints to ensure correct matching
                print(f"Wall Number from Excel: {df_wall_number}")
                print(f"Wall Selection: {self.wallselection}")
                print(f"Stage from Excel: {df_stage}")
                print(f"Type Selection: {self.typeselection}")

                # ✅ Ensure all rows that match `self.wallselection` and `self.typeselection` are updated
                if str(df_wall_number) == str(self.wallselection) and str(df_stage) == str(self.typeselection):
                    print(f"✅ Updating row {index} in stage {stage} to 'done'")
                    df.at[index, "Status"] = "done"

            processed_data[stage] = df

        with pd.ExcelWriter(excel_filepath, engine="openpyxl") as writer:
            for sheet_name, df in processed_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        self.log_buffer.clear()
        
# run ros
def run_ros_spin(listenerNode):
    rclpy.spin(listenerNode)


# main runner for ros process runner
def main(args=None):
    rclpy.init(args=args)
    listenerNode = ListenerNode()
    try:
        rclpy.spin(listenerNode)
    except KeyboardInterrupt:
        pass
    finally:
        listenerNode.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
