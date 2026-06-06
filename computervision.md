This design specifies the Vision Agent, the high-performance edge service responsible for translating   
  raw pixels into attention states. To achieve real-time performance without crashing the user's
  workstation, we will utilize a Modular Pipeline Architecture based on MediaPipe and OpenCV, utilizing a 
  "Temporal Smoothing" approach to avoid erratic state flickering.
                                                                                                          
  ---
  1. CV Data Pipeline Architecture                                                                        
                                                                                                          
  The pipeline operates as a linear sequence of transformations, where each stage enriches the data for
  the next.                                                                                               

  Stage 1: Capture & Pre-processing                                                                       
                                                                                                          
  - Input: Raw RGB frames from the webcam.                                                                
  - Operations:                                                                                           
    - Frame resizing (e.g., 640x480) to reduce computational load.                                        
    - Color space normalization.                                                                          
    - Horizontal flipping (to treat the image as a mirror for intuitive coordinate mapping).
  - Output: Pre-processed image tensor.                                                                   
                                                                                                          
  Stage 2: Landmark Extraction (The "Backbone")                                                           
                                                                                                          
  - Model: MediaPipe Face Mesh (468 3D landmarks).                                                        
  - Operation: Detect face presence and extract precise coordinates for eyelids, iris, and face contour.  
  - Failure Handling: If no face is detected $\rightarrow$ immediately trigger "Away" state and skip
  further stages.                                                                                         
                                                                                                          
  Stage 3: Feature Engineering (The "Analyzers")                                                          
                                                                                                          
  We extract four primary feature vectors from the landmarks:                                             
                                                                                                          
  1. Gaze Vector (Eye Tracking):
    - Calculate the relative position of the iris center within the eye socket.                           
    - Determine if the gaze is centered, left, or right.                                                  
  2. Head Pose Estimation (Euler Angles):                                                                 
    - Use the SolvePnP (Perspective-n-Point) algorithm.                                                   
    - Map 2D landmarks to a generic 3D face model to calculate Pitch (up/down), Yaw (left/right), and Roll
   (tilt).                                                                                                
  3. Eye Aspect Ratio (EAR - Blink Detection):
    - Formula: $\frac{||p_2 - p_6|| + ||p_3 - p_5||}{2 ||p_1 - p_4||}$ (vertical distance vs horizontal   
  distance).                                                                                              
    - Detects blinks and prolonged closures (drowsiness).                                                 
  4. Face Centering:                                                                                      
    - Measure the distance of the face bounding box from the center of the frame.                         
                                                                                                          
  Stage 4: State Classification (The "Inference Engine")                                                  
                                                                                                          
  The system uses a Weighted Heuristic Matrix to map features to states.                                  
  State: Focused                                                                                          
  Trigger Conditions: Low Yaw/Pitch ($\pm 15^\circ$) + Centered Gaze + Normal EAR.                        
  Weight/Confidence: High                                                                                 
  ────────────────────────────────────────                                                                
  State: Possibly Distracted                                                                              
  Trigger Conditions: Moderate Yaw/Pitch ($\pm 15^\circ$ to $30^\circ$) OR Gaze shifted from center.      
  Weight/Confidence: Medium                                                                               
  ────────────────────────────────────────                                                                
  State: Likely Disengaged                                                                                
  Trigger Conditions: High Yaw/Pitch ($> 30^\circ$) OR Gaze shifted $\pm 20^\circ$ from center.           
  Weight/Confidence: Medium                                                                               
  ────────────────────────────────────────                                                                
  State: Away                                                                                             
  Trigger Conditions: Face landmarks not detected in frame.                                               
  Weight/Confidence: Absolute                                                                             
  ---                                                                                                     
  2. Confidence Scoring & Temporal Smoothing                                                              
                                                                                                          
  To prevent a single frame of noise (e.g., a sneeze) from triggering a "Distraction Event," we implement 
  a Temporal Smoothing Window.                                                                            
                                                                                                          
  The Windowing Mechanism                                                                                 
                                                                                                          
  - Buffer: A sliding window of the last 30 frames ($\approx 1$ second at 30 FPS).                        
  - Voting: The state is determined by the mode (most frequent) state in the window.                      
  - Confidence Calculation:                                                                               
  $$\text{Confidence} = \frac{\text{Count of State X in Window}}{\text{Total Frames in Window}}$$         
  - Event Trigger: A "Drift Event" is only emitted if the state is $\neq$ "Focused" for $\ge 80%$ of the  
  window.                                                                                                 
                                                                                                          
  ---                                                                                                     
  3. Output State Definition                                                                              
  ┌───────────────────┬────────────────────────────────────────────────────┬─────────────────────────────┐
  │       State       │                       Logic                        │           Action            │
  ├───────────────────┼────────────────────────────────────────────────────┼─────────────────────────────┤
  │ Focused           │ User is facing the screen, eyes are active.        │ Normal tracking; clear      │
  │                   │                                                    │ buffer.                     │
  ├───────────────────┼────────────────────────────────────────────────────┼─────────────────────────────┤
  │ Possibly          │ Small head movements or eyes glancing at a side    │ Increase monitoring         │
  │ Distracted        │ monitor.                                           │ frequency.                  │
  ├───────────────────┼────────────────────────────────────────────────────┼─────────────────────────────┤
  │ Likely Disengaged │ User is looking away or head is turned             │ Trigger Replay Buffer save. │
  │                   │ significantly.                                     │                             │
  ├───────────────────┼────────────────────────────────────────────────────┼─────────────────────────────┤
  │ Away              │ User has left the chair.                           │ Pause session timers.       │
  └───────────────────┴────────────────────────────────────────────────────┴─────────────────────────────┘
  ---
  4. Replay Buffer Integration                                                                            
                                                                                                          
  The Vision Agent manages the Circular RAM Buffer:                                                       
  - Storage: A deque of the last 900 frames ($\approx 30\text{s}$ at 30 FPS) stored as NumPy arrays.      
  - Trigger: When the State Machine moves from "Focused" $\rightarrow$ "Likely Disengaged".               
  - Execution:                                                                                            
    a. Backend sends a SAVE_CLIP signal.
    b. Agent flushes the deque to an .mp4 file using cv2.VideoWriter.                                     
    c. Agent sends the file_path back to the Backend.                                                     
                                                                                                          
  ---                                                                                                     
  5. Implementation Plan                                                                                  
                                                                                                          
  Phase 1: The Foundation (Basic Detection)
                                                                                                          
  - Set up OpenCV webcam loop.                                                                            
  - Integrate MediaPipe Face Mesh.                                                                        
  - Implement "Away" detection logic.                                                                     
                                                                                                          
  Phase 2: The Geometry (Feature Extraction)                                                              

  - Implement SolvePnP for Head Pose (Pitch, Yaw, Roll).                                                  
  - Implement EAR for blink detection.                                                                    
  - Implement Iris tracking for gaze direction.                                                           
                                                                                                          
  Phase 3: The Logic (State Machine)                                                                      
                                                                                                          
  - Build the Weighted Heuristic Matrix.
  - Implement the 30-frame sliding window for temporal smoothing.                                         
  - Create the confidence scoring system.                                                                 
                                                                                                          
  Phase 4: The Integration (Backend & Buffer)                                                             
                                                                                                          
  - Implement the WebSocket client for real-time event emission.                                          
  - Build the RAM-based circular buffer.                                                                  
  - Implement the "Flush to Disk" mechanism for replay clips.                                             
                                                                                                          
  Phase 5: Optimization                                                                                   
                                                                                                          
  - Profile CPU usage; implement frame-skipping (process every 2nd frame).
  - Tune drift thresholds based on empirical testing.    