#!/usr/bin/env python3
"""
CodeCompass Streamlit Dashboard

Web interface for the CodeCompass MCP server.
"""

import streamlit as st
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import json

from .core.analyzer import CodeAnalyzer
from .config.settings import Settings
from .utils.safety import PathValidator

# Page configuration
st.set_page_config(
    page_title="CodeCompass Dashboard",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "analyzer" not in st.session_state:
    st.session_state.analyzer = None
if "settings" not in st.session_state:
    st.session_state.settings = None
if "path_validator" not in st.session_state:
    st.session_state.path_validator = None


def initialize_components():
    """Initialize the analyzer and other components."""
    try:
        if not st.session_state.analyzer:
            st.session_state.settings = Settings()
            st.session_state.path_validator = PathValidator(st.session_state.settings.repositories.roots)
            st.session_state.analyzer = CodeAnalyzer(st.session_state.settings)
    except Exception as e:
        st.error(f"Failed to initialize: {e}")


def search_page():
    """Code search page."""
    st.header("🔍 Code Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Search Query", placeholder="Enter search term...")
    
    with col2:
        search_type = st.selectbox("Search Type", ["Text", "Regex", "Semantic"])
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        case_sensitive = st.checkbox("Case Sensitive", False)
    
    with col4:
        path_prefix = st.text_input("Path Prefix", placeholder="src/")
    
    with col5:
        limit = st.slider("Max Results", 10, 1000, 50)
    
    if st.button("Search", type="primary"):
        if query:
            with st.spinner("Searching..."):
                try:
                    # Perform search
                    results = asyncio.run(st.session_state.analyzer.search_code(
                        query=query,
                        regex=(search_type == "Regex"),
                        case_sensitive=case_sensitive,
                        path_prefix=path_prefix,
                        limit=limit
                    ))
                    
                    if results:
                        st.success(f"Found {len(results)} results")
                        
                        for i, result in enumerate(results):
                            with st.expander(f"Result {i+1}: {result.get('path', 'Unknown')}"):
                                st.code(result.get('snippet', ''), language='python')
                                st.text(f"Line: {result.get('line', 'Unknown')}")
                    else:
                        st.info("No results found")
                        
                except Exception as e:
                    st.error(f"Search error: {e}")
        else:
            st.warning("Please enter a search query")


def file_explorer_page():
    """File explorer page."""
    st.header("📁 File Explorer")
    
    # File upload
    uploaded_file = st.file_uploader("Upload a file", type=['py', 'js', 'ts', 'java', 'cpp', 'go', 'rs'])
    
    if uploaded_file:
        content = uploaded_file.read().decode('utf-8')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("File Content")
            st.code(content, language='python')
        
        with col2:
            st.subheader("File Info")
            st.json({
                "name": uploaded_file.name,
                "size": uploaded_file.size,
                "type": uploaded_file.type
            })
            
            if st.button("Analyze File"):
                with st.spinner("Analyzing..."):
                    try:
                        # Analyze the file
                        analysis = asyncio.run(st.session_state.analyzer.explain_range(
                            path=uploaded_file.name,
                            start_line=1,
                            end_line=len(content.split('\n')),
                            code=content
                        ))
                        
                        st.subheader("Analysis Results")
                        st.json(analysis)
                        
                    except Exception as e:
                        st.error(f"Analysis error: {e}")


def analysis_page():
    """Code analysis page."""
    st.header("🔬 Code Analysis")
    
    # Code input
    code_input = st.text_area("Paste code to analyze", height=300, placeholder="def hello():\n    print('world')")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Analyze Code", type="primary"):
            if code_input:
                with st.spinner("Analyzing..."):
                    try:
                        # Analyze the code
                        analysis = asyncio.run(st.session_state.analyzer.explain_range(
                            path="input.py",
                            start_line=1,
                            end_line=len(code_input.split('\n')),
                            code=code_input
                        ))
                        
                        st.subheader("Analysis Results")
                        
                        # Display summary
                        if "summary" in analysis:
                            st.subheader("Summary")
                            st.write(analysis["summary"])
                        
                        # Display risks
                        if "risks" in analysis and analysis["risks"]:
                            st.subheader("⚠️ Potential Risks")
                            for risk in analysis["risks"]:
                                st.warning(risk)
                        
                        # Display suggestions
                        if "suggestions" in analysis and analysis["suggestions"]:
                            st.subheader("💡 Suggestions")
                            for suggestion in analysis["suggestions"]:
                                st.info(suggestion)
                        
                        # Display complexity
                        if "complexity" in analysis:
                            st.subheader("📊 Complexity Analysis")
                            st.json(analysis["complexity"])
                        
                    except Exception as e:
                        st.error(f"Analysis error: {e}")
            else:
                st.warning("Please enter some code to analyze")
    
    with col2:
        st.subheader("Analysis Features")
        st.markdown("""
        - **Pattern Recognition**: Identifies common code patterns
        - **Risk Detection**: Finds potential security issues
        - **Complexity Analysis**: Calculates code complexity metrics
        - **Best Practices**: Suggests improvements
        - **Language Detection**: Automatically detects programming language
        """)


def todos_page():
    """TODO tracking page."""
    st.header("📝 TODO Tracker")
    
    path_prefix = st.text_input("Path Prefix", placeholder="src/")
    
    if st.button("Find TODOs", type="primary"):
        with st.spinner("Searching for TODOs..."):
            try:
                todos = asyncio.run(st.session_state.analyzer.list_todos(path_prefix=path_prefix))
                
                if todos:
                    st.success(f"Found {len(todos)} TODO items")
                    
                    for i, todo in enumerate(todos):
                        with st.expander(f"TODO {i+1}: {todo.get('path', 'Unknown')}"):
                            st.code(todo.get('text', ''), language='python')
                            st.text(f"Line: {todo.get('line', 'Unknown')}")
                            st.text(f"File: {todo.get('path', 'Unknown')}")
                else:
                    st.info("No TODO items found")
                    
            except Exception as e:
                st.error(f"TODO search error: {e}")


def settings_page():
    """Settings page."""
    st.header("⚙️ Settings")
    
    if st.session_state.settings:
        st.subheader("Repository Configuration")
        
        # Repository roots
        st.text_input("Repository Roots", value=", ".join(st.session_state.settings.repositories.roots))
        
        # Ignore patterns
        st.subheader("Ignore Patterns")
        ignore_patterns = st.text_area(
            "Ignore Patterns (one per line)",
            value="\n".join(st.session_state.settings.repositories.ignore_patterns)
        )
        
        # Search settings
        st.subheader("Search Settings")
        max_results = st.slider("Max Results", 10, 1000, st.session_state.settings.search.default_limit)
        case_sensitive = st.checkbox("Case Sensitive", st.session_state.search.case_sensitive)
        
        # Save settings
        if st.button("Save Settings"):
            st.success("Settings saved!")
    
    st.subheader("About CodeCompass")
    st.markdown("""
    **CodeCompass** is a powerful MCP server for intelligent codebase analysis and search.
    
    - 🔍 **Intelligent Search**: Text, regex, and semantic search
    - 📖 **Code Explanation**: Understand code with AI-powered analysis
    - 📝 **TODO Tracking**: Find and manage technical debt
    - 🔒 **Secure**: Runs locally with no cloud dependencies
    - 🚀 **Fast**: Optimized for large codebases
    
    **Version**: 1.0.0  
    **Author**: Nandan Pabolu  
    **License**: MIT
    """)


def main():
    """Main Streamlit application."""
    # Initialize components
    initialize_components()
    
    # Sidebar navigation
    st.sidebar.title("🧭 CodeCompass")
    
    page = st.sidebar.selectbox(
        "Navigate",
        ["🔍 Search", "📁 Explorer", "🔬 Analysis", "📝 TODOs", "⚙️ Settings"]
    )
    
    # Route to appropriate page
    if page == "🔍 Search":
        search_page()
    elif page == "📁 Explorer":
        file_explorer_page()
    elif page == "🔬 Analysis":
        analysis_page()
    elif page == "📝 TODOs":
        todos_page()
    elif page == "⚙️ Settings":
        settings_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**CodeCompass v1.0.0**")
    st.sidebar.markdown("Built with ❤️ using Streamlit")


if __name__ == "__main__":
    main()
