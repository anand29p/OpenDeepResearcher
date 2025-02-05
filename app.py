import streamlit as st
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from modules.research_core import ResearchCore
import aiohttp

nest_asyncio.apply()
load_dotenv()

st.set_page_config(page_title="OpenDeepResearcher", layout="wide")

async def main_async(query):
    async with aiohttp.ClientSession() as session:
        try:
            core = ResearchCore()
            return await core.research_loop(session, query)
        except aiohttp.ClientError as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Research failed: {str(e)}"

def main():
    st.title("🔍 OpenDeepResearcher")
    
    with st.form("research_form"):
        query = st.text_area("Research Query:", 
                           placeholder="Enter your research topic...",
                           height=100)
        submitted = st.form_submit_button("Start Research")
        
    if submitted and query:
        with st.spinner("🧠 Conducting deep research..."):
            result = asyncio.run(main_async(query))
            st.markdown(result)
            
if __name__ == "__main__":
    main()
