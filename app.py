import streamlit as st
try:
    import google.generativeai as genai
except ImportError:
    st.error("Failed to import google-generativeai. Please make sure it's installed.")
    st.stop()
import json
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY")

# Page configuration
st.set_page_config(page_title="AI Learning Assistant", layout="wide")

# Application title and introduction
st.title("🧠 Personalized Learning Assistant")
st.markdown("""
This application helps you master new subjects with personalized learning paths,
adaptive exercises, and AI-powered explanations tailored to your learning style.
""")

# Initialize session state for storing conversation and learning path
if 'initialized' not in st.session_state:
    st.session_state.conversations = {}
    st.session_state.learning_paths = {}
    st.session_state.current_subject = None
    st.session_state.current_module = None
    st.session_state.quiz_active = False
    st.session_state.quiz_questions = []
    st.session_state.quiz_responses = []
    st.session_state.progress = {}
    st.session_state.knowledge_level = "Beginner"  # Initialize with default value
    st.session_state.learning_style = "Visual"     # Initialize with default value
    st.session_state.user_name = "Learner"         # Initialize with default value
    st.session_state.initialized = True

# Sidebar for user profile (API key is now loaded from environment)
with st.sidebar:
    st.header("User Profile")
    user_name = st.text_input("Your Name", value=st.session_state.user_name)
    st.session_state.user_name = user_name
    
    # Learning style selection
    st.subheader("Learning Style")
    learning_style = st.selectbox(
        "Select your preferred learning style",
        ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"],
        index=["Visual", "Auditory", "Reading/Writing", "Kinesthetic"].index(st.session_state.learning_style)
    )
    st.session_state.learning_style = learning_style
    
    # Background knowledge level
    knowledge_level = st.select_slider(
        "Rate your current knowledge level",
        options=["Beginner", "Intermediate", "Advanced", "Expert"],
        value=st.session_state.knowledge_level
    )
    st.session_state.knowledge_level = knowledge_level

    # Add a separator
    st.markdown("---")
    
    # Social media section
    st.markdown("### Connect with Us")
    
    # Social media links with SVG icons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f'<a href="https://www.linkedin.com/in/vitthal-sawant-maharastra01/" target="_blank">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#0077B5"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>'
            f'</a>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f'<a href="https://www.instagram.com/vitthal_sawant__/" target="_blank">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#E4405F"><path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"/></svg>'
            f'</a>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f'<a href="https://wa.me/+918308075485" target="_blank">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#25D366"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>'
            f'</a>',
            unsafe_allow_html=True
        )

# Initialize Gemini API with the key from environment
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        st.session_state.model = model
        
        if 'model_initialized' not in st.session_state:
            st.success("API configured successfully from environment variable!")
            st.session_state.model_initialized = True
    except Exception as e:
        st.error(f"Error configuring API: {e}")
else:
    st.warning("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")

# Function to create a new learning path with improved JSON handling
def create_learning_path(subject):
    if 'model' not in st.session_state:
        return None
    
    prompt = f"""
    Create a comprehensive learning path for teaching {subject} to a {st.session_state.knowledge_level.lower()} level student 
    who prefers {st.session_state.learning_style} learning style. The user's name is {st.session_state.user_name}.
    
    Format the output as a valid JSON object with the following structure:
    {{
        "subject": "{subject}",
        "overview": "Brief overview of what they will learn",
        "modules": [
            {{
                "id": 1,
                "title": "Module title",
                "description": "Short description",
                "content": "Detailed learning content formatted for {st.session_state.learning_style} learners",
                "exercises": [
                    {{
                        "question": "Practice question",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "answer": "Correct option",
                        "explanation": "Detailed explanation of the answer"
                    }}
                ],
                "additional_resources": ["Resource 1", "Resource 2"]
            }}
        ]
    }}
    
    Include 5-7 modules with gradually increasing complexity, and 3-5 exercises per module.
    Ensure content is adapted to {st.session_state.learning_style} learning style by including appropriate examples and explanations.
    
    IMPORTANT: Make sure the JSON is properly formatted with no syntax errors. Use double quotes for all strings and keys, and ensure all quotes and brackets are properly closed.
    """
    
    try:
        response = st.session_state.model.generate_content(prompt)
        content = response.text
        
        # Extract JSON from the response
        json_str = content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        
        # Log the JSON string for debugging
        st.write("Parsing JSON...")
        
        try:
            # Try to parse the JSON
            learning_path = json.loads(json_str)
            st.session_state.learning_paths[subject] = learning_path
            st.session_state.current_subject = subject
            st.session_state.progress[subject] = {
                "started": datetime.now().strftime("%Y-%m-%d"),
                "modules_completed": [],
                "current_module": 0,
                "quiz_scores": []
            }
            return learning_path
        except json.JSONDecodeError as je:
            st.error(f"JSON parsing error: {je}")
            st.write("Attempting to fix JSON format...")
            
            # Attempt to fix common JSON errors
            fixed_json_str = json_str.replace('\n', ' ').replace('\r', '')
            fixed_json_str = fixed_json_str.replace('\\', '\\\\')
            
            # Ensure all quotes are properly escaped
            quote_positions = []
            in_quote = False
            for i, char in enumerate(fixed_json_str):
                if char == '"' and (i == 0 or fixed_json_str[i-1] != '\\'):
                    in_quote = not in_quote
                    quote_positions.append(i)
            
            try:
                learning_path = json.loads(fixed_json_str)
                st.success("JSON fixed successfully!")
                st.session_state.learning_paths[subject] = learning_path
                st.session_state.current_subject = subject
                st.session_state.progress[subject] = {
                    "started": datetime.now().strftime("%Y-%m-%d"),
                    "modules_completed": [],
                    "current_module": 0,
                    "quiz_scores": []
                }
                return learning_path
            except:
                # As a last resort, try using a different prompt for simpler JSON
                st.warning("Trying alternative approach...")
                return create_simpler_learning_path(subject)
    except Exception as e:
        st.error(f"Error creating learning path: {e}")
        return None

# Fallback function for creating a simpler learning path
def create_simpler_learning_path(subject):
    if 'model' not in st.session_state:
        return None
    
    prompt = f"""
    Create a simple learning path for {subject} at {st.session_state.knowledge_level.lower()} level.
    
    Return ONLY a valid JSON object with this exact structure:
    {{
        "subject": "subject name",
        "overview": "brief overview",
        "modules": [
            {{
                "id": 1,
                "title": "title1",
                "description": "description1",
                "content": "content1",
                "exercises": [
                    {{
                        "question": "question1",
                        "options": ["opt1", "opt2", "opt3", "opt4"],
                        "answer": "opt1",
                        "explanation": "explanation1"
                    }}
                ],
                "additional_resources": ["res1", "res2"]
            }}
        ]
    }}
    
    Include 3 modules with 2 exercises each. No markdown formatting in your response.
    """
    
    try:
        response = st.session_state.model.generate_content(prompt)
        content = response.text
        
        # Extract JSON
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        learning_path = json.loads(json_str)
        st.session_state.learning_paths[subject] = learning_path
        st.session_state.current_subject = subject
        st.session_state.progress[subject] = {
            "started": datetime.now().strftime("%Y-%m-%d"),
            "modules_completed": [],
            "current_module": 0,
            "quiz_scores": []
        }
        return learning_path
    except Exception as e:
        st.error(f"Could not create learning path: {e}")
        return None

# Function to generate AI response for questions
def get_ai_explanation(question, subject, module):
    if 'model' not in st.session_state:
        return "Please configure the API key first."
    
    prompt = f"""
    The user {st.session_state.user_name} is learning about {subject}, specifically in the module: {module}.
    They have a {st.session_state.knowledge_level.lower()} knowledge level and prefer {st.session_state.learning_style} learning style.
    
    Their question is: "{question}"
    
    Please provide a helpful, detailed explanation that:
    1. Directly answers their question
    2. Uses examples and explanations suitable for {st.session_state.learning_style} learners
    3. Connects to the broader context of {subject}
    4. Is appropriate for someone at {st.session_state.knowledge_level.lower()} level
    """
    
    try:
        response = st.session_state.model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating explanation: {e}"

# Function to evaluate quiz answers
def evaluate_quiz_answer(user_answer, correct_answer, question, subject, module):
    if 'model' not in st.session_state:
        return "Please configure the API key first."
    
    prompt = f"""
    Evaluate the user's answer to the following question about {subject} from module "{module}".
    
    Question: {question}
    Correct answer: {correct_answer}
    User's answer: {user_answer}
    
    Provide:
    1. Whether the answer is correct, partially correct, or incorrect
    2. A detailed explanation of why
    3. Additional insights or tips to help the user understand better
    4. Explain any misconceptions if present
    
    Remember the user is at {st.session_state.knowledge_level.lower()} level and prefers {st.session_state.learning_style} learning style.
    """
    
    try:
        response = st.session_state.model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error evaluating answer: {e}"

# Function to mark a module as complete
def complete_module(subject, module_id):
    if subject in st.session_state.progress:
        if module_id not in st.session_state.progress[subject]["modules_completed"]:
            st.session_state.progress[subject]["modules_completed"].append(module_id)
        
        # Set the next module as current
        next_module = module_id + 1
        if next_module <= len(st.session_state.learning_paths[subject]["modules"]):
            st.session_state.progress[subject]["current_module"] = next_module
        else:
            st.session_state.progress[subject]["current_module"] = module_id

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["Learning Path", "Study Module", "Practice", "Progress"])

# Tab 1: Learning Path Creation
with tab1:
    st.header("Create Your Learning Journey")
    
    new_subject = st.text_input("What subject would you like to learn?")
    
    if st.button("Create Learning Path", disabled='model' not in st.session_state):
        if new_subject:
            with st.spinner(f"Creating personalized learning path for {new_subject}..."):
                learning_path = create_learning_path(new_subject)
                if learning_path:
                    st.success(f"Learning path for {new_subject} created successfully!")
                    st.session_state.current_module = 1
        else:
            st.warning("Please enter a subject to start learning")
    
    # Display available learning paths
    if st.session_state.learning_paths:
        st.subheader("Your Learning Paths")
        cols = st.columns(3)
        
        i = 0
        for subject, path in st.session_state.learning_paths.items():
            with cols[i % 3]:
                st.info(f"📚 {subject}")
                st.write(path["overview"])
                if st.button(f"Study {subject}", key=f"study_{subject}"):
                    st.session_state.current_subject = subject
                    if subject in st.session_state.progress:
                        current_module = st.session_state.progress[subject]["current_module"]
                        st.session_state.current_module = current_module if current_module > 0 else 1
                    else:
                        st.session_state.current_module = 1
            i += 1

# Tab 2: Study Module
with tab2:
    st.header("Study Module")
    
    if st.session_state.current_subject and st.session_state.current_module:
        subject = st.session_state.current_subject
        module_id = st.session_state.current_module
        
        if subject in st.session_state.learning_paths:
            path = st.session_state.learning_paths[subject]
            
            # Module selection
            all_modules = [f"Module {m['id']}: {m['title']}" for m in path["modules"]]
            selected_module = st.selectbox(
                "Select module to study:", 
                all_modules,
                index=module_id-1
            )
            
            # Extract module ID from selection
            selected_id = int(selected_module.split(":")[0].replace("Module ", ""))
            
            # Find the selected module
            module = next((m for m in path["modules"] if m["id"] == selected_id), None)
            
            if module:
                st.subheader(f"{module['title']}")
                st.write(module["description"])
                
                # Render module content
                st.markdown("## Learning Content")
                st.markdown(module["content"])
                
                # Additional resources
                if module.get("additional_resources"):
                    st.markdown("### Additional Resources")
                    for resource in module["additional_resources"]:
                        st.markdown(f"- {resource}")
                
                # Mark as complete button
                if st.button("Mark Module as Complete"):
                    complete_module(subject, selected_id)
                    st.success(f"Module {selected_id} marked as complete!")
                    st.session_state.current_module = selected_id + 1
                
                # Ask a question about this module
                st.markdown("### Questions about this module?")
                question = st.text_input("Type your question here")
                
                if st.button("Get Explanation", key="ask_question"):
                    if question:
                        with st.spinner("Generating explanation..."):
                            explanation = get_ai_explanation(question, subject, module["title"])
                            st.markdown("### Answer")
                            st.markdown(explanation)
                    else:
                        st.warning("Please enter a question")
    else:
        st.info("Please select or create a learning path first")

# Tab 3: Practice
with tab3:
    st.header("Practice Exercises")
    
    if st.session_state.current_subject and st.session_state.current_module:
        subject = st.session_state.current_subject
        module_id = st.session_state.current_module
        
        if subject in st.session_state.learning_paths:
            path = st.session_state.learning_paths[subject]
            
            # Module selection for practice
            all_modules = [f"Module {m['id']}: {m['title']}" for m in path["modules"]]
            practice_module = st.selectbox(
                "Select module to practice:", 
                all_modules,
                index=module_id-1,
                key="practice_module"
            )
            
            # Extract module ID from selection
            practice_id = int(practice_module.split(":")[0].replace("Module ", ""))
            
            # Find the selected module
            module = next((m for m in path["modules"] if m["id"] == practice_id), None)
            
            if module and "exercises" in module:
                if not st.session_state.quiz_active:
                    if st.button("Start Practice Quiz"):
                        st.session_state.quiz_active = True
                        st.session_state.quiz_questions = module["exercises"]
                        st.session_state.quiz_responses = []
                        st.rerun()
                
                if st.session_state.quiz_active:
                    # Display quiz questions one by one
                    if not st.session_state.quiz_responses or len(st.session_state.quiz_responses) < len(st.session_state.quiz_questions):
                        q_index = len(st.session_state.quiz_responses)
                        question = st.session_state.quiz_questions[q_index]
                        
                        st.subheader(f"Question {q_index + 1}/{len(st.session_state.quiz_questions)}")
                        st.markdown(question["question"])
                        
                        # Multiple choice or text input
                        if "options" in question:
                            user_answer = st.radio(
                                "Select your answer:",
                                question["options"],
                                key=f"q_{q_index}"
                            )
                        else:
                            user_answer = st.text_input(
                                "Your answer:",
                                key=f"q_{q_index}"
                            )
                        
                        if st.button("Submit Answer"):
                            correct_answer = question["answer"]
                            evaluation = evaluate_quiz_answer(
                                user_answer, 
                                correct_answer, 
                                question["question"],
                                subject,
                                module["title"]
                            )
                            
                            st.session_state.quiz_responses.append({
                                "question": question["question"],
                                "user_answer": user_answer,
                                "correct_answer": correct_answer,
                                "evaluation": evaluation,
                                "is_correct": user_answer == correct_answer
                            })
                            
                            st.rerun()
                    else:
                        # Quiz completed - show results
                        st.success("Quiz completed!")
                        
                        # Calculate score
                        correct_count = sum(1 for resp in st.session_state.quiz_responses if resp["is_correct"])
                        total = len(st.session_state.quiz_responses)
                        score = (correct_count / total) * 100
                        
                        st.metric("Score", f"{score:.1f}%", f"{correct_count}/{total} correct")
                        
                        # Store score in progress
                        if subject in st.session_state.progress:
                            if "quiz_scores" not in st.session_state.progress[subject]:
                                st.session_state.progress[subject]["quiz_scores"] = []
                            
                            st.session_state.progress[subject]["quiz_scores"].append({
                                "module_id": practice_id,
                                "score": score,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                        
                        # Review answers
                        st.subheader("Review Your Answers")
                        for i, response in enumerate(st.session_state.quiz_responses):
                            with st.expander(f"Question {i+1}"):
                                st.markdown(response["question"])
                                st.markdown(f"**Your answer:** {response['user_answer']}")
                                st.markdown(f"**Correct answer:** {response['correct_answer']}")
                                st.markdown("### Feedback")
                                st.markdown(response["evaluation"])
                        
                        if st.button("Close Quiz"):
                            st.session_state.quiz_active = False
                            st.session_state.quiz_questions = []
                            st.session_state.quiz_responses = []
                            st.rerun()
            else:
                st.warning("No exercises available for this module")
    else:
        st.info("Please select or create a learning path first")

# Tab 4: Progress Tracking
with tab4:
    st.header("Your Learning Progress")
    
    if st.session_state.progress:
        for subject, progress in st.session_state.progress.items():
            st.subheader(f"Subject: {subject}")
            st.write(f"Started on: {progress['started']}")
            
            # Progress percentage
            if subject in st.session_state.learning_paths:
                total_modules = len(st.session_state.learning_paths[subject]["modules"])
                completed_modules = len(progress["modules_completed"])
                progress_pct = (completed_modules / total_modules) * 100
                
                st.progress(progress_pct / 100)
                st.write(f"Completed {completed_modules} out of {total_modules} modules ({progress_pct:.1f}%)")
                
                # List completed modules
                if completed_modules > 0:
                    st.markdown("### Completed Modules")
                    completed_ids = progress["modules_completed"]
                    for module in st.session_state.learning_paths[subject]["modules"]:
                        if module["id"] in completed_ids:
                            st.success(f"✓ Module {module['id']}: {module['title']}")
                
                # Quiz scores
                if "quiz_scores" in progress and progress["quiz_scores"]:
                    st.markdown("### Quiz Performance")
                    for score_data in progress["quiz_scores"]:
                        module = next((m for m in st.session_state.learning_paths[subject]["modules"] 
                                      if m["id"] == score_data["module_id"]), None)
                        if module:
                            st.write(f"Module {score_data['module_id']} ({module['title']}): " +
                                    f"{score_data['score']:.1f}% on {score_data['date']}")
    else:
        st.info("No learning progress yet. Start by creating a learning path!")

# Footer
st.markdown("---")
st.markdown("© 2025 Personalized Learning Assistant. All rights reserved.❤️ | Powered by Gemini AI | Created with Streamlit")