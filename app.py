import streamlit as st
import os

from summa import validate_openai_key, check_youtube_url_validity, fetch_video_duration, compute_api_cost, fetch_video_metadata, generate_qa, generate_video_summary

# Set up Streamlit page
st.set_page_config(page_title="VideoAnalyzer", page_icon='🎬')

# Main Function
def main_app():

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎬 VideoAnalyzer: Insights at a Glance")
        st.video("https://www.youtube.com/watch?v=gT1EExZkzMM")
        st.markdown("""
                    <div style="text-align: justify;">VideoAnalyzer allows you to quickly get the information you need from YouTube videos. 
                    Pose a question and receive an answer in under two minutes for just $0.006/min. 
                    Or, get a summarized version for $0.009/min.</div>
                    """, unsafe_allow_html=True)
        st.markdown("###")

    # Main Content
    st.header("🎬 VideoAnalyzer: Quick Summaries and Q&A")
    st.markdown('###') 
    action = st.radio("Select an Option:", ('Generate Summary', 'Answer a Question'), horizontal=True)
    st.markdown('###') 

    # API Key Input
    st.subheader('🔑 Step 1: Enter OpenAI API Key')
    api_key = st.text_input("[Get API Key from OpenAI](https://platform.openai.com/account/api-keys):", type="password")

    # YouTube URL Input
    st.subheader('🎥 Step 2: Enter YouTube Video URL')
    yt_url = st.text_input("URL:", placeholder="https://www.youtube.com/watch?v=************") if api_key else st.text_input("URL:", placeholder="Enter OpenAI API key first", disabled=True)

    if check_youtube_url_validity(yt_url):
        video_length = fetch_video_duration(yt_url)
        cost_type = 'summary' if action == 'Generate Summary' else 'answer'
        est_cost = compute_api_cost(video_length, cost_type)

        if 4 <= video_length <= 20:
            st.info(f"🕒 Video Length: {video_length} mins. Approx. Cost: ${est_cost}")
            thumbnail, title = fetch_video_metadata(yt_url)
            st.subheader(f"🎥 {title}")
            st.image(thumbnail, use_column_width=True)
        else:
            st.warning("Video should be between 4 and 20 minutes.")
    else:
        st.error("Invalid YouTube URL.")

    # Generate Summary or Answer
    if action == "Generate Summary":
        if api_key and yt_url:
            if st.button("Generate Summary"):
                if validate_openai_key(api_key):
                    with st.spinner("Creating summary..."):
                        summary = generate_video_summary(api_key, yt_url)
                    st.subheader("📝 Summary:")
                    st.success(summary)
                else:
                    st.error("Invalid OpenAI API key.")
        else:
            st.warning("Enter both OpenAI API key and YouTube URL.")

    elif action == "Answer a Question":
        if api_key and yt_url:
            st.subheader('❓ Step 3: What’s your question?')
            query = st.text_input("Your Question:", placeholder="What does X mean? How to do X?")
            if st.button("Generate Answer"):
                if validate_openai_key(api_key):
                    with st.spinner("Fetching answer..."):
                        answer = generate_qa(api_key, yt_url, query)
                    st.subheader(f"🔍 {query}")
                    st.success(answer)
                else:
                    st.error("Invalid OpenAI API key.")
        else:
            st.warning("Enter both OpenAI API key and YouTube URL.")

main_app()

# Hide default Streamlit elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
