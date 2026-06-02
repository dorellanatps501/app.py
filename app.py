import streamlit as st
import pandas as pd
import random

# Page configuration
st.set_page_config(
    page_title="Library Companion Book Matcher", 
    page_icon="📚", 
    layout="centered"
)

# Title and introduction
st.title("🎯 Find Your Next Favorite Book!")
st.write("Answer a few quick questions to search our library shelves for your next read.")
st.markdown("---")

@st.cache_data
def load_and_clean_data():
    # Load spreadsheet
    file_path = "LibraryTitleCopyReportJob2086481.xlsx"
    df = pd.read_excel(file_path, sheet_name=0)
    
    # Clean up titles (removes subtitle noise after the colon)
    df['Clean_Title'] = df['Title'].astype(str).str.split(' :').str[0].str.strip()
    df['Author'] = df['Author'].fillna('Unknown Author')
    df['Call_Prefix'] = df['Call Number'].astype(str).str.split().str[0]
    df['Status'] = df['Status'].fillna('Available')
    
    # Custom rule engine to map Call Numbers to student interests
    def assign_category(row):
        prefix = str(row['Call_Prefix'])
        title_lower = str(row['Clean_Title']).lower()
        
        if prefix == 'F':
            if any(w in title_lower for w in ['graphic', 'comic', 'ilustrada', 'novela']):
                return '🎨 Graphic Novels & Comics'
            elif any(w in title_lower for w in ['mystery', 'secret', 'lost', 'escape', 'abduction', 'ghost']):
                return '🚨 Mystery, Ghosts & Thrilling Adventures'
            else:
                return '✨ Fiction (Stories, Fantasy & Friendship)'
        elif prefix in ['B', '920']:
            return '👤 Real People, Biographies & Memoirs'
        elif prefix in ['398.2', '811']:
            return '🐉 Myths, Legends & Poetry'
        elif prefix == 'EQ' or prefix == 'E':
            return '📖 Quick Reads & Illustrated Stories'
        else:
            return '🧠 True Facts, Science, Sports & History'
            
    df['Story_Type'] = df.apply(assign_category, axis=1)
    return df

# Initialize data loading safely
try:
    library_data = load_and_clean_data()
except Exception as e:
    st.error("⚠️ Error finding your data file. Please make sure 'LibraryTitleCopyReportJob2086481.xlsx' is inside the exact same folder as this app.py file!")
    st.stop()

# ----------------- STUDENT INTERFACE -----------------

with st.form("quiz_form"):
    st.subheader("Step 1: What are you in the mood for?")
    pathway = st.selectbox(
        "Pick a reading territory:",
        options=sorted(library_data['Story_Type'].unique())
    )
    
    st.subheader("Step 2: Narrow it down")
    # Dynamic Search Filter
    keyword = st.text_input("✨ (Optional) Type a keyword you like (e.g., 'space', 'dog', 'magic', 'war'):").strip().lower()
    
    st.subheader("Step 3: Availability Check")
    only_available = st.checkbox("Only show books currently marked 'Available' right now", value=True)
    
    submitted = st.form_submit_button("Match Me With A Book! 🚀")

# ----------------- MATCHING LOGIC -----------------

if submitted:
    # Filter by main category choice
    filtered_df = library_data[library_data['Story_Type'] == pathway]
    
    # Filter by status if checked
    if only_available:
        filtered_df = filtered_df[filtered_df['Status'].str.lower() == 'available']
        
    # Filter by optional keyword
    if keyword:
        filtered_df = filtered_df[
            filtered_df['Clean_Title'].str.lower().str.contains(keyword) | 
            filtered_df['Author'].str.lower().str.contains(keyword)
        ]
        
    if not filtered_df.empty:
        st.balloons()
        st.success(f"📚 We scanned all 7,950+ books and found {len(filtered_df)} tailored matches for you! Here are some top picks:")
        
        # Pull a random sample of up to 3 books to give fresh choices every time
        sample_size = min(3, len(filtered_df))
        recommendations = filtered_df.sample(n=sample_size)
        
        for idx, row in recommendations.iterrows():
            with st.container():
                st.markdown(f"### 📖 **{row['Clean_Title']}**")
                st.markdown(f"*✍️ Written by: {row['Author']}*")
                
                # Highlight call number so they can find it physically
                st.markdown(
                    f"🧭 **Where to find it on our shelves:** "
                    f"Look for Call Number: `{row['Call Number']}`"
                )
                
                # Style status badge
                status_color = "green" if row['Status'].lower() == 'available' else "orange"
                st.markdown(f"📊 **Current Status:** :{status_color}[{row['Status']}]")
                st.markdown("---")
    else:
        st.warning("🕵️‍♂️ No books match that exact keyword combination right now. Try leaving the keyword blank or typing a simpler word like 'cat', 'hero', or 'world'!")