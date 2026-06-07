The UI/UX goal is to create a "Productivity Command Center" that transitions seamlessly between two     
  modes: Active Mode (high-utility, low-distraction) and Reflective Mode (analytical, calm, and           
  insightful).                                                                                            
                                                                                                          
  ---                                                                                                     
  1. Component Hierarchy                                                                                  
                                                                                                          
  The application is structured as a Single Page Application (SPA) with a persistent layout wrapper.      
                                                                                                          
  Layout Wrapper (AppLayout)                                                                              
                                                                                                          
  - SidebarNav: Collapsible navigation with active-state indicators.                                      
  - TopBar: Global status (Current Focus Level), User Profile, and System Health (Agent connectivity).    
  - MainContent: Dynamic routing area.                                                                    
                                                                                                          
  Page Components                                                                                         
                                                                                                          
  - Dashboard (DashboardPage)                                                                             
    - WelcomeHero: User greeting and current daily streak.                                                
    - QuickStartCard: "Start Focus Session" button with label selector.                                   
    - MetricOverview: Grid of StatCards (Avg Focus, Total Hours, Top Distraction).                        
    - MotivationalQuote: Dynamic quote component.                                                         
  - Focus Session (SessionPage)                                                                           
    - FocusTimer: Minimalist countdown/count-up timer.                                                    
    - FocusGauge: A large, fluid visualizer of current attention state.                                   
    - SessionControls: Pause, Stop, and "I'm Distracted" manual tagger.                                   
  - Live Monitoring (MonitoringPage)                                                                      
    - WebcamCanvas: Live feed with MediaPipe landmark overlays (Iris, Face Mesh).                         
    - TelemetryPanel: Real-time readouts of Yaw, Pitch, and EAR (Eye Aspect Ratio).                       
    - StateLog: A scrolling feed of state transitions (e.g., "Focused $\rightarrow$ Drifted").            
  - Replay Viewer (ReplayPage)                                                                            
    - VideoPlayer: Custom player with playback speed control.                                             
    - EventTimeline: A scrubbable timeline with markers for every "Drift" and "Recovery" event.           
    - ContextPanel: Displays the active app and AI-detected trigger during that specific clip.            
  - Journal (JournalPage)                                                                                 
    - SessionSelector: List of recent sessions to reflect upon.                                           
    - RichTextEditor: Markdown-supported editor for session notes.                                        
    - MoodPicker: Visual emoji-based mood selection.                                                      
  - AI Coach (AICoachPage)                                                                                
    - ChatInterface: Message-bubble layout with streaming text effects.                                   
    - InsightCards: Carousel of AI-generated recommendations for the current session.                     
    - SuggestedPrompts: Quick-action buttons (e.g., "Analyze my fatigue patterns").                       
  - Analytics (AnalyticsPage)                                                                             
    - TrendChart: Focus score over time (Daily/Weekly).                                                   
    - AppDistribution: Donut chart of app usage during focus vs. drift.                                   
    - FocusHeatmap: Grid showing focus intensity by hour of the day.                                      
  - Settings (SettingsPage)                                                                               
    - ProfileSection: Account management.                                                                 
    - CVCalibration: Sliders for drift thresholds and sensitivity.                                        
    - PrivacyToggles: Local storage paths and encryption settings.                                        
                                                                                                          
  ---                                                                                                     
  2. State Management                                                                                     
                                                                                                          
  We will use Zustand for its minimal boilerplate and high performance with frequent updates.             
                                                                                                          
  useSessionStore (Session Lifecycle)                                                                     
                                                                                                          
  - State: isActive, startTime, currentSessionId, overallScore.                                           
  - Actions: startSession(), stopSession(), updateScore().                                                
                                                                                                          
  useLiveStore (High-Frequency Data)                                                                      
                                                                                                          
  - State: currentFocusLevel, gazeDirection, activeApp, isUserAway.                                       
  - Mechanism: Updated every 100ms via WebSocket.                                                         
  - Optimization: Uses transient updates to prevent the entire React tree from re-rendering on every gaze 
  shift.                                                                                                  
                                                                                                          
  useUserStore (Preferences)                                                                              
                                                                                                          
  - State: settings, theme, userId.                                                                       
  - Actions: updateSettings(), toggleTheme().                                                             
                                                                                                          
  ---                                                                                                     
  3. Routing Strategy                                                                                     
                                                                                                          
  Using React Router v6 with a focus on deep-linking for session reviews.                                 
                                                                                                          
  - / $\rightarrow$ Dashboard                                                                             
  - /session $\rightarrow$ Focus Session (Protected: only if session is active)                           
  - /monitor $\rightarrow$ Live Monitoring                                                                
  - /replay/:clipId $\rightarrow$ Replay Viewer (Direct link to a specific event)                         
  - /journal/:sessionId $\rightarrow$ Journal                                                             
  - /coach $\rightarrow$ AI Coach                                                                         
  - /analytics $\rightarrow$ Analytics                                                                    
  - /settings $\rightarrow$ Settings                                                                      
                                                                                                          
  ---                                                                                                     
  4. Data Visualization (Charts)                                                                          
                                                                                                          
  We use Recharts for its SVG-based responsiveness and TypeScript support.                                
  ┌─────────────┬─────────────────────┬────────────────┬─────────────────────────────────┐                
  │ Chart Type  │       Purpose       │     X-Axis     │             Y-Axis              │                
  ├─────────────┼─────────────────────┼────────────────┼─────────────────────────────────┤                
  │ Area Chart  │ Focus Score Trend   │ Time (Minutes) │ Score (0-100)                   │                
  ├─────────────┼─────────────────────┼────────────────┼─────────────────────────────────┤                
  │ Donut Chart │ Distraction Sources │ App Name       │ % of total drift time           │                
  ├─────────────┼─────────────────────┼────────────────┼─────────────────────────────────┤                
  │ Heatmap     │ Peak Productivity   │ Hour of Day    │ Focus Intensity                 │                
  ├─────────────┼─────────────────────┼────────────────┼─────────────────────────────────┤                
  │ Bar Chart   │ Fatigue Correlation │ Day of Week    │ Avg Blink Rate / Pose Deviation │                
  └─────────────┴─────────────────────┴────────────────┴─────────────────────────────────┘                
  ---                                                                                                     
  5. Data Flow                                                                                            
                                                                                                          
  The Live Loop (Websocket)                                                                               
                                                                                                          
  Vision Agent $\rightarrow$ Backend $\rightarrow$ WebSocket $\rightarrow$ useLiveStore $\rightarrow$     
  FocusGauge (Immediate update).                                                                          
                                                                                                          
  The Reflection Loop (REST)                                                                              
                                                                                                          
  User $\rightarrow$ Stop Session $\rightarrow$ Backend $\rightarrow$ Gemma 4 $\rightarrow$ PostgreSQL    
  $\rightarrow$ AI Coach Page (Fetched via GET).                                                          
                                                                                                          
  The Replay Loop (Streaming)                                                                             
                                                                                                          
  Replay Viewer $\rightarrow$ Request /media/replays/{id} $\rightarrow$ FastAPI FileResponse $\rightarrow$
   HTML5 Video Tag.                                                                                       
                                                                                                          
  ---                                                                                                     
  6. Responsive Design & UX                                                                               
                                                                                                          
  Theme & Aesthetics                                                                                      
                                                                                                          
  - Primary Theme: "Deep Space" (Dark mode).                                                              
  - Accent Colors:                                                                                        
    - Focus: Emerald-500                                                                                  
    - Possible Distraction: Amber-400                                                                     
    - Disengaged: Rose-500                                                                                
    - Away: Slate-400                                                                                     
                                                                                                          
  Adaptive Layouts                                                                                        
                                                                                                          
  - Desktop (Primary): Fixed sidebar, multi-column dashboard, high-density analytics.                     
  - Tablet/Mobile (Secondary): Collapsible hamburger menu, stacked stat cards, simplified AI chat.        
  - "Zen Mode": When a session is active, the Sidebar and TopBar fade out, leaving only the FocusTimer and
   FocusGauge to eliminate UI distractions.                                                               
                                                                                                          
  Micro-Interactions                                                                                      
                                                                                                          
  - Smooth Interpolation: The FocusGauge uses CSS transitions to glide between scores rather than jumping.
  - Skeleton Screens: Used during AI generation in the Coach page to indicate the LLM is "thinking."      
  - Haptic-like Visuals: Subtle screen flashes (Amber/Rose) when the user enters a "Distracted" state to  
  nudge them back to focus.      