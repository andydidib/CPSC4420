# Quadrotor UAV Simulator (Unreal Engine 5.6)

## Implementation

**Drone**
The drone is a custom character created using a Pawn with a box collision that fits the UAV drone's shape more naturally than a standard character collision box. The drone mesh does not have its own collision box; instead, it fits inside the Pawn's collision box. A `FloatingPawnMovement` component handles flight movement, with gravity disabled and braking that brings the drone to a stable hover when no keys are pressed.

**Flight controller**
- **Takeoff:** a 2-second Timeline smoothly lifts the drone to a hover and starts the rotor animation.
- **Movement:** WASD and E/Q use `Add Movement Input` along the drone's forward, right, and up directions.
- **Yaw:** `Add Controller Yaw Input`, with the drone set to follow the controller's rotation.
- **Landing:** the drone descends gently until `Event Hit` detects a flat surface below it, then it is marked as landed and the rotors stop.

**Onboard RGB camera**
A Scene Capture 2D component at the drone's nose renders an RGB view into a Render Target, which is displayed as a live feed in the top-right corner of the screen. The camera is attached to the collision box rather than the mesh to keep it stable. In a future implementation, the camera will be connected to a gyroscope to improve stabilization.

**Telemetry HUD**
A widget displays the drone's X/Y/Z position (in meters), rotation (pitch, roll, and yaw), speed (m/s), and current camera view. The camera view variable changes depending on the view the user selects, such as thermal imaging or other available camera modes.

## Controls

| Key | Action |
|---|---|
| **T** | Take off |
| **G** | Land |
| **W / S** | Forward / backward |
| **A / D** | Left / right |
| **E / Q** | Up / down |
| **Left / Right Arrow** | Yaw |
