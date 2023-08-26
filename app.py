import streamlit as st
import os

from summa import validate_openai_key, check_youtube_url_validity, fetch_video_duration, compute_api_cost, fetch_video_metadata, generate_qa, generate_video_summary

# Configure the Streamlit page
st.set_page_config(page_title="GPTube", page_icon='📹')

# Main App Function
def gptube_app():

    # Sidebar content
    with st.sidebar:
        st.markdown("### 📹 GPTube: Video Insights")
        st.video("https://www.youtube.com/watch?v=uuuv3ooY1WQ")
        st.markdown("""
                    <div style="text-align: justify;">GPTube helps you extract valuable insights from YouTube videos. 
                    Ask a question and get an answer in less than two minutes at a cost of $0.006 per minute. 
                    Alternatively, get a summary for $0.009 per minute.</div>
                    """, unsafe_allow_html=True)
        st.markdown("###")
        st.markdown("🔗 [GitHub Source](https://github.com/Hamagistral/GPTube)")
        st.markdown("👤 Created by [Hamza El Belghiti](https://www.linkedin.com/in/hamza-elbelghiti/)")

    # Main content
    st.header("📹 GPTube: Quick Video Summaries and Answers")
    st.markdown('###') 
    user_choice = st.radio("Select an action:", ('Generate Summary', 'Answer a Question'), horizontal=True)
    st.markdown('###') 

    # OpenAI API Key Input
    st.subheader('🔑 Step 1: Input OpenAI API Key')
    api_key = st.text_input("[Get API Key from OpenAI](https://platform.openai.com/account/api-keys):", type="password")

    # YouTube URL Input
    st.subheader('🎬 Step 2: Input YouTube Video URL')
    yt_url = st.text_input("URL:", placeholder="https://www.youtube.com/watch?v=************") if api_key else st.text_input("URL:", placeholder="Enter OpenAI API key first", disabled=True)

    if check_youtube_url_validity(yt_url):
        video_length = fetch_video_duration(yt_url)
        cost_option = 'summary' if user_choice == 'Generate Summary' else 'answer'
        estimated_cost = compute_api_cost(video_length, cost_option)

        if 4 <= video_length <= 20:
            st.info(f"🕒 Video duration: {video_length} minutes. Estimated cost: ${estimated_cost}")
            thumbnail, title = fetch_video_metadata(yt_url)
            st.subheader(f"🎥 {title}")
            st.image(thumbnail, use_column_width=True)
        else:
            st.warning("Video duration should be between 4 and 20 minutes.")
    else:
        st.error("Invalid YouTube URL.")

    # Generate Summary or Answer
    if user_choice == "Generate Summary":
        if api_key and yt_url:
            if st.button("Generate Summary"):
                if validate_openai_key(api_key):
                    with st.spinner("Summarizing..."):
                        summary = generate_video_summary(api_key, yt_url)
                    st.subheader("📝 Summary:")
                    st.success(summary)
                else:
                    st.error("Invalid OpenAI API key.")
        else:
            st.warning("Enter both OpenAI API key and YouTube URL.")

    elif user_choice == "Answer a Question":
        if api_key and yt_url:
            st.subheader('❓ Step 3: What is your question?')
            user_question = st.text_input("Question:", placeholder="What does X mean? How to do X?")
            if st.button("Generate Answer"):
                if validate_openai_key(api_key):
                    with st.spinner("Fetching answer..."):
                        answer = generate_qa(api_key, yt_url, user_question)
                    st.subheader(f"🔍 {user_question}")
                    st.success(answer)
                else:
                    st.error("Invalid OpenAI API key.")
        else:
            st.warning("Enter both OpenAI API key and YouTube URL.")

gptube_app()

# Hide Streamlit's default menu and footer
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
