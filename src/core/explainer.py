"""
Code explanation engine using rule-based analysis.
"""

import re
import ast
from typing import Dict, List, Any, Optional
from loguru import logger


class CodeExplainer:
    """Rule-based code explanation engine."""
    
    def __init__(self, settings):
        self.settings = settings
        
        # Code patterns for analysis
        self.patterns = {
            "authentication": ["login", "auth", "jwt", "token", "password", "session"],
            "database": ["query", "select", "insert", "update", "delete", "sql", "db"],
            "api": ["endpoint", "route", "request", "response", "http", "rest"],
            "security": ["hash", "encrypt", "validate", "sanitize", "csrf", "xss"],
            "error_handling": ["try", "catch", "except", "error", "exception", "raise"],
            "async": ["async", "await", "promise", "future", "coroutine", "asyncio"],
            "testing": ["test", "assert", "mock", "fixture", "pytest", "unittest"],
            "logging": ["log", "debug", "info", "warn", "error", "logger"],
            "file_io": ["read", "write", "open", "close", "file", "path"],
            "network": ["socket", "http", "tcp", "udp", "request", "response"]
        }
        
        # Risk patterns
        self.risk_patterns = {
            "sql_injection": ["execute", "query", "sql", "raw", "format"],
            "xss": ["innerHTML", "document.write", "eval", "innerText"],
            "hardcoded_secrets": ["password", "secret", "key", "token", "api_key"],
            "memory_leaks": ["malloc", "new", "create", "allocate", "memory"],
            "race_conditions": ["thread", "async", "concurrent", "parallel", "lock"],
            "infinite_loops": ["while True", "for i in range", "recursive"],
            "unsafe_eval": ["eval", "exec", "compile", "__import__"],
            "path_traversal": ["../", "..\\", "path", "file", "directory"]
        }
        
        # Language detection patterns
        self.language_patterns = {
            "python": ["def ", "import ", "class ", "if __name__", "lambda", "yield"],
            "javascript": ["function ", "const ", "let ", "var ", "=>", "require("],
            "typescript": ["interface ", "type ", "enum ", "namespace ", "export "],
            "java": ["public class ", "private ", "protected ", "import java", "static"],
            "cpp": ["#include", "int main", "class ", "namespace ", "std::"],
            "go": ["package ", "func ", "import ", "type ", "var "],
            "rust": ["fn ", "let ", "use ", "mod ", "impl ", "struct "],
            "php": ["<?php", "function ", "class ", "namespace ", "use "],
            "ruby": ["def ", "class ", "module ", "require ", "end"],
            "swift": ["func ", "class ", "struct ", "import ", "var "],
            "kotlin": ["fun ", "class ", "import ", "val ", "var "]
        }
        
        logger.info("CodeExplainer initialized")
    
    async def explain(
        self,
        code: str,
        path: str = "",
        start_line: int = 1,
        end_line: int = 1
    ) -> Dict[str, Any]:
        """Explain code using rule-based analysis."""
        try:
            # Detect language
            language = self._detect_language(code)
            
            # Analyze patterns
            detected_patterns = self._analyze_patterns(code)
            
            # Identify risks
            risks = self._identify_risks(code)
            
            # Calculate complexity
            complexity = self._calculate_complexity(code)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(code, risks, complexity)
            
            # Generate summary
            summary = self._generate_summary(code, detected_patterns, language)
            
            explanation = {
                "summary": summary,
                "language": language,
                "patterns": detected_patterns,
                "risks": risks,
                "complexity": complexity,
                "suggestions": suggestions,
                "metadata": {
                    "path": path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "lines_of_code": len(code.split('\n'))
                }
            }
            
            logger.info(f"Code explanation completed: {language} code with {len(detected_patterns)} patterns")
            return explanation
            
        except Exception as e:
            logger.error(f"Code explanation error: {e}")
            raise
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code."""
        code_lower = code.lower()
        
        for language, patterns in self.language_patterns.items():
            if any(pattern.lower() in code_lower for pattern in patterns):
                return language
        
        return "unknown"
    
    def _analyze_patterns(self, code: str) -> List[str]:
        """Analyze code patterns."""
        detected_patterns = []
        code_lower = code.lower()
        
        for pattern_name, keywords in self.patterns.items():
            if any(keyword in code_lower for keyword in keywords):
                detected_patterns.append(pattern_name)
        
        return detected_patterns
    
    def _identify_risks(self, code: str) -> List[str]:
        """Identify potential risks in code."""
        risks = []
        code_lower = code.lower()
        
        for risk_type, patterns in self.risk_patterns.items():
            if any(pattern in code_lower for pattern in patterns):
                risks.append(risk_type)
        
        return risks
    
    def _calculate_complexity(self, code: str) -> Dict[str, Any]:
        """Calculate code complexity metrics."""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Basic metrics
        total_lines = len(lines)
        code_lines = len(non_empty_lines)
        
        # Cyclomatic complexity (simplified)
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'and', 'or']
        cyclomatic_complexity = 1  # Base complexity
        
        for line in lines:
            for keyword in complexity_keywords:
                if keyword in line.lower():
                    cyclomatic_complexity += 1
        
        # Nesting depth
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('if ', 'for ', 'while ', 'try:', 'with ', 'def ', 'class ')):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            elif stripped.startswith(('else:', 'elif ', 'except:', 'finally:')):
                # Same level
                pass
            elif stripped and not stripped.startswith('#'):
                # End of block
                current_nesting = max(0, current_nesting - 1)
        
        # Function count
        function_count = len(re.findall(r'def\s+\w+', code))
        
        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "cyclomatic_complexity": cyclomatic_complexity,
            "max_nesting_depth": max_nesting,
            "function_count": function_count,
            "complexity_score": self._calculate_complexity_score(cyclomatic_complexity, max_nesting, function_count)
        }
    
    def _calculate_complexity_score(self, cyclomatic: int, nesting: int, functions: int) -> str:
        """Calculate overall complexity score."""
        score = cyclomatic + nesting + functions
        
        if score <= 5:
            return "Low"
        elif score <= 15:
            return "Medium"
        elif score <= 30:
            return "High"
        else:
            return "Very High"
    
    def _generate_suggestions(self, code: str, risks: List[str], complexity: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Risk-based suggestions
        if "sql_injection" in risks:
            suggestions.append("Use parameterized queries to prevent SQL injection")
        
        if "xss" in risks:
            suggestions.append("Sanitize user input to prevent XSS attacks")
        
        if "hardcoded_secrets" in risks:
            suggestions.append("Move secrets to environment variables or secure config")
        
        if "memory_leaks" in risks:
            suggestions.append("Ensure proper resource cleanup and memory management")
        
        if "race_conditions" in risks:
            suggestions.append("Add proper synchronization mechanisms")
        
        if "infinite_loops" in risks:
            suggestions.append("Add break conditions to prevent infinite loops")
        
        if "unsafe_eval" in risks:
            suggestions.append("Avoid using eval() for security reasons")
        
        if "path_traversal" in risks:
            suggestions.append("Validate and sanitize file paths")
        
        # Complexity-based suggestions
        if complexity["cyclomatic_complexity"] > 10:
            suggestions.append("Consider breaking down complex functions into smaller ones")
        
        if complexity["max_nesting_depth"] > 4:
            suggestions.append("Reduce nesting depth for better readability")
        
        if complexity["function_count"] == 0 and complexity["code_lines"] > 20:
            suggestions.append("Consider organizing code into functions")
        
        # General suggestions
        if "TODO" in code:
            suggestions.append("Complete TODO items")
        
        if "console.log" in code:
            suggestions.append("Use proper logging instead of console.log")
        
        if "var " in code:
            suggestions.append("Use let/const instead of var")
        
        if "print(" in code:
            suggestions.append("Use proper logging instead of print statements")
        
        return suggestions
    
    def _generate_summary(self, code: str, patterns: List[str], language: str) -> str:
        """Generate code summary."""
        lines = code.split('\n')
        line_count = len([line for line in lines if line.strip()])
        
        # Base summary
        summary_parts = [f"This is {line_count} lines of {language} code"]
        
        # Add pattern information
        if patterns:
            if len(patterns) == 1:
                summary_parts.append(f"that appears to handle {patterns[0]}")
            else:
                summary_parts.append(f"that involves {', '.join(patterns[:-1])} and {patterns[-1]}")
        
        # Add specific observations
        if "def " in code:
            function_count = len(re.findall(r'def\s+\w+', code))
            summary_parts.append(f"with {function_count} function(s)")
        
        if "class " in code:
            class_count = len(re.findall(r'class\s+\w+', code))
            summary_parts.append(f"and {class_count} class(es)")
        
        if "import " in code:
            summary_parts.append("that imports external dependencies")
        
        return ". ".join(summary_parts) + "."
