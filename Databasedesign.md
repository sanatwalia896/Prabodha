 This is the detailed PostgreSQL schema design for the Focus Awareness and Reflection Platform.          
                                                                                                          
  The design follows a Time-Series Optimized Relational Model. Since the platform generates high-frequency
   data (focus scores, attention events), the schema is optimized for rapid writes and efficient temporal 
  querying.                                                                                               
                                                                                                          
  ---                                                                                                     
  1. Entity Relationship (ER) Diagram (Conceptual)                                                        
                                                                                                          
  erDiagram                                                                                               
      USERS ||--o{ SESSIONS : creates                                                                     
      USERS ||--o{ SAVED_CLIPS : bookmarks                                                                
      USERS ||--o{ CHAT_HISTORY : interacts                                                               
      USERS ||--o{ JOURNALS : writes                                                                      
                                                                                                          
      SESSIONS ||--o{ ATTENTION_EVENTS : triggers                                                         
      SESSIONS ||--o{ APP_ACTIVITY : tracks                                                               
      SESSIONS ||--o{ FOCUS_SCORES : records                                                              
      SESSIONS ||--o{ AI_INSIGHTS : generates                                                             
      SESSIONS ||--o{ JOURNALS : relates_to                                                               
      SESSIONS ||--o{ CHAT_HISTORY : contexts                                                             
                                                                                                          
      ATTENTION_EVENTS ||--o| REPLAY_CLIPS : archives                                                     
      REPLAY_CLIPS ||--o{ SAVED_CLIPS : marked_as                                                         
                                                                                                          
      SESSIONS ||--o{ SYSTEM_METRICS : monitors                                                           
                                                                                                          
  ---                                                                                                     
  2. Table Definitions                                                                                    
                                                                                                          
  2.1 Core User & Session Management                                                                      
                                                                                                          
  users                                                                                                   
                                                                                                          
  Stores user profiles and local configuration.                                                           
  ┌───────────────┬─────────────┬────────────────────────────────┬───────────────────────────────────────┐
  │    Column     │  Data Type  │          Constraints           │              Description              │
  ├───────────────┼─────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ user_id       │ UUID        │ PK, Default: gen_random_uuid() │ Unique identifier                     │
  ├───────────────┼─────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ username      │ VARCHAR(50) │ Unique, Not Null               │ User handle                           │
  ├───────────────┼─────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ password_hash │ TEXT        │ Not Null                       │ Argon2/Bcrypt hash                    │
  ├───────────────┼─────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ settings      │ JSONB       │ Default: '{}'                  │ Local config (drift thresholds, etc.) │
  ├───────────────┼─────────────┼────────────────────────────────┼───────────────────────────────────────┤
  │ created_at    │ TIMESTAMPTZ │ Default: now()                 │ Account creation date                 │
  └───────────────┴─────────────┴────────────────────────────────┴───────────────────────────────────────┘
  - Indexes: idx_users_username (B-Tree)                                                                  
                                                                                                          
  sessions                                                                                                
                                                                                                          
  Represents a single period of tracked productivity.                                                     
  Column: session_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: PK, Default: gen_random_uuid()                                                             
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: user_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ users.user_id                                                             
  Description: Owner of the session                                                                       
  ────────────────────────────────────────                                                                
  Column: start_time                                                                                      
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Not Null                                                                                   
  Description: Session start                                                                              
  ────────────────────────────────────────                                                                
  Column: end_time                                                                                        
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Nullable                                                                                   
  Description: Session end (Null if active)                                                               
  ────────────────────────────────────────                                                                
  Column: label                                                                                           
  Data Type: VARCHAR(100)                                                                                 
  Constraints: Nullable                                                                                   
  Description: User-defined name (e.g., "Deep Work")                                                      
  ────────────────────────────────────────                                                                
  Column: overall_score                                                                                   
  Data Type: FLOAT                                                                                        
  Constraints: Nullable                                                                                   
  Description: Calculated aggregate focus score                                                           
  ────────────────────────────────────────                                                                
  Column: created_at                                                                                      
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Default: now()                                                                             
  Description: Record creation                                                                            
  - Indexes: idx_sessions_user_time (Composite: user_id, start_time)                                      
                                                                                                          
  ---                                                                                                     
  2.2 High-Frequency Event Data                                                                           
                                                                                                          
  attention_events                                                                                        
                                                                                                          
  Specific moments where attention shifted or fatigue was detected.                                       
  Column: event_id                                                                                        
  Data Type: UUID                                                                                         
  Constraints: PK                                                                                         
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: session_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ sessions.session_id                                                       
  Description: Parent session                                                                             
  ────────────────────────────────────────                                                                
  Column: timestamp                                                                                       
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Not Null                                                                                   
  Description: Precise moment of event                                                                    
  ────────────────────────────────────────                                                                
  Column: event_type                                                                                      
  Data Type: EVENT_TYPE_ENUM                                                                              
  Constraints: Not Null                                                                                   
  Description: DRIFT, FATIGUE, RECOVERY, FOCUS_GAIN                                                       
  ────────────────────────────────────────                                                                
  Column: confidence                                                                                      
  Data Type: FLOAT                                                                                        
  Constraints: Check(0..1)                                                                                
  Description: CV Model confidence score                                                                  
  ────────────────────────────────────────                                                                
  Column: metadata                                                                                        
  Data Type: JSONB                                                                                        
  Constraints: Default: '{}'                                                                              
  Description: Detailed CV data (gaze angle, blink rate)                                                  
  - Indexes: idx_events_session_time (Composite: session_id, timestamp)                                   
                                                                                                          
  app_activity                                                                                            
                                                                                                          
  Logs changes in the active desktop application.                                                         
  ┌──────────────┬──────────────┬──────────────────────────────────────┬─────────────────────────────────┐
  │    Column    │  Data Type   │             Constraints              │           Description           │
  ├──────────────┼──────────────┼──────────────────────────────────────┼─────────────────────────────────┤
  │ activity_id  │ BIGINT       │ PK, Identity                         │ Unique identifier               │
  ├──────────────┼──────────────┼──────────────────────────────────────┼─────────────────────────────────┤
  │ session_id   │ UUID         │ FK $\rightarrow$ sessions.session_id │ Parent session                  │
  ├──────────────┼──────────────┼──────────────────────────────────────┼─────────────────────────────────┤
  │ timestamp    │ TIMESTAMPTZ  │ Not Null                             │ Time of app switch              │
  ├──────────────┼──────────────┼──────────────────────────────────────┼─────────────────────────────────┤
  │ app_name     │ VARCHAR(255) │ Not Null                             │ Process name (e.g., "code.exe") │
  ├──────────────┼──────────────┼──────────────────────────────────────┼─────────────────────────────────┤
  │ window_title │ TEXT         │ Nullable                             │ Title of the active window      │
  ├──────────────┼──────────────┼──────────────────────────────────────┼─────────────────────────────────┤
  │ duration     │ INTERVAL     │ Nullable                             │ How long the app was active     │
  └──────────────┴──────────────┴──────────────────────────────────────┴─────────────────────────────────┘
  - Indexes: idx_app_session (B-Tree on session_id)                                                       
                                                                                                          
  focus_scores                                                                                            
                                                                                                          
  Time-series data for the real-time focus meter.                                                         
  ┌────────────┬──────────────────┬──────────────────────────────────────┬───────────────────┐            
  │   Column   │    Data Type     │             Constraints              │    Description    │            
  ├────────────┼──────────────────┼──────────────────────────────────────┼───────────────────┤            
  │ score_id   │ BIGINT           │ PK, Identity                         │ Unique identifier │            
  ├────────────┼──────────────────┼──────────────────────────────────────┼───────────────────┤            
  │ session_id │ UUID             │ FK $\rightarrow$ sessions.session_id │ Parent session    │            
  ├────────────┼──────────────────┼──────────────────────────────────────┼───────────────────┤            
  │ timestamp  │ TIMESTAMPTZ      │ Not Null                             │ Time of sample    │            
  ├────────────┼──────────────────┼──────────────────────────────────────┼───────────────────┤            
  │ score      │ FLOAT            │ Check(0..100)                        │ Focus percentage  │            
  ├────────────┼──────────────────┼──────────────────────────────────────┼───────────────────┤            
  │ level      │ FOCUS_LEVEL_ENUM │ Not Null                             │ DEEP, LIGHT, NONE │            
  └────────────┴──────────────────┴──────────────────────────────────────┴───────────────────┘            
  - Indexes: idx_scores_session_time (Composite: session_id, timestamp)                                   
                                                                                                          
  ---                                                                                                     
  2.3 Video & Media Layer                                                                                 
                                                                                                          
  replay_clips                                                                                            
                                                                                                          
  Metadata for the automatically saved video buffers.                                                     
  Column: clip_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: PK                                                                                         
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: event_id                                                                                        
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ attention_events.event_id                                                 
  Description: Triggering event                                                                           
  ────────────────────────────────────────                                                                
  Column: file_path                                                                                       
  Data Type: TEXT                                                                                         
  Constraints: Not Null                                                                                   
  Description: Local absolute path to .mp4                                                                
  ────────────────────────────────────────                                                                
  Column: start_timestamp                                                                                 
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Not Null                                                                                   
  Description: Start of the buffer                                                                        
  ────────────────────────────────────────                                                                
  Column: end_timestamp                                                                                   
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Not Null                                                                                   
  Description: End of the buffer                                                                          
  ────────────────────────────────────────                                                                
  Column: is_deleted                                                                                      
  Data Type: BOOLEAN                                                                                      
  Constraints: Default: false                                                                             
  Description: Soft delete flag                                                                           
  - Indexes: idx_clips_event (B-Tree on event_id)                                                         
                                                                                                          
  saved_clips                                                                                             
                                                                                                          
  User-curated "bookmarks" of important focus/drift moments.                                              
  Column: save_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: PK                                                                                         
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: clip_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ replay_clips.clip_id                                                      
  Description: The source clip                                                                            
  ────────────────────────────────────────                                                                
  Column: user_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ users.user_id                                                             
  Description: User who saved it                                                                          
  ────────────────────────────────────────                                                                
  Column: save_note                                                                                       
  Data Type: TEXT                                                                                         
  Constraints: Nullable                                                                                   
  Description: User's observation on why this was saved                                                   
  ────────────────────────────────────────                                                                
  Column: created_at                                                                                      
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Default: now()                                                                             
  Description: Bookmark date                                                                              
  ---                                                                                                     
  2.4 AI & Reflection Layer                                                                               
                                                                                                          
  journals                                                                                                
                                                                                                          
  User's manual reflections on a specific session.                                                        
  Column: journal_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: PK                                                                                         
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: session_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ sessions.session_id                                                       
  Description: Related session                                                                            
  ────────────────────────────────────────                                                                
  Column: user_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ users.user_id                                                             
  Description: Author                                                                                     
  ────────────────────────────────────────                                                                
  Column: content                                                                                         
  Data Type: TEXT                                                                                         
  Constraints: Not Null                                                                                   
  Description: Journal entry text                                                                         
  ────────────────────────────────────────                                                                
  Column: mood                                                                                            
  Data Type: VARCHAR(20)                                                                                  
  Constraints: Nullable                                                                                   
  Description: User-selected mood (e.g., "Productive")                                                    
  ────────────────────────────────────────                                                                
  Column: created_at                                                                                      
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Default: now()                                                                             
  Description: Entry date                                                                                 
  ai_insights                                                                                             
                                                                                                          
  Outputs from Gemma 4 based on session analysis.                                                         
  Column: insight_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: PK                                                                                         
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: session_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ sessions.session_id                                                       
  Description: Analyzed session                                                                           
  ────────────────────────────────────────                                                                
  Column: user_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ users.user_id                                                             
  Description: Recipient                                                                                  
  ────────────────────────────────────────                                                                
  Column: summary                                                                                         
  Data Type: TEXT                                                                                         
  Constraints: Not Null                                                                                   
  Description: Narrative session summary                                                                  
  ────────────────────────────────────────                                                                
  Column: recommendations                                                                                 
  Data Type: JSONB                                                                                        
  Constraints: Default: '[]'                                                                              
  Description: List of actionable coaching tips                                                           
  ────────────────────────────────────────                                                                
  Column: created_at                                                                                      
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Default: now()                                                                             
  Description: Generation date                                                                            
  chat_history                                                                                            
                                                                                                          
  Conversations between the user and the AI about their focus data.                                       
  Column: message_id                                                                                      
  Data Type: BIGINT                                                                                       
  Constraints: PK, Identity                                                                               
  Description: Unique identifier                                                                          
  ────────────────────────────────────────                                                                
  Column: user_id                                                                                         
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ users.user_id                                                             
  Description: The user                                                                                   
  ────────────────────────────────────────                                                                
  Column: session_id                                                                                      
  Data Type: UUID                                                                                         
  Constraints: FK $\rightarrow$ sessions.session_id                                                       
  Description: Context (if discussing a specific session)                                                 
  ────────────────────────────────────────                                                                
  Column: role                                                                                            
  Data Type: VARCHAR(10)                                                                                  
  Constraints: Not Null                                                                                   
  Description: USER or AI                                                                                 
  ────────────────────────────────────────                                                                
  Column: content                                                                                         
  Data Type: TEXT                                                                                         
  Constraints: Not Null                                                                                   
  Description: Message text                                                                               
  ────────────────────────────────────────                                                                
  Column: timestamp                                                                                       
  Data Type: TIMESTAMPTZ                                                                                  
  Constraints: Default: now()                                                                             
  Description: Message time                                                                               
  - Indexes: idx_chat_context (Composite: user_id, session_id)                                            
                                                                                                          
  ---                                                                                                     
  2.5 Auxiliary Systems                                                                                   
                                                                                                          
  quotes                                                                                                  
                                                                                                          
  Motivational quotes for the dashboard.                                                                  
  ┌───────────┬──────────────┬───────────────┬───────────────────────────────────┐                        
  │  Column   │  Data Type   │  Constraints  │            Description            │                        
  ├───────────┼──────────────┼───────────────┼───────────────────────────────────┤                        
  │ quote_id  │ SERIAL       │ PK            │ Unique identifier                 │                        
  ├───────────┼──────────────┼───────────────┼───────────────────────────────────┤                        
  │ text      │ TEXT         │ Not Null      │ Quote content                     │                        
  ├───────────┼──────────────┼───────────────┼───────────────────────────────────┤                        
  │ author    │ VARCHAR(100) │ Nullable      │ Author name                       │                        
  ├───────────┼──────────────┼───────────────┼───────────────────────────────────┤                        
  │ category  │ VARCHAR(50)  │ Nullable      │ e.g., "Focus", "Rest", "Ambition" │                        
  ├───────────┼──────────────┼───────────────┼───────────────────────────────────┤                        
  │ is_active │ BOOLEAN      │ Default: true │ Visibility toggle                 │                        
  └───────────┴──────────────┴───────────────┴───────────────────────────────────┘                        
  system_metrics                                                                                          
                                                                                                          
  Performance telemetry for the agents.                                                                   
  ┌────────────┬─────────────┬────────────────┬──────────────────────────────────────┐                    
  │   Column   │  Data Type  │  Constraints   │             Description              │                    
  ├────────────┼─────────────┼────────────────┼──────────────────────────────────────┤                    
  │ metric_id  │ BIGINT      │ PK, Identity   │ Unique identifier                    │                    
  ├────────────┼─────────────┼────────────────┼──────────────────────────────────────┤                    
  │ timestamp  │ TIMESTAMPTZ │ Default: now() │ Sample time                          │                    
  ├────────────┼─────────────┼────────────────┼──────────────────────────────────────┤                    
  │ agent_type │ VARCHAR(20) │ Not Null       │ VISION or ACTIVITY                   │                    
  ├────────────┼─────────────┼────────────────┼──────────────────────────────────────┤                    
  │ cpu_usage  │ FLOAT       │ Nullable       │ CPU %                                │                    
  ├────────────┼─────────────┼────────────────┼──────────────────────────────────────┤                    
  │ mem_usage  │ FLOAT       │ Nullable       │ RAM usage in MB                      │                    
  ├────────────┼─────────────┼────────────────┼──────────────────────────────────────┤                    
  │ fps        │ FLOAT       │ Nullable       │ Frames per second (for Vision agent) │                    
  └────────────┴─────────────┴────────────────┴──────────────────────────────────────┘                    
  ---                                                                                                     
  3. Relationship Explanations                                                                            
                                                                                                          
  1. User $\rightarrow$ Session (1:N): A user can have thousands of sessions over time, but each session  
  belongs to exactly one user.                                                                            
  2. Session $\rightarrow$ Events/Activity/Scores (1:N): The session is the "container." All temporal data
   points are linked to a session_id to allow the frontend to query "everything that happened in Session  
  X."                                                                                                     
  3. Attention Event $\rightarrow$ Replay Clip (1:1/N): A "Drift" event triggers the saving of a clip.    
  While usually 1:1, a single event could potentially trigger multiple clips if the buffer is fragmented. 
  4. Replay Clip $\rightarrow$ Saved Clip (1:N): A clip is a raw file. A "Saved Clip" is a user's         
  intentional bookmark of that file with a personal note.                                                 
  5. Session $\rightarrow$ AI Insights/Journal (1:1): Each session concludes with one AI-generated        
  reflection and one user-written journal entry to create a "closed-loop" of reflection.                  
  6. User/Session $\rightarrow$ Chat History (1:N): Chat is flexible. It can be a general conversation    
  about progress (linked to user_id) or a specific deep-dive into a session (linked to session_id).       
                                                                                                          
  4. Technical Design Notes                                                                               
                                                                                                          
  - UUIDs vs BIGINT: I used UUID for primary keys of high-level entities (Users, Sessions, Events) to     
  prevent ID enumeration and facilitate potential future distributed synchronization. I used BIGINT for   
  high-frequency time-series data (FocusScores, AppActivity, SystemMetrics) to optimize index size and    
  write speed.                                                                                            
  - JSONB Usage: settings and metadata use JSONB to allow the CV models to evolve (e.g., adding a new "Eye
   Gaze Vector" field) without requiring a database migration.                                            
  - Timezone Awareness: All time columns use TIMESTAMPTZ to ensure that the local-first platform handles  
  daylight savings and user travel correctly.                                                             
  - Enum Types: I've specified EVENT_TYPE_ENUM and FOCUS_LEVEL_ENUM to ensure data consistency across the 
  AI and Backend layers. 