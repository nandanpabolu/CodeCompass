# 🧭 CodeCompass

**A powerful Model Context Protocol (MCP) server that transforms your local codebase into an intelligent, searchable knowledge base. Built for developers who want to understand, explore, and analyze their code with natural language queries.**

## ✨ Key Features

- 🔍 **Intelligent Code Search** - Text, regex, and semantic search across your entire codebase
- 📖 **Smart Code Explanation** - Get instant explanations of functions, classes, and code blocks
- 📝 **TODO Detection** - Find and track all TODO, FIXME, and technical debt comments
- 🔒 **Safe & Secure** - Runs entirely locally with no cloud dependencies
- 🚀 **Claude Desktop Ready** - Seamless integration with Claude Desktop and other MCP clients
- 🌐 **Web Dashboard** - Beautiful Streamlit interface for team collaboration
- 💰 **Completely Free** - Zero ongoing costs, no API fees, no subscriptions

## 🎯 Perfect For

- **Code Reviews** - Quickly understand unfamiliar codebases
- **Onboarding** - Help new team members navigate complex projects
- **Documentation** - Generate explanations and insights automatically
- **Technical Debt** - Track and prioritize TODO items across projects
- **Code Analysis** - Identify patterns, risks, and improvement opportunities

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/nandanpabolu/CodeCompass.git
cd CodeCompass

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run MCP Server
python src/mcp_server.py

# Or run the web dashboard
streamlit run src/streamlit_app.py
```

### Claude Desktop Integration

1. Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "codecompass": {
      "command": "python",
      "args": ["/path/to/CodeCompass/src/mcp_server.py"],
      "env": {
        "REPO_ROOT": "/path/to/your/codebase"
      }
    }
  }
}
```

## 🔧 Tech Stack

- **Python 3.12+** with async/await
- **MCP Protocol** for AI client integration
- **Streamlit** for web interface
- **Local AI** support via Ollama (optional)
- **Semantic Search** with sentence-transformers
- **Zero Dependencies** on external services

## 📁 Project Structure

```
CodeCompass/
├── src/                    # Source code
│   ├── mcp_server.py      # MCP protocol server
│   ├── streamlit_app.py   # Streamlit dashboard
│   ├── core/              # Core analysis engine
│   └── tools/             # MCP tool implementations
├── config/                # Configuration files
├── tests/                 # Test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── scripts/               # Utility scripts
```

## 🛠️ Available Tools

### Core Tools
- `search_code` - Search code with text or regex
- `read_file` - Read file contents with pagination
- `list_todos` - Find TODO/FIXME comments
- `explain_range` - Explain code blocks
- `get_file_info` - Get file metadata

### Advanced Tools
- `semantic_search` - Semantic code search
- `analyze_complexity` - Code complexity analysis
- `find_references` - Find function/variable usage
- `code_metrics` - Calculate code metrics

## 🌐 Web Dashboard

Access the Streamlit dashboard at `http://localhost:8501` for:
- Interactive code search
- File explorer
- Code analysis results
- Configuration management
- Team collaboration

## 🔒 Security Features

- Path traversal protection
- File size limits
- Whitelisted repository roots
- Ignore pattern support
- Safe file access controls

## 📊 Performance

- File reading: < 100ms for files < 1MB
- Text search: < 500ms for 10,000 files
- Semantic search: < 1s for 1,000 code chunks
- Memory usage: < 500MB for typical codebase

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [Streamlit](https://streamlit.io/)
- Inspired by the need for better code understanding tools

---

**Transform your codebase into an intelligent assistant. Start exploring your code like never before! 🚀**

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-1.0+-orange.svg)](https://modelcontextprotocol.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
