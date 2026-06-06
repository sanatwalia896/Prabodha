⏺ This is the complete backend design for the Focus Awareness and Reflection Platform.                    
                                                                                                          
  The architecture follows a Layered Clean Architecture pattern. By separating the API, Service, and      
  Repository layers, we ensure that the business logic (e.g., how a focus score is calculated) is         
  independent of the database technology or the API framework.                                            
                                                                                                          
  ---                                                                                                     
  1. Folder Structure                                                                                     
                                                                                                          
  focus_backend/                                                                                          
  ├── app/                                                                                                
  │   ├── api/                    # API Layer (Routers & Dependencies)                                    
  │   │   ├── v1/                                                                                         
  │   │   │   ├── auth.py         # Auth endpoints                                                        
  │   │   │   ├── sessions.py     # Session management                                                    
  │   │   │   ├── events.py       # Event ingestion (Agents)                                              
  │   │   │   ├── ai.py           # AI Reflection & Chat                                                  
  │   │   │   ├── media.py        # Replay clips                                                          
  │   │   │   └── analytics.py    # Trends & stats                                                        
  │   │   └── deps.py             # Common dependencies (get_db, get_current_user)                        
  │   ├── core/                   # Core Configuration                                                    
  │   │   ├── config.py           # Env vars, Pydantic Settings                                           
  │   │   ├── security.py        # JWT, Hashing, Password logic                                           
  │   │   └── constants.py        # Enums, Fixed thresholds                                               
  │   ├── db/                     # Database Layer                                                        
  │   │   ├── session.py          # SQLAlchemy engine & session local                                     
  │   │   ├── base_model.py       # Declarative Base                                                      
  │   │   └── models/             # SQLAlchemy Table Models (mapped to PG schema)                         
  │   │       ├── user.py                                                                                 
  │   │       ├── session.py                                                                              
  │   │       ├── event.py                                                                                
  │   │       └── ... (others)                                                                            
  │   ├── repositories/            # Repository Layer (Pure DB queries)                                   
  │   │   ├── base_repo.py        # Generic CRUD                                                          
  │   │   ├── user_repo.py                                                                                
  │   │   ├── session_repo.py                                                                             
  │   │   └── event_repo.py                                                                               
  │   ├── services/                # Service Layer (Business Logic)                                       
  │   │   ├── auth_service.py     # Logic for login/token generation                                      
  │   │   ├── session_service.py   # Logic for session lifecycle & aggregation                            
  │   │   ├── event_service.py    # Logic for drift detection & trigger signals                           
  │   │   ├── ai_service.py        # Integration with Gemma 4/Ollama                                      
  │   │   └── media_service.py    # Video file system management                                          
  │   ├── schemas/                # Pydantic Models (Request/Response validation)                         
  │   │   ├── user.py                                                                                     
  │   │   ├── session.py                                                                                  
  │   │   ├── event.py                                                                                    
  │   │   └── ai.py                                                                                       
  │   ├── workers/               # Background Task Processors                                             
  │   │   ├── reflection_worker.py # Triggers AI on session end                                           
  │   │   └── metrics_worker.py    # Periodic aggregation of focus scores                                 
  │   └── main.py                 # Application entry point & WebSocket config                            
  ├── tests/                      # Pytest suite                                                          
  ├── .env                        # Local environment variables                                           
  └── docker-compose.yml          # Backend, DB, Redis, AI Engine orchestration                           
                                                                                                          
  ---                                                                                                     
  2. Component Responsibilities                                                                           
                                                                                                          
  API Layer                                                                                               
                                                                                                          
  - Responsibility: Handle HTTP requests, validate input via Pydantic, and return standardized JSON       
  responses.                                                                                              
  - Logic: Zero business logic. It only calls the corresponding Service method.                           
                                                                                                          
  Service Layer                                                                                           
                                                                                                          
  - Responsibility: The "Brain" of the app. It manages transactions, enforces business rules, and         
  coordinates between different repositories.                                                             
  - Example: When session_service.end_session() is called, it updates the DB $\rightarrow$ calculates the 
  final score $\rightarrow$ triggers the reflection_worker to call Gemma 4.                               
                                                                                                          
  Repository Layer                                                                                        
                                                                                                          
  - Responsibility: Abstract the database. All SQL queries live here.                                     
  - Benefit: If we switch from PostgreSQL to a Time-Series DB (like TimescaleDB) for events, we only      
  change the Repository layer.                                                                            
                                                                                                          
  Authentication Layer                                                                                    
                                                                                                          
  - Mechanism: JWT (JSON Web Tokens) with a local secret.                                                 
  - Flow: User Login $\rightarrow$ Auth Service $\rightarrow$ JWT Issued $\rightarrow$ Frontend stores in 
  HttpOnly Cookie/LocalStorage $\rightarrow$ Passed in Authorization Header.                              
                                                                                                          
  Database Layer                                                                                          
                                                                                                          
  - SQLAlchemy 2.0: Using async sessions for high-concurrency event ingestion.                            
  - Migrations: Managed via Alembic.                                                                      
                                                                                                          
  Background Workers                                                                                      
                                                                                                          
  - Tooling: FastAPI BackgroundTasks for simple jobs; Celery or RQ (via Redis) for heavy AI inference.    
  - Key Job: ReflectionWorker polls the session end event, gathers all AttentionEvents and AppActivity,   
  and sends a structured prompt to the AI Engine.                                                         
                                                                                                          
  ---                                                                                                     
  3. API Endpoints Specification                                                                          
                                                                                                          
  🔐 Authentication & User                                                                                
  ┌────────┬─────────────────┬────────────────────┬─────────────────┬─────────────────────────┐           
  │ Method │      Route      │   Request Schema   │ Response Schema │       Description       │           
  ├────────┼─────────────────┼────────────────────┼─────────────────┼─────────────────────────┤           
  │ POST   │ /auth/register  │ UserCreate         │ UserOut         │ Create local account    │           
  ├────────┼─────────────────┼────────────────────┼─────────────────┼─────────────────────────┤           
  │ POST   │ /auth/login     │ UserLogin          │ Token           │ Get JWT access token    │           
  ├────────┼─────────────────┼────────────────────┼─────────────────┼─────────────────────────┤           
  │ GET    │ /users/me       │ N/A                │ UserOut         │ Current user profile    │           
  ├────────┼─────────────────┼────────────────────┼─────────────────┼─────────────────────────┤           
  │ PATCH  │ /users/settings │ UserSettingsUpdate │ UserOut         │ Update drift thresholds │           
  └────────┴─────────────────┴────────────────────┴─────────────────┴─────────────────────────┘           
  ⏱️ Session Management                                                                                   
  ┌────────┬─────────────────────┬────────────────┬──────────────────┬──────────────────────────┐         
  │ Method │        Route        │ Request Schema │ Response Schema  │       Description        │         
  ├────────┼─────────────────────┼────────────────┼──────────────────┼──────────────────────────┤         
  │ POST   │ /sessions           │ SessionCreate  │ SessionOut       │ Start a focus session    │         
  ├────────┼─────────────────────┼────────────────┼──────────────────┼──────────────────────────┤         
  │ POST   │ /sessions/{id}/stop │ N/A            │ SessionOut       │ End session & trigger AI │         
  ├────────┼─────────────────────┼────────────────┼──────────────────┼──────────────────────────┤         
  │ GET    │ /sessions           │ SessionQuery   │ List[SessionOut] │ History of sessions      │         
  ├────────┼─────────────────────┼────────────────┼──────────────────┼──────────────────────────┤         
  │ GET    │ /sessions/{id}      │ N/A            │ SessionDetail    │ Full session metrics     │         
  └────────┴─────────────────────┴────────────────┴──────────────────┴──────────────────────────┘         
  📡 Event Ingestion (Agent Interface)                                                                    
  ┌────────┬───────────────────┬──────────────────┬─────────────────┬───────────────────────────┐         
  │ Method │       Route       │  Request Schema  │ Response Schema │        Description        │         
  ├────────┼───────────────────┼──────────────────┼─────────────────┼───────────────────────────┤         
  │ POST   │ /events/attention │ AttentionEventIn │ EventOut        │ Log CV drift/fatigue      │         
  ├────────┼───────────────────┼──────────────────┼─────────────────┼───────────────────────────┤         
  │ POST   │ /events/activity  │ ActivityEventIn  │ EventOut        │ Log App/Window switch     │         
  ├────────┼───────────────────┼──────────────────┼─────────────────┼───────────────────────────┤         
  │ POST   │ /events/score     │ FocusScoreIn     │ ScoreOut        │ Log real-time focus %     │         
  ├────────┼───────────────────┼──────────────────┼─────────────────┼───────────────────────────┤         
  │ WS     │ /ws/live-state    │ N/A              │ RealtimeState   │ Bi-directional state sync │         
  └────────┴───────────────────┴──────────────────┴─────────────────┴───────────────────────────┘         
  🤖 AI Reflection & Chat                                                                                 
  ┌────────┬──────────────────────────┬────────────────┬──────────────────────┬──────────────────────────┐
  │ Method │          Route           │ Request Schema │   Response Schema    │       Description        │
  ├────────┼──────────────────────────┼────────────────┼──────────────────────┼──────────────────────────┤
  │ GET    │ /ai/reflect/{session_id} │ N/A            │ AIInsightOut         │ Fetch session reflection │
  ├────────┼──────────────────────────┼────────────────┼──────────────────────┼──────────────────────────┤
  │ POST   │ /ai/chat                 │ ChatMessageIn  │ ChatMessageOut       │ Interactive AI coaching  │
  ├────────┼──────────────────────────┼────────────────┼──────────────────────┼──────────────────────────┤
  │ GET    │ /ai/chat/history         │ ChatQuery      │ List[ChatMessageOut] │ Retrieve conversation    │
  └────────┴──────────────────────────┴────────────────┴──────────────────────┴──────────────────────────┘
  📹 Media & Replays                                                                                      
  ┌────────┬──────────────────────────┬────────────────┬─────────────────┬─────────────────────────┐      
  │ Method │          Route           │ Request Schema │ Response Schema │       Description       │      
  ├────────┼──────────────────────────┼────────────────┼─────────────────┼─────────────────────────┤      
  │ GET    │ /media/replays/{clip_id} │ N/A            │ FileResponse    │ Stream .mp4 replay      │      
  ├────────┼──────────────────────────┼────────────────┼─────────────────┼─────────────────────────┤      
  │ POST   │ /media/save/{clip_id}    │ SaveClipIn     │ SavedClipOut    │ Bookmark a replay clip  │      
  ├────────┼──────────────────────────┼────────────────┼─────────────────┼─────────────────────────┤      
  │ DELETE │ /media/clips/{clip_id}   │ N/A            │ Success         │ Delete local video file │      
  └────────┴──────────────────────────┴────────────────┴─────────────────┴─────────────────────────┘      
  📈 Analytics                                                                                            
  ┌────────┬───────────────────┬────────────────┬─────────────────┬───────────────────────┐               
  │ Method │       Route       │ Request Schema │ Response Schema │      Description      │               
  ├────────┼───────────────────┼────────────────┼─────────────────┼───────────────────────┤               
  │ GET    │ /analytics/trends │ TrendQuery     │ TrendDataOut    │ Focus score over time │               
  ├────────┼───────────────────┼────────────────┼─────────────────┼───────────────────────┤               
  │ GET    │ /analytics/apps   │ SessionQuery   │ AppUsageOut     │ Most distracting apps │               
  ├────────┼───────────────────┼────────────────┼─────────────────┼───────────────────────┤               
  │ GET    │ /analytics/peak   │ N/A            │ PeakHourOut     │ User's "Golden Hours" │               
  └────────┴───────────────────┴────────────────┴─────────────────┴───────────────────────┘               
  ---                                                                                                     
  4. Critical Data Schemas (Pydantic)                                                                     
                                                                                                          
  Example: AttentionEventIn (Request)                                                                     
  {                                                                                                       
    "session_id": "uuid",                                                                                 
    "event_type": "DRIFT",                                                                                
    "confidence": 0.92,                                                                                   
    "metadata": {                                                                                         
      "gaze_direction": "left",                                                                           
      "blink_rate": 12,                                                                                   
      "head_pose": {"pitch": 5, "yaw": -10}                                                               
    }                                                                                                     
  }                                                                                                       
                                                                                                          
  Example: AIInsightOut (Response)                                                                        
  {                                                                                                       
    "insight_id": "uuid",                                                                                 
    "summary": "You had a strong start, but focus dropped significantly after 2 PM...",                   
    "recommendations": [                                                                                  
      "Take a 10min walk when fatigue is detected at 2 PM",                                               
      "Limit Slack notifications during 'Deep Work' labels"                                               
    ],                                                                                                    
    "created_at": "timestamp"
  }