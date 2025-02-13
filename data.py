# # data.py
# import streamlit as st

# def collect_personal_info():
#     return {
#         "name": st.text_input("Full Name", key="name"),
#         "email": st.text_input("Email", key="email"),
#         "phone": st.text_input("Phone Number", key="phone"),
#         "linkedin": st.text_input("LinkedIn URL", key="linkedin"),
#         "location": st.text_input("Location", key="location")
#     }

# def collect_education():
#     st.subheader("Education")
#     num_education = st.number_input("Number of Education Entries", 1, 5, 1, key="num_edu")
#     education = []
#     for i in range(num_education):
#         st.markdown(f"#### Education {i+1}")
#         edu = {
#             "degree": st.text_input("Degree/Certificate", key=f"edu_degree_{i}"),
#             "school": st.text_input("Institution", key=f"edu_school_{i}"),
#             "location": st.text_input("Location", key=f"edu_location_{i}"),
#             "graduation_date": st.text_input("Graduation Date", key=f"edu_grad_date_{i}"),
#             "gpa": st.text_input("GPA (optional)", key=f"edu_gpa_{i}")
#         }
#         education.append(edu)
#     return education

# def collect_experience():
#     st.subheader("Professional Experience")
#     num_experiences = st.number_input("Number of Experience Entries", 1, 10, 1, key="num_exp")
#     experiences = []
#     for i in range(num_experiences):
#         st.markdown(f"#### Experience {i+1}")
#         exp = {
#             "title": st.text_input("Job Title", key=f"exp_title_{i}"),
#             "company": st.text_input("Company", key=f"exp_company_{i}"),
#             "location": st.text_input("Location", key=f"exp_location_{i}"),
#             "start_date": st.text_input("Start Date", key=f"exp_start_date_{i}"),
#             "end_date": st.text_input("End Date", key=f"exp_end_date_{i}"),
#             "responsibilities": st.text_area(
#                 "Key Responsibilities and Achievements (one per line)",
#                 help="Focus on achievements and quantifiable results",
#                 key=f"exp_resp_{i}"
#             )
#         }
#         experiences.append(exp)
#     return experiences

# def collect_skills(skills_text):
#     return skills_text.split('\n') if skills_text else []

# def collect_resume_data():
#     st.subheader("Personal Information")
#     personal_info = collect_personal_info()
    
#     st.subheader("Professional Summary")
#     summary = st.text_area("Write a brief professional summary", 
#                           height=100, 
#                           key="summary",
#                           help="A 2-3 sentence overview of your career and goals")
    
#     education = collect_education()
#     experiences = collect_experience()
    
#     st.subheader("Skills")
#     skills_text = st.text_area(
#         "Technical Skills (one per line)",
#         help="List your technical skills, tools, and technologies",
#         key="skills"
#     )
    
#     return {
#         "personal_info": personal_info,
#         "summary": summary,
#         "education": education,
#         "experience": experiences,
#         "skills": collect_skills(skills_text)
#     }