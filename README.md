# Quadrotor UAV Simulator (Unreal Engine 5)

A controllable quadrotor drone built in Unreal Engine 5 with Blueprints. It has a flight controller, environment collision, an onboard RGB camera, a telemetry HUD, waypoint autopilot, RRT path planning, LiDAR, and multi-camera (multimodal) image capture.

## Controls

| Key | Action |
|---|---|
| **T** | Take off |
| **G** | Land |
| **W / S** | Forward / backward |
| **A / D** | Left / right |
| **E / Q** | Up / down (E also lifts off from the ground) |
| **Left / Right Arrow** | Yaw (turn) |
| **P** | Start the waypoint autopilot; press again to cancel |
| **O** | Plan a path to the goal with RRT and fly it |
| **R** | Reset the drone to its spawn point |
| **F** | Capture one frame from all sensor cameras |

Movement and yaw only work while the drone is in the air. P and O take off automatically if the drone is on the ground. The LiDAR scans automatically.

## Implementation

**Drone (`BP_DronePawn`)**
The drone is a Pawn with a box collider as its root, so collision fits the drone's shape. Only the box collides with the world; the drone mesh has no collision. A `FloatingPawnMovement` component handles flight, with no gravity and braking that brings the drone to a stable hover when no keys are pressed.

**Flight controller**
- **Shared controls:** `ApplyHorizontal`, `ApplyVertical` and `ApplyYaw` move the drone. The keyboard and the autopilot both use these functions, so autopilot flight behaves like piloted flight.
- **Takeoff:** a 2-second Timeline smoothly lifts the drone to a hover and starts the rotor animation (`StartTakeoff` event).
- **Landing:** the drone descends gently until `Event Hit` detects a flat surface below it while it is landing or moving down, then it is marked as landed and the rotors stop (`StartLanding` event). Flying into a slope does not count as landing.
- **State:** `IsFlying` and `IsLanding` track the flight state and block movement on the ground.
- **Reset:** R cancels any mission, stops movement and teleports the drone back to the transform saved at BeginPlay.

**Tilt**
The visible model sits on a separate pivot that pitches and rolls based on the control inputs, smoothed with `FInterp To`. The collision box stays level, so tilting never affects collisions.

**Onboard RGB camera and telemetry HUD**
A Scene Capture 2D at the drone's nose renders a live feed into a Render Target shown in the top-right of the HUD. The HUD also shows X/Y/Z position (m), pitch/roll/yaw (degrees), speed (m/s) and the current camera view.

**Waypoint autopilot (P)**
`BP_Waypoint` actors are placed in the level with an Index (order) and Label. The autopilot loads them, then for each waypoint it works out where the waypoint is relative to the drone and sets the yaw, forward, sideways and vertical inputs with `Map Range Clamped`: it turns to face the waypoint, flies toward it, slows down as it gets close, hovers for the waypoint's `HoverDuration`, and lands after the last one. Waypoints can show a ring the drone flies through.

**Position log**
During a mission, `LogPosition` writes `POSLOG,time,waypoint,x,y,z` (meters) to the log every 0.5 s and at each waypoint.

**RRT path planning (O)**
- `BuildTree` grows a Rapidly-exploring Random Tree from the drone toward `BP_Goal`: it samples random points (sometimes the goal itself), steps from the nearest tree node (`FindNearest`), and keeps the step only if a sphere trace the size of the drone is clear (`IsPathClear`). It stops when a node can see the goal. Up to 5 attempts are made.
- `ExtractPath` follows the parent links back from the goal to get the path; `SmoothPath` removes unneeded turns by skipping to the farthest point with a clear line.
- `BuildPathWaypoints` spawns hidden waypoints along the smoothed path and the autopilot flies them.
- Debug lines: green = tree, red = raw path, blue = smoothed path.

**LiDAR (`BP_Lidar`)**
A component on the drone that scans every 0.1 s (timer). Each scan casts 16 vertical channels × 90 horizontal steps (4° apart, full 360°) of line traces out to 50 m, draws the hits as red points and stores them in `ScanPoints`. Every 10th scan, the scan number, drone position, rotation and all hit points are written to the log in one line.

**Multimodal capture (F)**
A `SensorRig` on the drone's nose holds three Scene Capture cameras at the exact same position and field of view: RGB (`Cam_RGB`), depth (`Cam_Depth`, distance in cm) and surface normals (`Cam_Normal`). They only capture when F is pressed: `CaptureFrame` captures all three in the same frame and saves them with the same frame number to `Saved/Captures/` (`frame_N_rgb.png`, `frame_N_depth.hdr`, `frame_N_normal.hdr`), so the images line up pixel for pixel.

## Data scripts

Run these from the project folder (next to the `.uproject` file) after playing:

| Script | Output |
|---|---|
| `python extract_poslog.py` | `position_log.csv`: drone position during missions |
| `python extract_lidar.py` | `lidar_scans.csv`: one row per LiDAR hit point, with the drone's pose |
| `python fix_capture_alpha.py` | Viewable copies of the RGB captures (`*_rgb_fixed.png`); needs `pip install pillow` |
| `build_rrt_course.py` | Run inside Unreal (Tools → Execute Python Script) to build an RRT obstacle course |
