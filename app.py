import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import tempfile

def main():
    st.set_page_config(page_title="Posture and Scoliosis Assessment Tool", layout="wide")
    st.title("🧍‍♂️ Posture and Scoliosis Assessment Tool")
    st.write("Welcome! This tool will help assess your posture and identify potential issues related to scoliosis.")

    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = {}

    def reset_assessment():
        st.session_state.score = 0
        st.session_state.responses = {}
        st.experimental_rerun()

    # Collect demographic information
    st.header("1. Demographic Information")
    age = st.number_input("What is your age?", min_value=5, max_value=100, value=20, step=1)
    gender = st.radio("What is your gender?", ("Male", "Female", "Prefer not to say", "Other"))
    height = st.number_input("What is your height? (cm)", min_value=50, max_value=250, value=170, step=1)
    weight = st.number_input("What is your weight? (kg)", min_value=20, max_value=200, value=70, step=1)
    occupation = st.selectbox("What is your primary occupation?", ["Student", "Office Worker", "Manual Labor", "Other"])

    st.markdown("---")

    # Collect symptom assessment
    st.header("2. Symptom Assessment")
    pain_present = st.radio("Do you experience any pain in your back or neck?", ("Yes", "No"), key='pain_present')

    if pain_present == "Yes":
        pain_location = st.multiselect("Where do you primarily feel the pain?", ["Upper Back", "Lower Back", "Neck", "Shoulders", "Other"])
        pain_severity = st.slider("On a scale of 1 to 10, how would you rate your pain?", 1, 10, 5)
        pain_duration = st.selectbox("How long have you been experiencing this pain?", ["Less than a month", "1-6 months", "6 months to a year", "Over a year"])
        symptom_onset = st.radio("Did your pain start gradually or suddenly?", ("Gradually", "Suddenly"))
        activity_related_pain = st.radio("Does physical activity worsen your pain?", ("Yes", "No"))

    st.markdown("---")

    # Collect medical and personal history
    st.header("3. Medical and Personal History")
    previous_diagnosis = st.radio("Have you been previously diagnosed with scoliosis or any other spinal condition?", ("Yes", "No"))
    family_history = st.radio("Is there a family history of scoliosis or spinal issues?", ("Yes", "No"))
    past_injuries = st.radio("Have you had any back or spinal injuries in the past?", ("Yes", "No"))
    physical_activity_level = st.selectbox("How would you describe your regular physical activity level?", ["Sedentary", "Lightly active", "Moderately active", "Very active"])

    st.markdown("---")

    # Collect lifestyle and ergonomics information
    st.header("4. Lifestyle and Ergonomics")
    screen_time = st.number_input("How many hours per day do you spend sitting or using screens?", min_value=0, max_value=24, value=6, step=1)
    posture_awareness = st.slider("How would you rate your awareness of maintaining good posture?", 1, 10, 5)
    ergonomic_setup = st.radio("Do you have an ergonomic workspace setup (e.g., chair, desk height)?", ("Yes", "No"))
    sleeping_position = st.radio("What is your usual sleeping position?", ("Back", "Side", "Stomach", "Other"))

    st.markdown("---")

    # Collect physical assessment indicators
    st.header("5. Physical Assessment Indicators")
    shoulder_alignment = st.radio("Do you notice one shoulder higher than the other?", ("Yes", "No"))
    head_alignment = st.radio("Does your head appear to lean to one side when viewed from the front?", ("Yes", "No"))
    spinal_curvature = st.radio("Do you feel or notice any unevenness in your spine?", ("Yes", "No"))
    hip_level = st.radio("Are your hips level when you stand straight?", ("Yes", "No"))
    foot_alignment = st.radio("Do your feet point straight ahead or do they turn inward/outward?", ("Straight", "Inward", "Outward"))
    clothes_fit = st.radio("Do your clothes fit unevenly, indicating potential asymmetry in your body?", ("Yes", "No"))

    st.markdown("---")

    # Collect functional assessment indicators
    st.header("6. Functional Assessments")
    mobility = st.radio("Do you experience difficulty in moving or performing daily tasks due to your posture?", ("Yes", "No"))
    fatigue = st.radio("Do you often feel fatigued or tired, even without strenuous activity?", ("Yes", "No"))
    breathing = st.radio("Has your posture affected your breathing patterns?", ("Yes", "No"))
    balance_issues = st.radio("Do you experience balance problems?", ("Yes", "No"))

    st.markdown("---")

    # Image upload and analysis
    st.header("7. Image Upload and Analysis")
    st.write("You can upload a **side view** image of your body to analyze your posture.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Read the uploaded image
        image = Image.open(uploaded_file)
        # Convert the image to RGB
        image = image.convert('RGB')
        # Convert to numpy array
        image_np = np.array(image)

        # Display the uploaded image
        st.image(image_np, caption='Uploaded Image',  width=400)

        # Process the image and analyze posture
        with st.spinner('Analyzing image...'):
            # Initialize Mediapipe
            mp_drawing = mp.solutions.drawing_utils
            mp_pose = mp.solutions.pose

            # Convert the image to RGB for Mediapipe
            image_rgb = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

            # Perform pose estimation
            with mp_pose.Pose(static_image_mode=True, model_complexity=2, enable_segmentation=False) as pose:
                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    # Draw pose landmarks on the image
                    annotated_image = image_np.copy()
                    mp_drawing.draw_landmarks(
                        annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                    # Display the annotated image
                    st.image(annotated_image, caption='Analyzed Image',  width=400)

                    # Calculate angles
                    # For side view, relevant landmarks could be:
                    # - Shoulder (left/right)
                    # - Hip (left/right)
                    # - Knee (left/right)
                    # Since it's a side view, one side of the body may be more visible.

                    # Get landmark coordinates
                    landmarks = results.pose_landmarks.landmark

                    # Define function to get coordinates
                    def get_landmark_coords(landmark):
                        return [landmark.x, landmark.y]

                    # Choose left side landmarks for side view analysis
                    shoulder = get_landmark_coords(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER])
                    hip = get_landmark_coords(landmarks[mp_pose.PoseLandmark.LEFT_HIP])
                    knee = get_landmark_coords(landmarks[mp_pose.PoseLandmark.LEFT_KNEE])

                    # Calculate angle at hip
                    def calculate_angle(a, b, c):
                        a = np.array(a)  # First point
                        b = np.array(b)  # Middle point
                        c = np.array(c)  # End point

                        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                        angle = np.abs(radians*180.0/np.pi)

                        if angle > 180.0:
                            angle = 360 - angle

                        return angle

                    hip_angle = calculate_angle(shoulder, hip, knee)

                    st.write(f"**Hip Angle:** {hip_angle:.2f} degrees")

                    # Analyze hip angle
                    if hip_angle < 165:
                        st.write("🔴 **Your hip angle indicates a possible issue with posture.**")
                        st.session_state.score += 2  # Add to the score
                    else:
                        st.write("🟢 **Your hip angle is within a normal range.**")

                else:
                    st.write("⚠️ No pose landmarks detected. Please upload a clear side or back view image.")

    st.markdown("---")

    # Submit assessment button
    if st.button("Submit Assessment"):
        # Store responses in session state
        st.session_state.responses = {
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "occupation": occupation,
            "pain_present": pain_present,
            "pain_location": pain_location if pain_present == "Yes" else [],
            "pain_severity": pain_severity if pain_present == "Yes" else 0,
            "pain_duration": pain_duration if pain_present == "Yes" else "",
            "symptom_onset": symptom_onset if pain_present == "Yes" else "",
            "activity_related_pain": activity_related_pain if pain_present == "Yes" else "",
            "previous_diagnosis": previous_diagnosis,
            "family_history": family_history,
            "past_injuries": past_injuries,
            "physical_activity_level": physical_activity_level,
            "screen_time": screen_time,
            "posture_awareness": posture_awareness,
            "ergonomic_setup": ergonomic_setup,
            "sleeping_position": sleeping_position,
            "shoulder_alignment": shoulder_alignment,
            "head_alignment": head_alignment,
            "spinal_curvature": spinal_curvature,
            "hip_level": hip_level,
            "foot_alignment": foot_alignment,
            "clothes_fit": clothes_fit,
            "mobility": mobility,
            "fatigue": fatigue,
            "breathing": breathing,
            "balance_issues": balance_issues,
            "hip_angle": hip_angle if 'hip_angle' in locals() else None
        }

        # Calculate the assessment score
        score = st.session_state.score

        if pain_present == "Yes":
            score += 2
            if pain_severity >= 7:
                score += 2
            elif pain_severity >= 4:
                score += 1
            if pain_duration in ["6 months to a year", "Over a year"]:
                score += 2
            if symptom_onset == "Suddenly":
                score += 1
            if activity_related_pain == "Yes":
                score += 1

        if previous_diagnosis == "Yes":
            score += 3
        if family_history == "Yes":
            score += 2
        if past_injuries == "Yes":
            score += 1
        if physical_activity_level in ["Sedentary", "Lightly active"]:
            score += 1

        if screen_time > 6:
            score += 1
        if posture_awareness < 5:
            score += 1
        if ergonomic_setup == "No":
            score += 1
        if sleeping_position == "Stomach":
            score += 1

        if shoulder_alignment == "Yes":
            score += 2
        if head_alignment == "Yes":
            score += 2
        if spinal_curvature == "Yes":
            score += 3
        if hip_level == "No":
            score += 2
        if foot_alignment != "Straight":
            score += 1
        if clothes_fit == "Yes":
            score += 1

        if mobility == "Yes":
            score += 2
        if fatigue == "Yes":
            score += 1
        if breathing == "Yes":
            score += 1
        if balance_issues == "Yes":
            score += 1

        st.session_state.score = score

        # Determine risk level
        if score >= 15:
            risk_level = "High"
        elif 8 <= score < 15:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # Display assessment results
        st.success("📄 **Assessment Complete! Please see your report below.**")
        st.markdown("### 📊 **Your Posture Assessment Report**")
        st.write(f"**Risk Level:** {risk_level}")

        st.markdown("#### **Summary of Findings:**")
        if risk_level == "High":
            st.write("You are at **high risk** for posture-related issues or scoliosis. It is strongly recommended to consult a healthcare professional for a comprehensive evaluation.")
        elif risk_level == "Moderate":
            st.write("You are at **moderate risk** for posture-related issues. Consider taking proactive steps to improve your posture and reduce risk factors.")
        else:
            st.write("You are at **low risk** for posture-related issues. Continue maintaining good posture habits to sustain your spinal health.")

        st.markdown("#### **Recommendations:**")

        if risk_level == "Low":
            st.write("- **Maintain Good Posture:** Continue being mindful of your posture during daily activities.")
            st.write("- **Regular Exercise:** Incorporate stretching and strengthening exercises to support spinal health.")
            st.write("- **Ergonomic Practices:** Ensure your workspace remains ergonomic to prevent future issues.")

        elif risk_level == "Moderate":
            st.write("- **Posture Improvement Exercises:** Start specific exercises to enhance your posture.")
            st.write("- **Ergonomic Adjustments:** Reevaluate and adjust your workspace setup for better ergonomics.")
            st.write("- **Reduce Screen Time:** Take regular breaks to move and stretch during prolonged sitting periods.")

        elif risk_level == "High":
            st.write("- **Consult a Healthcare Professional:** Seek professional medical advice for a comprehensive evaluation.")
            st.write("- **Targeted Physical Therapy:** Begin physical therapy exercises as recommended by a professional.")
            st.write("- **Lifestyle Adjustments:** Implement significant ergonomic and lifestyle changes to support spinal health.")

        st.markdown("#### **Safe Exercises Suggestions:**")

        if risk_level in ["Moderate", "High"]:
            st.subheader("🧘 **Stretching Exercises:**")
            st.write("- **Neck Stretch:** Gently tilt your head towards each shoulder. Hold for 15 seconds on each side.")
            st.write("- **Chest Stretch:** Clasp your hands behind your back and gently lift your arms to stretch the chest muscles.")

            st.subheader("💪 **Strengthening Exercises:**")
            st.write("- **Planks:** Strengthen your core muscles by holding a plank position for 20-30 seconds. Gradually increase the duration.")
            st.write("- **Bridges:** Strengthen your lower back and glutes by lying on your back with knees bent and lifting your hips off the ground.")

            st.subheader("🧍 **Postural Awareness:**")
            st.write("- **Wall Angels:** Stand against a wall and move your arms up and down to improve shoulder alignment.")
            st.write("- **Seated Posture Correction:** Regularly check and adjust your sitting posture to maintain spinal alignment.")

            st.markdown("*Note: Perform all exercises slowly and stop if you experience any pain. Consult with a healthcare professional before starting any new exercise regimen.*")

        st.markdown("#### **Lifestyle Recommendations:**")
        if risk_level in ["Moderate", "High"]:
            st.write("- **Ergonomic Adjustments:** Set up your workspace to promote good posture, including chair and desk height adjustments.")
            st.write("- **Movement Breaks:** Take short breaks every 30 minutes to stand, stretch, and move around.")
            st.write("- **Mindfulness Practices:** Incorporate activities like yoga or tai chi to enhance body awareness and posture.")

        st.markdown("---")
        report = generate_report(risk_level, st.session_state.responses, score)
        st.download_button(
            label="📥 Download Your Report",
            data=report,
            file_name="Posture_Assessment_Report.txt",
            mime="text/plain",
        )

        st.button("🔄 Reset Assessment", on_click=reset_assessment)

    st.markdown("---")
    st.warning(
        "**Disclaimer:** This tool provides general information and is not a substitute for professional medical diagnosis or treatment. If you suspect you have scoliosis or any serious posture-related issues, please consult a healthcare professional."
    )

def generate_report(risk_level, responses, score):
    report = f"""
**Posture and Scoliosis Assessment Report**

**Risk Level:** {risk_level}

**Total Score:** {score}

---

**Summary of Findings:**
"""
    if risk_level == "High":
        report += "You are at high risk for posture-related issues or scoliosis. It is strongly recommended to consult a healthcare professional for a comprehensive evaluation.\n"
    elif risk_level == "Moderate":
        report += "You are at moderate risk for posture-related issues. Consider taking proactive steps to improve your posture and reduce risk factors.\n"
    else:
        report += "You are at low risk for posture-related issues. Continue maintaining good posture habits to sustain your spinal health.\n"

    report += "\n---\n\n**Recommendations:**\n"

    if risk_level == "Low":
        report += """
- **Maintain Good Posture:** Continue being mindful of your posture during daily activities.
- **Regular Exercise:** Incorporate stretching and strengthening exercises to support spinal health.
- **Ergonomic Practices:** Ensure your workspace remains ergonomic to prevent future issues.
"""
    elif risk_level == "Moderate":
        report += """
- **Posture Improvement Exercises:** Start specific exercises to enhance your posture.
- **Ergonomic Adjustments:** Reevaluate and adjust your workspace setup for better ergonomics.
- **Reduce Screen Time:** Take regular breaks to move and stretch during prolonged sitting periods.
"""
    elif risk_level == "High":
        report += """
- **Consult a Healthcare Professional:** Seek professional medical advice for a comprehensive evaluation.
- **Targeted Physical Therapy:** Begin physical therapy exercises as recommended by a professional.
- **Lifestyle Adjustments:** Implement significant ergonomic and lifestyle changes to support spinal health.
"""

    report += "\n---\n\n**Safe Exercises Suggestions:**\n"
    if risk_level in ["Moderate", "High"]:
        report += """
**Stretching Exercises:**
- **Neck Stretch:** Gently tilt your head towards each shoulder. Hold for 15 seconds on each side.
- **Chest Stretch:** Clasp your hands behind your back and gently lift your arms to stretch the chest muscles.

**Strengthening Exercises:**
- **Planks:** Strengthen your core muscles by holding a plank position for 20-30 seconds. Gradually increase the duration.
- **Bridges:** Strengthen your lower back and glutes by lying on your back with knees bent and lifting your hips off the ground.

**Postural Awareness:**
- **Wall Angels:** Stand against a wall and move your arms up and down to improve shoulder alignment.
- **Seated Posture Correction:** Regularly check and adjust your sitting posture to maintain spinal alignment.

*Note: Perform all exercises slowly and stop if you experience any pain. Consult with a healthcare professional before starting any new exercise regimen.*
"""

    report += "\n---\n\n**Lifestyle Recommendations:**\n"
    if risk_level in ["Moderate", "High"]:
        report += """
- **Ergonomic Adjustments:** Set up your workspace to promote good posture, including chair and desk height adjustments.
- **Movement Breaks:** Take short breaks every 30 minutes to stand, stretch, and move around.
- **Mindfulness Practices:** Incorporate activities like yoga or tai chi to enhance body awareness and posture.
"""

    report += "\n---\n\n**Disclaimer:** This report provides general information and is not a substitute for professional medical diagnosis or treatment. If you suspect you have scoliosis or any serious posture-related issues, please consult a healthcare professional."

    return report

if __name__ == "__main__":
    main()
