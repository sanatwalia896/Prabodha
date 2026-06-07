This is the complete Docker architecture for the Focus Awareness and Reflection Platform.               
                                                                                                          
  ⚠️ The "Agent" Paradox: Architect's Note                                                                 
                                                                                                          
  In previous design phases, we identified that the cv-service and activity-service require direct        
  hardware access (Webcam, OS Window Manager). While we can containerize them using Privileged Mode and   
  Device Mapping on Linux, this is notoriously unstable on macOS and Windows.                             
                                                                                                          
  Our Strategy: We will provide the cv-service as a Docker container for Linux-based deployments, but we  
  will implement a "Native-Hybrid" mode where the agents can run as standalone Python processes on the    
  host while the rest of the stack remains Dockerized.                                                    
                                                                                                          
  ---                                                                                                     
  1. Docker Compose Design                                                                                
                                                                                                          
  The system is orchestrated via a single docker-compose.yml file, utilizing a dedicated bridge network to
   isolate the core services from the public internet.                                                    
                                                                                                          
  Container Breakdown                                                                                     
  Container: focus-ui                                                                                     
  Image: nginx:alpine                                                                                     
  Role: Frontend Host                                                                                     
  Key Configuration: Port 80 $\rightarrow$ 80; Serves production React build.                             
  ────────────────────────────────────────                                                                
  Container: focus-backend                                                                                
  Image: python:3.11-slim                                                                                 
  Role: API Orchestrator                                                                                  
  Key Configuration: Port 8000 $\rightarrow$ 8000; Connects to PG, Redis, and Gemma.                      
  ────────────────────────────────────────                                                                
  Container: focus-db                                                                                     
  Image: postgres:16-alpine                                                                               
  Role: Metadata Store                                                                                    
  Key Configuration: Port 5432; Volume for persistence.                                                   
  ────────────────────────────────────────                                                                
  Container: focus-cache                                                                                  
  Image: redis:7-alpine                                                                                   
  Role: State/Queue                                                                                       
  Key Configuration: Port 6379; In-memory state for live monitoring.                                      
  ────────────────────────────────────────                                                                
  Container: focus-ai                                                                                     
  Image: ollama/ollama                                                                                    
  Role: LLM Inference                                                                                     
  Key Configuration: Port 11434; Requires NVIDIA GPU pass-through.                                        
  ────────────────────────────────────────                                                                
  Container: focus-cv                                                                                     
  Image: python:3.11-slim                                                                                 
  Role: Vision Processing                                                                                 
  Key Configuration: Privileged Mode; Access to /dev/video0.                                              
  ---                                                                                                     
  2. Networking & Communication                                                                           
                                                                                                          
  Network Topology                                                                                        
                                                                                                          
  - Network Name: focus-network (Bridge)                                                                  
  - Internal DNS: Containers communicate via service names (e.g., backend calls http://focus-db:5434).    
  - External Exposure: Only focus-ui (80) and focus-backend (8000) are exposed to the host. All other     
  services are internal-only for security.                                                                
                                                                                                          
  Flow Example: Real-time Focus Update                                                                    
                                                                                                          
  focus-cv $\xrightarrow{\text{HTTP/WS}}$ focus-backend $\xrightarrow{\text{SET}}$ focus-cache            
  $\xrightarrow{\text{PUBLISH}}$ focus-ui.                                                                
                                                                                                          
  ---                                                                                                     
  3. Volume & Storage Strategy                                                                            
                                                                                                          
  Since this is a local-first, privacy-centric app, we use Bind Mounts instead of named volumes for       
  critical data. This ensures the user has direct access to their videos and DB files on their own hard   
  drive.                                                                                                  
  ┌──────────────┬─────────────────┬──────────────────────────┬───────────────────────────────────────┐   
  │ Volume Name  │    Host Path    │      Container Path      │                Purpose                │   
  ├──────────────┼─────────────────┼──────────────────────────┼───────────────────────────────────────┤   
  │ db_data      │ ./data/postgres │ /var/lib/postgresql/data │ Database persistence.                 │   
  ├──────────────┼─────────────────┼──────────────────────────┼───────────────────────────────────────┤   
  │ media_store  │ ./data/media    │ /app/media               │ Shared storage for .mp4 replay clips. │   
  ├──────────────┼─────────────────┼──────────────────────────┼───────────────────────────────────────┤   
  │ ai_models    │ ./data/ollama   │ /root/.ollama            │ Storage for Gemma 4 model weights.    │   
  ├──────────────┼─────────────────┼──────────────────────────┼───────────────────────────────────────┤   
  │ config_files │ ./config        │ /app/config              │ User settings and .env files.         │   
  └──────────────┴─────────────────┴──────────────────────────┴───────────────────────────────────────┘   
  Critical Storage Logic: The focus-cv and focus-backend both mount media_store. The CV service writes the
   .mp4 file, and the Backend reads it to stream to the frontend.                                         
                                                                                                          
  ---                                                                                                     
  4. Environment Variables (.env)                                                                         
                                                                                                          
  We use a centralized .env file to manage the environment across all containers.                         
                                                                                                          
  # --- Global ---                                                                                        
  APP_ENV=production                                                                                      
  USER_ID=default_user                                                                                    
                                                                                                          
  # --- Backend ---                                                                                       
  BACKEND_PORT=8000                                                                                       
  DATABASE_URL=postgresql+asyncpg://user:pass@focus-db:5432/focus_db                                      
  REDIS_URL=redis://focus-cache:6379/0                                                                    
  AI_ENGINE_URL=http://focus-ai:11434                                                                     
                                                                                                          
  # --- AI Engine ---                                                                                     
  LLM_MODEL=gemma4:31b                                                                                    
  GPU_ACCELERATION=true                                                                                   
                                                                                                          
  # --- CV Service ---                                                                                    
  CAMERA_DEVICE=/dev/video0                                                                               
  FRAME_WIDTH=640                                                                                         
  FRAME_HEIGHT=480                                                                                        
  BUFFER_DURATION_SEC=600                                                                                 
                                                                                                          
  ---                                                                                                     
  5. Deployment Workflow                                                                                  
                                                                                                          
  Step 1: Infrastructure Setup                                                                            
                                                                                                          
  1. Clone the repository.                                                                                
  2. Configure .env with local paths and DB credentials.                                                  
  3. Create local directories: mkdir -p data/postgres data/media data/ollama.                             
                                                                                                          
  Step 2: Model Initialization                                                                            
                                                                                                          
  Before launching the full stack, we initialize the LLM:                                                 
  docker compose run --rm focus-ai ollama run gemma4 (This pulls the model weights).                      
                                                                                                          
  Step 3: Orchestration                                                                                   
                                                                                                          
  docker compose up -d --build                                                                            
  - This builds the custom images for UI, Backend, and CV.                                                
  - Launches the official images for PG and Redis.                                                        
  - Starts the GPU-accelerated AI engine.                                                                 
                                                                                                          
  Step 4: Verification                                                                                    
                                                                                                          
  1. Check logs: docker compose logs -f focus-cv (Verify webcam access).                                  
  2. Check health: curl http://localhost:8000/health.                                                     
  3. Access UI: Open http://localhost.                                                                    
                                                                                                          
  ---                                                                                                     
  6. Resource Management Plan                                                                             
  ┌───────────────┬───────────┬───────────┬─────────────────────────┐                                     
  │   Component   │ CPU Limit │ RAM Limit │     GPU Requirement     │                                     
  ├───────────────┼───────────┼───────────┼─────────────────────────┤                                     
  │ focus-ui      │ 0.1 Core  │ 128MB     │ None                    │                                     
  ├───────────────┼───────────┼───────────┼─────────────────────────┤                                     
  │ focus-backend │ 0.5 Core  │ 512MB     │ None                    │                                     
  ├───────────────┼───────────┼───────────┼─────────────────────────┤                                     
  │ focus-db      │ 0.5 Core  │ 1GB       │ None                    │                                     
  ├───────────────┼───────────┼───────────┼─────────────────────────┤                                     
  │ focus-cache   │ 0.2 Core  │ 256MB     │ None                    │                                     
  ├───────────────┼───────────┼───────────┼─────────────────────────┤                                     
  │ focus-ai      │ 2.0 Cores │ 16GB+     │ Required (Min 8GB VRAM) │                                     
  ├───────────────┼───────────┼───────────┼─────────────────────────┤                                     
  │ focus-cv      │ 1.0 Core  │ 2GB       │ Recommended (CUDA)      │                                     
  └───────────────┴───────────┴───────────┴─────────────────────────┘                                     
                                                                       