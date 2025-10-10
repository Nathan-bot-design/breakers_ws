# #!/usr/bin/env python3
# # """
# # dojo_behavior_tree.py

# # Behavior tree that:
# #  - Moves the robot across a sequence of waypoints
# #  - Uses a camera to detect screen item and item color
# #  - Selects drop-off point based on color and publishes servo command to offload
# #  - Publishes /goal_pose for RViz and waypoint markers for visualization

# # This is a cleaned-up / improved version of your original script that:
# #  - Ensures each MoveToMapPosition only publishes/send its goal once and never "revisits" the same goal.
# #  - Emits clear, single-line stage logs like:
# #      "Moving to ramp1"  (when sending)
# #      "Finished ramp1"    (when the action reports success or treated-as-success abort)
# #  - Publishes the current goal as both /goal_pose (PoseStamped) and a visual Marker (arrow) so RViz shows where the robot is headed.
# #  - Preserves all original classes and behavior (only augments MoveToMapPosition with better logging and RViz arrow publishing).
# # """

# import rclpy
# from rclpy.node import Node
# from rclpy.action import ActionClient
# from rclpy.qos import QoSProfile
# import py_trees
# import py_trees_ros
# from geometry_msgs.msg import PoseStamped
# from nav2_msgs.action import NavigateToPose
# from std_msgs.msg import String
# from visualization_msgs.msg import Marker, MarkerArray
# from rclpy.action.client import GoalStatus
# import time
# from std_msgs.msg import Float32
# from typing import Optional

# # -----------------------
# # Helper: make pose directly from RViz (x,y,qx,qy,qz,qw)
# # -----------------------
# def make_pose_from_rviz(x, y, qx, qy, qz, qw, frame="map"):
#     ps = PoseStamped()
#     ps.header.frame_id = frame
#     ps.header.stamp = rclpy.time.Time().to_msg()
#     ps.pose.position.x = float(x)
#     ps.pose.position.y = float(y)
#     ps.pose.position.z = 0.0
#     ps.pose.orientation.x = float(qx)
#     ps.pose.orientation.y = float(qy)
#     ps.pose.orientation.z = float(qz)
#     ps.pose.orientation.w = float(qw)
#     return ps

# # -----------------------
# # USER: Replace with real waypoints from RViz (/goal_pose)

# # kings

# WAYPOINTS = {
#     "weeding":  make_pose_from_rviz(0.4583090543746948, 2.8434579372406006, 0.0, 0.0, -0.999416263086319, 0.03416332944222052),
#     "ramp1":    make_pose_from_rviz(0.026719212532043457, 2.871814489364624, 0.0, 0.0, -0.9993689191191492, 0.03552131048572937),
#     "grass1":   make_pose_from_rviz(-0.5238167643547058, 2.9825963973999023, 0.0, 0.0, -0.6737467448234301, 0.7389623291073989),
#     "gravel":   make_pose_from_rviz(-0.6857829093933105, 2.2556872367858887, 0.0, 0.0, -0.7412917924395527, 0.6711828949412784),
#     "sawdust":  make_pose_from_rviz(-0.6597670316696167, 1.7882885932922363, 0.0, 0.0, -0.6523841718480922, 0.757888443190737),
#     "grass2":   make_pose_from_rviz(-0.6648229956626892, 1.100379467010498, 0.0, 0.0, -0.7209490587485928, 0.6929880624437321),
#     "ramp2":    make_pose_from_rviz(-0.6093888282775879, 0.2551478147506714, 0.0, 0.0, -0.6889180725092997, 0.7248392162197568),
#     "loading":  make_pose_from_rviz(-0.5809906721115112, -0.14477598667144775, 0.0, 0.0, -0.05940444756452824, 0.9982339964204551),
#     "d1":       make_pose_from_rviz(0.4610176086425781, -0.14088964462280273, 0.0, 0.0, 0.021723566645224207, 0.9997640154817589),
#     "d2":       make_pose_from_rviz(1.4670453071594238, -0.16850292682647705, 0.0, 0.0, 0.6993558964750385, 0.7147736215513238),
# }

# # -----------------------
# # WAYPOINTS = {
# #     "weeding":  make_pose_from_rviz(-0.930598, 3.062611, 0.0, 0.0, 0.748628, 0.662990),
# #     "ramp1":    make_pose_from_rviz(-2.2916247844696045, 3.231801986694336, 0.0, 0.0, -0.7217528278020483, 0.6921508907454695),
# #     "grass1":   make_pose_from_rviz(-2.134199857711792, 2.0926566123962402, 0.0, 0.0, -0.6997734348511632, 0.7143648506726832),
# #     "gravel":   make_pose_from_rviz(-2.1026406288146973, 1.6457620859146118, 0.0, 0.0, -0.699773425069685, 0.7143648602543675),
# #     "sawdust":  make_pose_from_rviz(-2.064913749694824, 0.8858974575996399, 0.0, 0.0, -0.6997733946321537, 0.7143648900701882),
# #     "grass2":   make_pose_from_rviz(-1.989225149154663, 0.4624646306037903, 0.0, 0.0, -0.6996858159706905, 0.7144506693463372),
# #     "ramp2":    make_pose_from_rviz(-1.8715894222259521, 0.1741146594285965, 0.0, 0.0, -0.14043884204619392, 0.9900893553840099),
# #     "loading":  make_pose_from_rviz(-0.6222162246704102, -0.13495390117168427, 0.0, 0.0, 0.13020588028468813, 0.9914869786029917),
# #     "d1":       make_pose_from_rviz(0.1618044376373291, 0.23586659133434296, 0.0, 0.0, 0.7491769352647264, 0.6623699266024627),
# #     "d2":       make_pose_from_rviz(0.21818673610687256, 1.7869453430175781, 0.0, 0.0, 0.7622709177385536, 0.6472580999647847),
# # }


# # #waypoints for the test gamefield
# # WAYPOINTS = {
# #     "weeding":  make_pose_from_rviz(4.376263618469238, 6.141400337219238, 0.0, 0.0, 0.9270287905570218, 0.3749901618421282),
# #     "ramp1":    make_pose_from_rviz(3.4751272201538086, 6.965201377868652, 0.0, 0.0, -0.9098744381263388, 0.41488372689740327),
# #     "grass1":   make_pose_from_rviz(2.808107852935791, 6.219321250915527, 0.0, 0.0, -0.8555817524605689, 0.517667716645052),
# #     "gravel":   make_pose_from_rviz(2.1853184700012207, 5.1144585609436035, 0.0, 0.0, -0.3219066765898746, 0.9467714040711527),
# #     "sawdust":  make_pose_from_rviz(2.9122581481933594, 4.455145835876465, 0.0, 0.0, -0.32331065217716, 0.9462928839364584),
# #     "grass2":   make_pose_from_rviz(3.66929292678833, 3.9430816173553467, 0.0, 0.0, 0.4452724853489267, 0.8953951160192856),
# #     "ramp2":    make_pose_from_rviz(4.231014728546143, 4.751044273376465, 0.0, 0.0, 0.4520530864412896, 0.8919910352906603),
# #     "loading":  make_pose_from_rviz(3.3496828079223633, 5.354134559631348, 0.0, 0.0, -0.26502480775708026, 0.9642415938307799),
# #     "d1":       make_pose_from_rviz(4.111565589904785, 3.430048942565918, 0.0, 0.0, 0.44285238538350274, 0.8965945375475703),
# #     "d2":       make_pose_from_rviz(4.7606682777404785, 2.91103196144104, 0.0, 0.0, 0.47195661303846154, 0.8816217757118207),
# # }


# # -----------------------
# # MoveToMapPosition (patched to handle preemptions, single-send, visual marker for RViz)
# # -----------------------
# class MoveToMapPosition(py_trees.behaviour.Behaviour):
#     def __init__(self, name, target_pose: PoseStamped):
#         super().__init__(name)
#         self.target_pose = target_pose
#         self._action_client: Optional[ActionClient] = None
#         self._goal_future = None
#         self._goal_handle = None
#         self._result_future = None
#         self._completed = False
#         self._goal_pub = None
#         self._node: Optional[Node] = None
#         self._marker_pub = None
#         self._started_logging = False

#     def setup(self, **kwargs):
#         node = kwargs.get("node")
#         if node:
#             self._node = node
#             # Nav2 action client
#             self._action_client = ActionClient(node, NavigateToPose, "navigate_to_pose")
#             # publish for RViz pose tool compatibility
#             self._goal_pub = node.create_publisher(PoseStamped, "/goal_pose", QoSProfile(depth=10))
#             # marker to show current heading/goal in RViz
#             self._marker_pub = node.create_publisher(Marker, "/current_goal_marker", QoSProfile(depth=10))
#             self._node.get_logger().info(f"{self.name}: Action client & publishers created for Nav2 & RViz")

#     def initialise(self):
#         # reset only if never completed previously; if already completed, keep completed=True to avoid re-sending
#         self._goal_future = None
#         self._goal_handle = None
#         self._result_future = None
#         # only set started_logging false if not completed yet
#         if not self._completed:
#             self._started_logging = False

#     def _short_name(self):
#         # make readable name for messages (strip Go_ prefix if present)
#         n = self.name
#         if n.startswith("Go_"):
#             return n[3:]
#         return n

#     def _publish_marker(self):
#         if not self._marker_pub or not self._node:
#             return
#         m = Marker()
#         m.header.frame_id = self.target_pose.header.frame_id or "map"
#         m.header.stamp = rclpy.time.Time().to_msg()
#         m.ns = "current_goal"
#         m.id = 0
#         m.type = Marker.ARROW
#         m.action = Marker.ADD
#         # place arrow at goal pose (slightly above ground for visibility)
#         m.pose = self.target_pose.pose
#         m.pose.position.z = 0.1
#         m.scale.x = 0.4  # shaft length
#         m.scale.y = 0.08  # shaft diameter
#         m.scale.z = 0.08  # head diameter
#         m.color.a = 1.0
#         m.color.r = 0.0
#         m.color.g = 1.0
#         m.color.b = 0.0
#         self._marker_pub.publish(m)

#     def update(self):
#         # If this goal already completed, return success and never re-send.
#         if self._completed:
#             return py_trees.common.Status.SUCCESS

#         # first goal send
#         if self._goal_future is None:
#             if not self._action_client.wait_for_server(timeout_sec=5.0):
#                 self._node.get_logger().error(f"{self.name}: Nav2 action server not available")
#                 return py_trees.common.Status.FAILURE

#             # Log start (only once)
#             if not self._started_logging:
#                 short = self._short_name()
#                 # Print the "Moving to <name>" exactly once when we start sending the goal.
#                 # Use info logging for consistency; StageAnnounce still exists but MoveToMapPosition will handle the "moving" and "finished" logs.
#                 self._node.get_logger().info(f"Moving to {short}")
#                 self._started_logging = True

#             goal_msg = NavigateToPose.Goal()
#             goal_msg.pose = self.target_pose

#             # store current goal in /goal_pose for RViz tools and to visualize heading
#             if self._goal_pub:
#                 self.target_pose.header.stamp = rclpy.time.Time().to_msg()
#                 self._goal_pub.publish(self.target_pose)
#             # also publish a marker arrow for RViz to show where it's heading
#             self._publish_marker()

#             # send to Nav2 action server
#             self._goal_future = self._action_client.send_goal_async(goal_msg)
#             self._goal_future.add_done_callback(self._goal_response_callback)

#             return py_trees.common.Status.RUNNING

#         # check result
#         if self._result_future is not None and self._result_future.done():
#             status = self._result_future.result().status
#             short = self._short_name()
#             self._node.get_logger().info(f"{self.name}: Result status={status}")

#             # Treat success
#             if status == GoalStatus.STATUS_SUCCEEDED:
#                 self._node.get_logger().info(f"Finished {short}")
#                 # remove/update marker to indicate goal reached (set alpha low)
#                 if self._marker_pub:
#                     m = Marker()
#                     m.header.frame_id = self.target_pose.header.frame_id or "map"
#                     m.header.stamp = rclpy.time.Time().to_msg()
#                     m.ns = "current_goal"
#                     m.id = 0
#                     m.action = Marker.DELETE
#                     self._marker_pub.publish(m)
#                 self._completed = True
#                 return py_trees.common.Status.SUCCESS

#             # treat preempted/aborted as success if we're already at goal
#             elif status == GoalStatus.STATUS_ABORTED:
#                 # This often happens when the nav stack preempts; treat as success to continue sequence
#                 self._node.get_logger().warn(f"{self.name}: Got ABORTED, treating as success (likely preempted)")
#                 # also remove marker
#                 if self._marker_pub:
#                     m = Marker()
#                     m.header.frame_id = self.target_pose.header.frame_id or "map"
#                     m.header.stamp = rclpy.time.Time().to_msg()
#                     m.ns = "current_goal"
#                     m.id = 0
#                     m.action = Marker.DELETE
#                     self._marker_pub.publish(m)
#                 self._completed = True
#                 # print finished message to maintain user-visible sequence continuity
#                 self._node.get_logger().info(f"Finished {short}")
#                 return py_trees.common.Status.SUCCESS

#             else:
#                 self._node.get_logger().warn(f"{self.name}: Failed, status={status}")
#                 self._completed = True
#                 return py_trees.common.Status.FAILURE

#         return py_trees.common.Status.RUNNING

#     def _goal_response_callback(self, future):
#         self._goal_handle = future.result()
#         if not self._goal_handle.accepted:
#             self._node.get_logger().warn(f"{self.name}: Goal rejected")
#             self._completed = True
#         else:
#             self._node.get_logger().info(f"{self.name}: Goal accepted")
#             self._result_future = self._goal_handle.get_result_async()

# # -----------------------
# # StageAnnounce
# # -----------------------
# class StageAnnounce(py_trees.behaviour.Behaviour):
#     def __init__(self, message, name=None):
#         super().__init__(name or f"Announce_{message}")
#         self.message = message
#         self._announced = False

#     def initialise(self):
#         self._announced = False

#     def update(self):
#         if not self._announced:
#             print(self.message)
#             self._announced = True
#         return py_trees.common.Status.SUCCESS

# # -----------------------
# # WaitSeconds
# # -----------------------
# class WaitSeconds(py_trees.behaviour.Behaviour):
#     def __init__(self, name, seconds=1.0):
#         super().__init__(name)
#         self.seconds = float(seconds)
#         self._start_time = None

#     def initialise(self):
#         self._start_time = time.time()

#     def update(self):
#         if (time.time() - self._start_time) >= self.seconds:
#             return py_trees.common.Status.SUCCESS
#         return py_trees.common.Status.RUNNING

# # -----------------------
# # CameraDetect (dummy -> always succeed)
# # -----------------------
# class CameraDetect(py_trees.behaviour.Behaviour):
#     def __init__(self, name="CameraDetect"):
#         super().__init__(name)
#         self._done = False

#     def initialise(self):
#         self._done = False

#     def update(self):
#         if not self._done:
#             print("Late blight detected")
#             self._done = True
#         return py_trees.common.Status.SUCCESS

# # -----------------------
# # DetectColor (dummy -> always red)
# # -----------------------
# class DetectColor(py_trees.behaviour.Behaviour):
#     """
#     Subscribes to /detected_colour (std_msgs/String) and writes it to blackboard as 'item_color'.
#     Succeeds as soon as a valid color is received.
#     """
#     def __init__(self, name="DetectColor", topic="/detected_colour", timeout=5.0):
#         super().__init__(name)
#         self.topic = topic
#         self.timeout = timeout
#         self._node = None
#         self._sub = None
#         self._received = None
#         self._start_time = None

#     def setup(self, **kwargs):
#         self._node = kwargs.get("node")
#         if self._node:
#             qos = QoSProfile(depth=10)
#             self._sub = self._node.create_subscription(
#                 String, self.topic, self._callback, qos
#             )
#             self._node.get_logger().info(f"{self.name}: subscribed to {self.topic}")

#     def initialise(self):
#         self._received = None
#         self._start_time = time.time()

#     def _callback(self, msg):
#         color = msg.data.strip().lower()
#         self._received = color
#         bb = py_trees.blackboard.Blackboard()
#         bb.set("item_color", color)
#         if self._node:
#             self._node.get_logger().info(
#                 f"{self.name}: received '{color}' -> stored in blackboard as item_color"
#             )

#     def update(self):
#         if self._received:
#             return py_trees.common.Status.SUCCESS

#         if (time.time() - self._start_time) > self.timeout:
#             if self._node:
#                 self._node.get_logger().warn(
#                     f"{self.name}: timeout, no colour detected from {self.topic}"
#                 )
#             return py_trees.common.Status.FAILURE

#         return py_trees.common.Status.RUNNING


# # -----------------------
# # ServoPublish
# # -----------------------
# # class ServoPublish(py_trees.behaviour.Behaviour):
# #     def __init__(self, name="ServoPublish", topic="/servo_cmd", command_open="OPEN", command_close="CLOSE"):
# #         super().__init__(name)
# #         self.topic = topic
# #         self.command_open = command_open
# #         self.command_close = command_close
# #         self._node = None
# #         self._pub = None
# #         self._done = False

# #     def setup(self, **kwargs):
# #         self._node = kwargs.get("node")
# #         if self._node:
# #             self._pub = self._node.create_publisher(String, self.topic, QoSProfile(depth=10))

# #     def initialise(self):
# #         self._done = False

# #     def update(self):
# #         if self._done:
# #             return py_trees.common.Status.SUCCESS
# #         if self._pub:
# #             self._pub.publish(String(data=self.command_open))
# #             time.sleep(0.5)
# #             self._pub.publish(String(data=self.command_close))
# #             self._done = True
# #             return py_trees.common.Status.SUCCESS
# #         return py_trees.common.Status.FAILURE



# class ServoPublish(py_trees.behaviour.Behaviour):
#     def __init__(self, name="ServoPublish", topic="/servo_angle", angle=60.0):
#         super().__init__(name)
#         self.topic = topic
#         self.angle = angle
#         self._node = None
#         self._pub = None
#         self._done = False

#     def setup(self, **kwargs):
#         self._node = kwargs.get("node")
#         if self._node:
#             self._pub = self._node.create_publisher(Float32, self.topic, 10)

#     def initialise(self):
#         self._done = False

#     def update(self):
#         if self._done:
#             return py_trees.common.Status.SUCCESS

#         if self._pub:
#             msg = Float32()
#             msg.data = self.angle
#             self._pub.publish(msg)
#             self.logger.info(f"Published servo angle: {self.angle}")
#             self._done = True
#             return py_trees.common.Status.SUCCESS

#         return py_trees.common.Status.FAILURE


# # -----------------------
# # Markers
# # -----------------------
# def create_waypoints_marker_array(frame_id="map"):
#     arr = MarkerArray()
#     for i, (name, pose_stamped) in enumerate(WAYPOINTS.items()):
#         m = Marker()
#         m.header.frame_id = frame_id
#         m.header.stamp = rclpy.time.Time().to_msg()
#         m.ns = "waypoints"
#         m.id = i
#         m.type = Marker.TEXT_VIEW_FACING
#         m.action = Marker.ADD
#         m.pose.position = pose_stamped.pose.position
#         m.pose.position.z = 0.2
#         m.scale.z = 0.2
#         m.color.a = 1.0
#         m.color.r = 1.0
#         m.color.g = 1.0
#         m.color.b = 1.0
#         m.text = name
#         arr.markers.append(m)
#     return arr

# # -----------------------
# # Build tree
# # -----------------------
# def create_root(node):
#     root = py_trees.composites.Sequence("Root", memory=True)
#     # First move to weeding and then camera detect
#     root.add_children([
#         MoveToMapPosition("Go_weeding", WAYPOINTS["weeding"]),
#         CameraDetect("DetectScreen")
#     ])

#     # Path sequence (ramp1 -> grass1 -> gravel -> sawdust -> grass2 -> ramp2)
#     seq = py_trees.composites.Sequence("Path", memory=True)
#     for s in ["ramp1", "grass1", "gravel", "sawdust", "grass2", "ramp2"]:
#         # MoveToMapPosition already logs Moving/Finished; StageAnnounce prints once when added
#         seq.add_children([
#             MoveToMapPosition(f"Go_{s}", WAYPOINTS[s]),
#             StageAnnounce(f"Now at {s}")
#         ])
#     root.add_child(seq)

#     # Loading area -> wait -> detect color
#     root.add_children([
#         MoveToMapPosition("Go_loading", WAYPOINTS["loading"]),
#         WaitSeconds("WaitForItem", 2.0),
#         DetectColor("DetectColor")
#     ])

#     # Choose drop-off based on color
#     class ColorIs(py_trees.behaviour.Behaviour):
#         def __init__(self, name, color):
#             super().__init__(name)
#             self.color = color
#             self.bb = py_trees.blackboard.Blackboard()

#         def update(self):
#             bb = py_trees.blackboard.Blackboard()
#             color = bb.get("item_color")   # <-- FIX
#             return py_trees.common.Status.SUCCESS if color == self.color else py_trees.common.Status.FAILURE


#     red_seq = py_trees.composites.Sequence("RedSeq", memory=True)
#     red_seq.add_children([ColorIs("IsRed", "red"), MoveToMapPosition("Go_d1", WAYPOINTS["d1"])])

#     blue_seq = py_trees.composites.Sequence("BlueSeq", memory=True)
#     blue_seq.add_children([ColorIs("IsBlue", "blue"), MoveToMapPosition("Go_d2", WAYPOINTS["d2"])])

#     # Stateless selector: re-evaluates every tick
#     selector = py_trees.composites.Selector("Route", memory=False)
#     selector.add_children([red_seq, blue_seq, StageAnnounce("Unknown color")])

#     root.add_child(selector)
#     root.add_child(ServoPublish("OffloadServo"))

#     return root

# # -----------------------
# # Main
# # -----------------------
# def main():
#     rclpy.init()
#     bt = None
#     try:
#         # short-lived node to publish waypoint text markers early (so RViz can see labels immediately)
#         tmp = rclpy.create_node("dojo_bt_tmp")
#         pub = tmp.create_publisher(MarkerArray, "/dojo_waypoints", QoSProfile(depth=1))
#         pub.publish(create_waypoints_marker_array())
#         tmp.destroy_node()

#         # create tree and set it up with a ROS node
#         root_bt = create_root(None)
#         bt = py_trees_ros.trees.BehaviourTree(root_bt)
#         bt.setup(timeout=15.0, node=bt.node)

#         # publish waypoint markers from the main tree node so they persist in RViz
#         pub2 = bt.node.create_publisher(MarkerArray, "/dojo_waypoints", QoSProfile(depth=1))
#         pub2.publish(create_waypoints_marker_array())

#         # Also publish an initial empty current_goal_marker delete (ensure clean state in RViz)
#         m_del = Marker()
#         m_del.header.frame_id = "map"
#         m_del.header.stamp = rclpy.time.Time().to_msg()
#         m_del.ns = "current_goal"
#         m_del.id = 0
#         m_del.action = Marker.DELETE
#         marker_pub_init = bt.node.create_publisher(Marker, "/current_goal_marker", QoSProfile(depth=1))
#         marker_pub_init.publish(m_del)

#         # Run the tree ticking loop and spin the node so action callbacks, publishers, etc. run.
#         bt.tick_tock(period_ms=100)
#         rclpy.spin(bt.node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         if bt:
#             bt.shutdown()
#         rclpy.shutdown()

# if __name__ == "__main__":
#     main()





#!/usr/bin/env python3
"""
dojo_behavior_tree.py (Enhanced version)

Changes:
- Adds 5 waypoints each for D1 and D2 paths (dummy values included)
- Prints color and detection messages only once per stage
- Announces each waypoint after completion
- Keeps navigation stable by breaking long paths into smoother segments
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile
import py_trees
import py_trees_ros
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String, Float32
from visualization_msgs.msg import Marker, MarkerArray
from rclpy.action.client import GoalStatus
import time
from typing import Optional

# -----------------------
# Helper
# -----------------------
def make_pose_from_rviz(x, y, qx, qy, qz, qw, frame="map"):
    ps = PoseStamped()
    ps.header.frame_id = frame
    ps.header.stamp = rclpy.time.Time().to_msg()
    ps.pose.position.x = float(x)
    ps.pose.position.y = float(y)
    ps.pose.position.z = 0.0
    ps.pose.orientation.x = float(qx)
    ps.pose.orientation.y = float(qy)
    ps.pose.orientation.z = float(qz)
    ps.pose.orientation.w = float(qw)
    return ps


# -----------------------
# WAYPOINTS (dummy additions for d11-d15, d21-d25)
# -----------------------
# 

# to use with the map labelled my_gamefield.pgm


WAYPOINTS = {
    # === Base route (weeding → loading) ===
    "weeding":  make_pose_from_rviz(-2.865177, -2.211364, 0.0, 0.0, -0.938095, 0.346379),  # P1
    "ramp1":    make_pose_from_rviz(-1.838345, -1.310360, 0.0, 0.0,  0.907927, 0.419128),  # P2
    "grass1":   make_pose_from_rviz(-2.763846, -0.437470, 0.0, 0.0,  0.925580, 0.378551),  # P3
    "gravel":   make_pose_from_rviz(-3.423790,  0.228918, 0.0, 0.0, -0.944690, 0.327964),  # P4
    "sawdust":  make_pose_from_rviz(-4.251595, -0.393288, 0.0, 0.0, -0.913787, 0.406193),  # P5
    "grass2":   make_pose_from_rviz(-4.847361, -1.054612, 0.0, 0.0, -0.427709, 0.903916),  # P6
    "ramp2":    make_pose_from_rviz(-4.095685, -1.810651, 0.0, 0.0, -0.437040, 0.899442),  # P7
    "loading":  make_pose_from_rviz(-3.379393, -1.001714, 0.0, 0.0, -0.932240, 0.361840),  # P8

    # === White (D1) route ===
    "d11": make_pose_from_rviz(-3.694529, -2.377832, 0.0, 0.0, -0.429074, 0.903269),  # P9
    "d12": make_pose_from_rviz(-4.397106, -3.885527, 0.0, 0.0, -0.921589, 0.388168),  # P10
    "d13": make_pose_from_rviz(-6.286625, -4.262188, 0.0, 0.0,  0.908466, 0.417959),  # P11
    "d14": make_pose_from_rviz(-4.913682, -2.547691, 0.0, 0.0,  0.780133, 0.625613),  # P12
    "d25": make_pose_from_rviz(-5.427554, -1.396694, 0.0, 0.0, -0.376507, 0.926414),  # P13 (unique end for white)

    # === Blue (D2) route ===
    "d21": make_pose_from_rviz(-3.694529, -2.377832, 0.0, 0.0, -0.429074, 0.903269),  # same as d11 (P9)
    "d22": make_pose_from_rviz(-4.397106, -3.885527, 0.0, 0.0, -0.921589, 0.388168),  # same as d12 (P10)
    "d23": make_pose_from_rviz(-6.286625, -4.262188, 0.0, 0.0,  0.908466, 0.417959),  # same as d13 (P11)
    "d24": make_pose_from_rviz(-4.913682, -2.547691, 0.0, 0.0,  0.780133, 0.625613),  # same as d14 (P12)
    "d15": make_pose_from_rviz(-6.007787, -1.880753, 0.0, 0.0, -0.401984, 0.915647),  # P14 (unique end for blue)
}




# -----------------------
# Behaviors
# -----------------------
class MoveToMapPosition(py_trees.behaviour.Behaviour):
    def __init__(self, name, target_pose: PoseStamped):
        super().__init__(name)
        self.target_pose = target_pose
        self._node: Optional[Node] = None
        self._action_client = None
        self._goal_future = None
        self._goal_handle = None
        self._result_future = None
        self._goal_pub = None
        self._marker_pub = None
        self._completed = False
        self._started_logging = False

    def setup(self, **kwargs):
        node = kwargs.get("node")
        if node:
            self._node = node
            self._action_client = ActionClient(node, NavigateToPose, "navigate_to_pose")
            self._goal_pub = node.create_publisher(PoseStamped, "/goal_pose", 10)
            self._marker_pub = node.create_publisher(Marker, "/current_goal_marker", 10)

    def _short_name(self):
        return self.name.replace("Go_", "")

    def initialise(self):
        if not self._completed:
            self._started_logging = False
        self._goal_future = None
        self._goal_handle = None
        self._result_future = None

    def _publish_marker(self):
        if not self._marker_pub or not self._node:
            return
        m = Marker()
        m.header.frame_id = "map"
        m.header.stamp = rclpy.time.Time().to_msg()
        m.ns = "current_goal"
        m.id = 0
        m.type = Marker.ARROW
        m.action = Marker.ADD
        m.pose = self.target_pose.pose
        m.pose.position.z = 0.1
        m.scale.x = 0.4
        m.scale.y = 0.08
        m.scale.z = 0.08
        m.color.a = 1.0
        m.color.g = 1.0
        self._marker_pub.publish(m)

    def update(self):
        if self._completed:
            return py_trees.common.Status.SUCCESS

        if self._goal_future is None:
            if not self._action_client.wait_for_server(timeout_sec=5.0):
                self._node.get_logger().error(f"{self.name}: Nav2 server not available")
                return py_trees.common.Status.FAILURE

            if not self._started_logging:
                self._node.get_logger().info(f"Moving to {self._short_name()}")
                self._started_logging = True

            goal = NavigateToPose.Goal()
            goal.pose = self.target_pose
            self._goal_pub.publish(self.target_pose)
            self._publish_marker()
            self._goal_future = self._action_client.send_goal_async(goal)
            self._goal_future.add_done_callback(self._goal_response_callback)
            return py_trees.common.Status.RUNNING

        if self._result_future and self._result_future.done():
            status = self._result_future.result().status
            short = self._short_name()
            if status == GoalStatus.STATUS_SUCCEEDED:
                self._node.get_logger().info(f"Finished {short}")
                self._completed = True
                return py_trees.common.Status.SUCCESS
            elif status == GoalStatus.STATUS_ABORTED:
                self._node.get_logger().warn(f"{self.name}: ABORTED, treating as success")
                self._completed = True
                return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING

    def _goal_response_callback(self, future):
        self._goal_handle = future.result()
        if not self._goal_handle.accepted:
            self._node.get_logger().warn(f"{self.name}: Goal rejected")
            self._completed = True
        else:
            self._result_future = self._goal_handle.get_result_async()


class StageAnnounce(py_trees.behaviour.Behaviour):
    def __init__(self, message):
        super().__init__(f"Announce_{message}")
        self.message = message
        self._done = False

    def initialise(self):
        self._done = False

    def update(self):
        if not self._done:
            print(self.message)
            self._done = True
        return py_trees.common.Status.SUCCESS


class WaitSeconds(py_trees.behaviour.Behaviour):
    def __init__(self, name, seconds=1.0):
        super().__init__(name)
        self.seconds = seconds
        self._start = None

    def initialise(self):
        self._start = time.time()

    def update(self):
        return (
            py_trees.common.Status.SUCCESS
            if time.time() - self._start >= self.seconds
            else py_trees.common.Status.RUNNING
        )


# class CameraDetect(py_trees.behaviour.Behaviour):
#     def __init__(self, name="CameraDetect"):
#         super().__init__(name)
#         self._printed = False

#     def update(self):
#         if not self._printed:
#             print("Late blight detected (Weeding Area)")
#             self._printed = True
#         return py_trees.common.Status.SUCCESS

class CameraDetect(py_trees.behaviour.Behaviour):
    def __init__(self, topic="/inference_result", timeout=10.0):
        super().__init__("CameraDetect")
        self.topic = topic
        self.timeout = timeout
        self._node = None
        self._sub = None
        self._received = None
        self._start_time = None
        self._printed = False
    
    def setup(self, **kwargs):
        self._node = kwargs.get("node")
        if self._node:
            self._sub = self._node.create_subscription(
                String, self.topic, self._callback, 10
            )
    
    def initialise(self):
        self._received = None
        self._start_time = time.time()
    
    def _callback(self, msg):
        inference = msg.data.strip().lower()
        self._received = inference
        py_trees.blackboard.Blackboard().set("inference", inference)
        if not self._printed:
            print(f"Inference Result: {inference}")
            self._printed = True
    
    def update(self):
        if self._received:
            return py_trees.common.Status.SUCCESS
        if time.time() - self._start_time > self.timeout:
            print("Camera detection timeout!")
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.RUNNING

    # def update(self):
    #     if not self._printed:
    #         print("Late blight detected (Weeding Area)")
    #         self._printed = True
    #     return py_trees.common.Status.SUCCESS

class DetectColor(py_trees.behaviour.Behaviour):
    def __init__(self, topic="/detected_colour", timeout=5.0):
        super().__init__("DetectColor")
        self.topic = topic
        self.timeout = timeout
        self._node = None
        self._sub = None
        self._received = None
        self._start_time = None
        self._printed = False

    def setup(self, **kwargs):
        self._node = kwargs.get("node")
        if self._node:
            self._sub = self._node.create_subscription(
                String, self.topic, self._callback, 10
            )

    def initialise(self):
        self._received = None
        self._start_time = time.time()

    def _callback(self, msg):
        color = msg.data.strip().lower()
        self._received = color
        py_trees.blackboard.Blackboard().set("item_color", color)
        if not self._printed:
            print(f"Detected color: {color}")
            self._printed = True

    def update(self):
        if self._received:
            return py_trees.common.Status.SUCCESS
        if time.time() - self._start_time > self.timeout:
            print("Color detection timeout!")
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.RUNNING


class ServoPublish(py_trees.behaviour.Behaviour):
    def __init__(self, angle):
        super().__init__("ServoPublish")
        self.angle = angle
        self._node = None
        self._pub = None
        self._done = False

    def setup(self, **kwargs):
        self._node = kwargs.get("node")
        if self._node:
            self._pub = self._node.create_publisher(Float32, "/servo_angle", 10)

    def update(self):
        if self._done:
            return py_trees.common.Status.SUCCESS
        msg = Float32()
        msg.data = self.angle
        self._pub.publish(msg)
        print(f"Servo angle {self.angle}° published")
        self._done = True
        return py_trees.common.Status.SUCCESS


# -----------------------
# Waypoint markers for RViz
# -----------------------
def create_waypoints_marker_array(frame_id="map"):
    arr = MarkerArray()
    for i, (name, pose) in enumerate(WAYPOINTS.items()):
        m = Marker()
        m.header.frame_id = frame_id
        m.header.stamp = rclpy.time.Time().to_msg()
        m.ns = "waypoints"
        m.id = i
        m.type = Marker.TEXT_VIEW_FACING
        m.action = Marker.ADD
        m.pose.position = pose.pose.position
        m.pose.position.z = 0.2
        m.scale.z = 0.2
        m.color.a = 1.0
        m.color.r = 1.0
        m.color.g = 1.0
        m.color.b = 1.0
        m.text = name
        arr.markers.append(m)
    return arr


# -----------------------
# Build Behavior Tree
# -----------------------
def create_root(node):
    root = py_trees.composites.Sequence("Root", memory=True)

    # Stage 1: Weeding + detection
    root.add_children([
        MoveToMapPosition("Go_weeding", WAYPOINTS["weeding"]),
        CameraDetect(),
    ])

    # Stage 2: Terrain traversal
    seq = py_trees.composites.Sequence("Path", memory=True)
    for s in ["ramp1", "grass1", "gravel", "sawdust", "grass2", "ramp2"]:
        seq.add_children([
            MoveToMapPosition(f"Go_{s}", WAYPOINTS[s]),
            StageAnnounce(f"Now at {s}")
        ])
    root.add_child(seq)

    # Stage 3: Loading + color detection
    root.add_children([
        MoveToMapPosition("Go_loading", WAYPOINTS["loading"]),
        WaitSeconds("WaitForLoad", 2.0),
        DetectColor(),
    ])

    # Stage 4: Color decision path
    class ColorIs(py_trees.behaviour.Behaviour):
        def __init__(self, name, color):
            super().__init__(name)
            self.color = color

        def update(self):
            bb = py_trees.blackboard.Blackboard()
            return (
                py_trees.common.Status.SUCCESS
                if bb.get("item_color") == self.color
                else py_trees.common.Status.FAILURE
            )

    white_seq = py_trees.composites.Sequence("WhiteSeq", memory=True)
    white_seq.add_children([ColorIs("IsWhite", "white")])
    for s in ["d11", "d12", "d13", "d14", "d15"]:
        white_seq.add_children([MoveToMapPosition(f"Go_{s}", WAYPOINTS[s]), StageAnnounce(f"Now at {s}")])

    blue_seq = py_trees.composites.Sequence("BlueSeq", memory=True)
    blue_seq.add_children([ColorIs("IsBlue", "blue")])
    for s in ["d21", "d22", "d23", "d24", "d25"]:
        blue_seq.add_children([MoveToMapPosition(f"Go_{s}", WAYPOINTS[s]), StageAnnounce(f"Now at {s}")])

    route_selector = py_trees.composites.Selector("ColorRoute", memory=False)
    route_selector.add_children([white_seq, blue_seq, StageAnnounce("Unknown color route")])

    root.add_child(route_selector)
    root.add_child(ServoPublish(angle=0.0))
    root.add_child(ServoPublish(angle=130.0))

    return root


# -----------------------
# Main
# -----------------------
def main():
    rclpy.init()
    bt = None
    try:
        tmp = rclpy.create_node("dojo_bt_tmp")
        pub = tmp.create_publisher(MarkerArray, "/dojo_waypoints", 1)
        pub.publish(create_waypoints_marker_array())
        tmp.destroy_node()

        root_bt = create_root(None)
        bt = py_trees_ros.trees.BehaviourTree(root_bt)
        bt.setup(timeout=15.0, node=bt.node)

        pub2 = bt.node.create_publisher(MarkerArray, "/dojo_waypoints", 1)
        pub2.publish(create_waypoints_marker_array())

        m_del = Marker()
        m_del.header.frame_id = "map"
        m_del.ns = "current_goal"
        m_del.id = 0
        m_del.action = Marker.DELETE
        marker_pub_init = bt.node.create_publisher(Marker, "/current_goal_marker", 1)
        marker_pub_init.publish(m_del)

        bt.tick_tock(period_ms=100)
        rclpy.spin(bt.node)

    except KeyboardInterrupt:
        pass
    finally:
        if bt:
            bt.shutdown()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
