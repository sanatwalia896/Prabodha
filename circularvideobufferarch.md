                                                                                                        
  The primary engineering challenge is the Memory-Storage Trade-off. Storing 10 minutes of raw video in   
  RAM is impossible (requiring >100GB). Therefore, we will implement a Tiered Ring-Buffer Architecture    
  that leverages high-speed RAM for immediate events and segmented disk storage for the historical window.
                                                                                                          
  ---                                                                                                     
  1. Storage Architecture: The Tiered Approach                                                            
                                                                                                          
  We divide the storage into three distinct tiers based on the "recency" of the data.                     
                                                                                                          
  Tier 1: The RAM Buffer (The "Instant" Window)                                                           
                                                                                                          
  - Duration: Last 30–60 seconds.                                                                         
  - Format: Raw NumPy arrays (deque).                                                                     
  - Purpose: Zero-latency access for "Save Current Event" triggers. Since these events are often triggered
   by a drift that just happened, we need the immediate past without disk I/O.                            
                                                                                                          
  Tier 2: The Segmented Disk Buffer (The "Rolling" Window)                                                
                                                                                                          
  - Duration: Last 10 minutes.                                                                            
  - Format: Compressed .mp4 segments.                                                                     
  - Structure: The 10-minute window is split into 10 segments of 1 minute each.                           
  - Mechanism: A circular file queue. Once segment 11 is created, segment 1 is deleted.                   
  - Purpose: Provides the "Replay Last 5/10 Mins" functionality without consuming system RAM.             
                                                                                                          
  Tier 3: The Archive (The "Permanent" Window)                                                            
                                                                                                          
  - Duration: Permanent.                                                                                  
  - Format: Optimized .mp4 clips.                                                                         
  - Purpose: Stores only the clips specifically saved by the user or triggered by a significant attention 
  event.                                                                                                  
                                                                                                          
  ---                                                                                                     
  2. Buffer Management Logic                                                                              
                                                                                                          
  The Rolling Segment Strategy                                                                            
                                                                                                          
  To avoid the overhead of constantly rewriting one giant file, we use a Segmented Ring Buffer:           
                                                                                                          
  1. Active Segment: The current minute is written to a temporary current_segment.mp4.                    
  2. Rotation: Every 60 seconds, current_segment.mp4 is renamed to segment_{timestamp}.mp4 and added to a 
  Metadata Index.                                                                                         
  3. Pruning: The system checks the Metadata Index. If more than 10 segments exist, it deletes the oldest 
  file from the disk.                                                                                     
                                                                                                          
  Timestamp Indexing                                                                                      
                                                                                                          
  We maintain a lightweight Index Map (in Redis or a local JSON file):                                    
  - Map<Timestamp, FilePath>                                                                              
  - Example: { "14:05:00": "seg_1405.mp4", "14:06:00": "seg_1406.mp4" ... }                               
  - This allows the system to instantly identify which files to concatenate for a "Last 5 Minutes"        
  request.                                                                                                
                                                                                                          
  ---                                                                                                     
  3. Video Compression Strategy                                                                           
                                                                                                          
  To minimize CPU and Disk impact, we utilize a Lossy-but-Efficient strategy:                             
                                                                                                          
  - Resolution: Downscale from 1080p $\rightarrow$ 720p (1280x720). For attention monitoring, high        
  resolution is unnecessary.                                                                              
  - Frame Rate: Reduce from 30fps $\rightarrow$ 15fps. Focus patterns are slow; 15fps is more than enough 
  to capture a gaze shift.                                                                                
  - Codec: H.264 (via libx264). It offers the best balance of compatibility and compression.              
  - Bitrate: Variable Bit Rate (VBR). Since the user is mostly static, VBR significantly reduces file size
   during "Deep Focus" periods.                                                                           
  - Hardware Acceleration: Use h264_nvenc (NVIDIA) or h264_vaapi (Intel/AMD) to offload encoding from the 
  CPU to the GPU.                                                                                         
                                                                                                          
  ---                                                                                                     
  4. Performance Considerations                                                                           
                                                                                                          
  CPU & I/O Bottlenecks                                                                                   
                                                                                                          
  - Asynchronous Writing: The Vision Agent must not wait for the video to be written to disk. We use a    
  Producer-Consumer Pattern:                                                                              
    - Producer: Vision Agent pushes frames into a Queue.                                                  
    - Consumer: A background thread pulls frames and writes them to the .mp4 segment.                     
  - Zero-Copy Buffer: Use collections.deque for the RAM buffer to ensure $O(1)$ complexity for adding new 
  frames and removing old ones.                                                                           
                                                                                                          
  Memory Usage Calculation (Estimated)                                                                    
                                                                                                          
  - RAM Buffer (60s @ 15fps, 720p, Compressed): $\approx 150\text{MB} - 300\text{MB}$.                    
  - Disk Buffer (10m @ 15fps, 720p, H.264): $\approx 200\text{MB} - 500\text{MB}$ total.                  
  - Result: Negligible impact on a modern production machine.                                             
                                                                                                          
  ---                                                                                                     
  5. User Action Implementation                                                                           
                                                                                                          
  Action: "Save Current Event"                                                                            
                                                                                                          
  1. Trigger: Drift detected.                                                                             
  2. Merge: Combine the last 30s of the RAM Buffer with the end of the current Disk Segment.              
  3. Extract: Use ffmpeg to trim the exact window (e.g., $T-30\text{s}$ to $T+5\text{s}$).                
  4. Save: Write to Tier 3 (Archive) and link to the event_id in PostgreSQL.                              
                                                                                                          
  Action: "Replay Last 5/10 Minutes"                                                                      
                                                                                                          
  1. Query: Retrieve the last 5 or 10 entries from the Timestamp Index.                                   
  2. Concatenate: Use ffmpeg's concat demuxer to merge the .mp4 segments into a single stream.            
  3. Stream: Pipe the merged stream to the React Frontend via the FastAPI /media/replays endpoint. 