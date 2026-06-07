Design a Gemma 4 integration layer.                                                                     
                                                                                                          
  Inputs:                                                                                                 
                                                                                                          
  - Journal Entries                                                                                       
  - Attention Drift Logs                                                                                  
  - Focus Metrics                                                                                         
  - Historical Trends                                                                                     
  - Application Usage                                                                                     
                                                                                                          
  Capabilities:                                                                                           
                                                                                                          
  - Session Summary                                                                                       
  - Pattern Discovery                                                                                     
  - Weekly Reflection                                                                                     
  - Motivation Generation                                                                                 
  - User Chat Assistant                                                                                   
                                                                                                          
  Generate:                                                                                               
                                                                                                          
  Prompt Templates                                                                                        
  Memory Design                                                                                           
  Context Construction                                                                                    
  RAG Strategy                                                                                            
  Conversation History Strategy                                                                           
  Token Optimization                                                                                      
                                                                                                          
  Design before implementation.                                                                           
                                                                                                          
⏺ This is the design for the Gemma 4 Integration Layer.                                                   
                                                                                                          
  The central challenge of this layer is that LLMs are not built to process raw time-series data (e.g.,   
  10,000 rows of focus scores). If we feed raw logs, we will hit token limits and introduce               
  "hallucinations."                                                                                       
                                                                                                          
  Our solution is a Distillation Pipeline: we transform raw telemetry into Narrative Artifacts before they
   reach Gemma 4.                                                                                         
                                                                                                          
  ---                                                                                                     
  1. Context Construction: The Distillation Pipeline                                                      
                                                                                                          
  Before prompting the LLM, the Backend runs a "Distiller" that converts data into structured text.       
                                                                                                          
  A. Telemetry Distillation (Metrics $\rightarrow$ Narrative)                                             
                                                                                                          
  - Raw: [10:00: 85%, 10:01: 82%, 10:02: 20%]                                                             
  - Narrative: "Focus started strong (80%+) but crashed sharply at 10:02."                                
                                                                                                          
  B. Behavioral Distillation (Events $\rightarrow$ Patterns)                                              
                                                                                                          
  - Raw: [10:02: DRIFT, 10:03: APP_SWITCH (Slack), 10:05: DRIFT]                                          
  - Narrative: "A distraction cluster occurred around 10:02, coinciding with a switch to Slack."          
                                                                                                          
  C. The "Session Artifact"                                                                               
                                                                                                          
  The final context injected into Gemma is a Markdown-formatted document containing:                      
  1. The Quantitative Snapshot: (Avg Score, Total Drift Count, Top 3 Apps).                               
  2. The Timeline of Friction: (Chronological summary of crashes/drifts).                                 
  3. The Subjective Layer: (User's journal entry for that session).                                       
  4. The Historical Baseline: (User's average focus for this time of day).                                
                                                                                                          
  ---                                                                                                     
  2. Prompt Templates                                                                                     
                                                                                                          
  We use a System Persona: "The Cognitive Performance Coach." The coach is objective, encouraging, and    
  evidence-based.                                                                                         
                                                                                                          
  Template A: Session Summary & Reflection                                                                
                                                                                                          
  System: You are a Cognitive Performance Coach. Analyze the provided Session Artifact.                   
  Context: {Session_Artifact}                                                                             
  Instruction: Identify the "Peak Focus Window" and the "Primary Friction Point." Provide a narrative     
  summary and 3 actionable tips.                                                                          
  Constraint: Use only the provided data. Do not diagnose medical conditions.                             
                                                                                                          
  Template B: Pattern Discovery (Longitudinal)                                                            
                                                                                                          
  System: You are a Behavioral Data Analyst.                                                              
  Context: {Comparison_of_5_Sessions}                                                                     
  Instruction: Find correlations between Application Usage and Attention Drift. Does a specific app       
  consistently precede a focus crash?                                                                     
  Output: Provide a "Distraction Correlation Map."                                                        
                                                                                                          
  Template C: Motivation Generation                                                                       
                                                                                                          
  System: You are a motivational strategist.                                                              
  Context: {Recent_Wins_and_Trends}                                                                       
  Instruction: The user is struggling today. Reference a specific "Win" from last week (e.g., a 2-hour    
  deep work block) to encourage them.                                                                     
                                                                                                          
  ---                                                                                                     
  3. Memory Design & RAG Strategy                                                                         
                                                                                                          
  Since we are local-first, we utilize a Hybrid Memory Architecture.                                      
                                                                                                          
  Short-Term Memory (Session-Specific)                                                                    
                                                                                                          
  - Stored in: Redis.                                                                                     
  - Content: The current session's Narrative Artifact.                                                    
  - Lifecycle: Cleared after the session is archived.                                                     
                                                                                                          
  Medium-Term Memory (The "Recent Window")                                                                
                                                                                                          
  - Stored in: PostgreSQL.                                                                                
  - Content: Summaries of the last 14 days of sessions.                                                   
  - Purpose: Used for "Weekly Reflections."                                                               
                                                                                                          
  Long-Term Memory (RAG - Retrieval Augmented Generation)                                                 
                                                                                                          
  To avoid feeding the LLM every session ever recorded, we use Vector Embeddings:                         
  1. Embedding: Every session summary is converted into a vector using a local model (e.g.,               
  all-MiniLM-L6-v2).                                                                                      
  2. Storage: A local vector index (e.g., FAISS or ChromaDB).                                             
  3. Retrieval: When a user asks "Why am I struggling today?", the system searches for the top 3 most     
  similar past sessions where the user felt the same way and injects them as "Similar Past Experiences."  
                                                                                                          
  ---                                                                                                     
  4. Conversation History Strategy                                                                        
                                                                                                          
  To prevent "context drift" and token bloat in the chat assistant:                                       
                                                                                                          
  1. The Sliding Window: Keep the last 6 turns of raw conversation for immediate context.                 
  2. Recursive Summarization: Once the conversation exceeds 10 turns, the AI summarizes the first 4 turns 
  into a "Conversation State" block.                                                                      
  3. The State Block:                                                                                     
    - User Goal: "Wants to stop checking email every 10 mins."                                            
    - AI Advice Given: "Suggested the Pomodoro technique."                                                
    - User Reaction: "Skeptical about timers."                                                            
                                                                                                          
  ---                                                                                                     
  5. Token Optimization                                                                                   
                                                                                                          
  Gemma 4's context window is large, but efficiency ensures speed.                                        
                                                                                                          
  - Markdown over JSON: We use Markdown for prompts. It is more token-efficient and helps the LLM         
  understand hierarchy better than raw JSON.                                                              
  - Temporal Pruning: We remove exact timestamps (e.g., 2026-06-06T10:00:01.443Z) and replace them with   
  relative time (e.g., T+10m).                                                                            
  - Entity Compression: Instead of repeating "The user switched to Visual Studio Code," we use "App:      
  VSCode."                                                                                                
  - Selective Injection: Only inject "Historical Trends" if the user's current session deviates by $>20%$ 
  from their average.                                                                                     
                                                                                                          
  ---                                                                                                     
  6. Logical Flow for a "Reflection" Request                                                              
                                                                                                          
  1. Trigger: User clicks "End Session."                                                                  
  2. Distillation: Backend $\rightarrow$ Distiller $\rightarrow$ Session Artifact.                        
  3. Retrieval: RAG Engine $\rightarrow$ Find 2 similar past sessions $\rightarrow$ Historical Context.   
  4. Assembly: Prompt Template + Session Artifact + Historical Context.                                   
  5. Inference: FastAPI $\rightarrow$ Gemma 4 (Local) $\rightarrow$ Narrative Insight.                    
  6. Persistence: AI Insight $\rightarrow$ PostgreSQL.                                                    
  7. Delivery: WebSocket $\rightarrow$ React Dashboard.    