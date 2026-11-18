# Quadrotor UAV Simulator (Unreal Engine 5)

CPSC 4420, Team 9_2: Andy D. Botkin, Damian M. Giannaccini, Syd Richardson

This is a quadrotor drone we built in Unreal Engine 5 using Blueprints. You can fly it with the keyboard, and it also has a waypoint autopilot, RRT path planning, a LiDAR sensor, an onboard camera with a telemetry HUD, and RGB/depth/normal image capture.

## Running the project

### What you need

- Unreal Engine 5.8 (install it from the Epic Games Launcher)
- Git, to clone the repo
- Python 3, only if you want to run the data scripts

### Steps

1. Clone the repo:
   ```
   git clone https://github.com/andydidib/CPSC4420.git
   ```
   If the files come down as small text pointers instead of real assets, the repo uses Git LFS. Run `git lfs install` and then `git lfs pull` inside the folder.
2. Open the folder and double-click the `.uproject` file. If Unreal asks which engine version to use, pick 5.8.
3. The first launch takes a while because Unreal compiles shaders. Let it finish.
4. If it says some plugins are missing or disabled, go to Edit → Plugins, enable them, and restart the editor.
5. Open the level from the Content Browser (or File → Open Level). Use `<MapName>` for the main demo.
6. Press Play (the green arrow at the top, or Alt+P). Click inside the game window so it gets keyboard input.
7. Press T to take off, then fly around with the controls below.

If the game runs slowly, try lowering Settings → Engine Scalability Settings to Medium, or play as a Standalone Game from the Play dropdown.

## Controls

| Key | Action |
|---|---|
| T | Take off |
| G | Land |
| W / S | Forward / backward |
| A / D | Left / right |
| E / Q | Up / down (E also lifts off from the ground) |
| Left / Right Arrow | Turn (yaw) |
| P | Start the waypoint autopilot, press again to cancel |
| O | Plan a path to the goal with RRT and fly it |
| R | Reset the drone to where it spawned |
| F | Capture one frame from all the sensor cameras |

You can only move and turn while the drone is in the air. P and O will take off on their own if the drone is on the ground. The LiDAR scans on its own while you play.

## How it works

### The drone (BP_DronePawn)

The drone is a Pawn with a box collider as its root, so the collision matches the drone's shape. Only the box hits things; the drone mesh itself has no collision. Movement comes from a FloatingPawnMovement component with gravity turned off. When you let go of the keys, braking slows it down to a hover.

### Flight controls

ApplyHorizontal, ApplyVertical and ApplyYaw are the functions that actually move the drone. The keyboard and the autopilot both call them, so the drone flies the same way whether you're flying it or the autopilot is.

Takeoff (StartTakeoff) uses a 2-second Timeline to lift the drone up to a hover and start the rotors spinning.

Landing (StartLanding) lowers the drone slowly until Event Hit picks up a flat surface underneath it. At that point it counts as landed and the rotors stop. Bumping into a slope doesn't count as a landing.

IsFlying and IsLanding keep track of the flight state, and they stop the drone from moving while it's on the ground.

Pressing R cancels any mission, stops the drone, and teleports it back to the spot it started at (saved on BeginPlay).

### Tilt

The drone model sits on its own pivot that pitches and rolls with your inputs, smoothed with FInterp To. The collision box doesn't tilt, so tilting never changes how the drone collides with things.

### Camera and HUD

A Scene Capture 2D on the front of the drone renders to a Render Target, and that feed shows up in the top-right corner of the HUD. The HUD also shows the drone's X/Y/Z position in meters, pitch/roll/yaw in degrees, speed in m/s, and which camera view is active.

### Waypoint autopilot (P)

You place BP_Waypoint actors in the level and give each one an Index (the order to visit them in) and a Label. When the autopilot starts, it loads the waypoints and flies to them one at a time. For each one it figures out where the waypoint is compared to the drone, then uses Map Range Clamped to set the yaw, forward, sideways and up/down inputs. The drone turns toward the waypoint, flies to it, slows down as it gets close, hovers there for the waypoint's HoverDuration, and lands after the last one. Waypoints can also show a ring for the drone to fly through.

### Position log

While a mission is running, LogPosition writes a line like `POSLOG,time,waypoint,x,y,z` (in meters) to the log every 0.5 seconds and again at each waypoint.

### RRT path planning (O)

BuildTree grows a Rapidly-exploring Random Tree from the drone toward BP_Goal. Each step picks a random point (and sometimes picks the goal itself), finds the closest node already in the tree (FindNearest), and takes one step from that node toward the point. The step only gets added if a drone-sized sphere trace along it doesn't hit anything (IsPathClear). The tree stops growing once a node has a clear line to the goal. If it doesn't find a path, it tries again, up to 5 times.

ExtractPath then walks back through the parent links from the goal to the start to get the path. SmoothPath cleans it up by skipping ahead to the farthest point it can reach in a straight line, which gets rid of the extra zigzags.

Finally, BuildPathWaypoints spawns hidden waypoints along the smoothed path, and the autopilot flies them.

The debug lines are color coded: green is the tree, red is the raw path, and blue is the smoothed path.

### LiDAR (BP_Lidar)

BP_Lidar is a component on the drone that runs a scan every 0.1 seconds on a timer. A scan fires line traces in 16 vertical channels and 90 horizontal steps (every 4°, all the way around), each going out up to 50 m. Hits get drawn as red points and saved in ScanPoints. Every 10th scan, the scan number, the drone's position and rotation, and all the hit points are written to the log on one line.

### Multimodal capture (F)

There's a SensorRig on the front of the drone with three Scene Capture cameras in the exact same spot with the same field of view: RGB (Cam_RGB), depth (Cam_Depth, distance in cm) and surface normals (Cam_Normal). They only capture when you press F. CaptureFrame grabs all three in the same frame and saves them to `Saved/Captures/` with the same frame number (`frame_N_rgb.png`, `frame_N_depth.hdr`, `frame_N_normal.hdr`), so the three images line up pixel for pixel.

## Data scripts

Run these from the project folder (the one with the `.uproject` file) after you've played the game:

| Script | What it makes |
|---|---|
| `python extract_poslog.py` | `position_log.csv`, the drone's position during missions |
| `python extract_lidar.py` | `lidar_scans.csv`, one row per LiDAR hit with the drone's pose |
| `python fix_capture_alpha.py` | Viewable copies of the RGB captures (`*_rgb_fixed.png`). Needs `pip install pillow` first |
| `build_rrt_course.py` | Run this one inside Unreal (Tools → Execute Python Script) to build an RRT obstacle course |
