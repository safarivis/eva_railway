#!/usr/bin/env python3
"""
Voice Coding Examples - Natural Language Commands for Claude Code

This module demonstrates practical voice commands and patterns for coding
with Claude Code using natural language.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class VoiceCommand(Enum):
    """Categories of voice commands for coding"""
    # File Operations
    CREATE_FILE = "create_file"
    OPEN_FILE = "open_file"
    SAVE_FILE = "save_file"
    DELETE_FILE = "delete_file"
    
    # Code Generation
    CREATE_FUNCTION = "create_function"
    CREATE_CLASS = "create_class"
    ADD_METHOD = "add_method"
    IMPLEMENT_INTERFACE = "implement_interface"
    
    # Code Modification
    REFACTOR_CODE = "refactor_code"
    RENAME_VARIABLE = "rename_variable"
    EXTRACT_METHOD = "extract_method"
    OPTIMIZE_CODE = "optimize_code"
    
    # Testing
    WRITE_TEST = "write_test"
    RUN_TESTS = "run_tests"
    DEBUG_CODE = "debug_code"
    
    # Documentation
    ADD_DOCSTRING = "add_docstring"
    GENERATE_README = "generate_readme"
    EXPLAIN_CODE = "explain_code"
    
    # Navigation
    GO_TO_DEFINITION = "go_to_definition"
    FIND_REFERENCES = "find_references"
    SEARCH_PROJECT = "search_project"


@dataclass
class CommandExample:
    """Example voice command with expected action"""
    voice_input: str
    command_type: VoiceCommand
    parameters: Dict[str, Any]
    expected_action: str


# Comprehensive examples of voice commands
VOICE_COMMAND_EXAMPLES = [
    # File Operations
    CommandExample(
        voice_input="Create a new Python file called user authentication",
        command_type=VoiceCommand.CREATE_FILE,
        parameters={"filename": "user_authentication.py", "template": "python"},
        expected_action="Create user_authentication.py with Python boilerplate"
    ),
    
    CommandExample(
        voice_input="Open the main configuration file",
        command_type=VoiceCommand.OPEN_FILE,
        parameters={"search": "config", "priority": ["main", "config", "settings"]},
        expected_action="Search for and open the primary configuration file"
    ),
    
    # Code Generation
    CommandExample(
        voice_input="Create a function to validate email addresses",
        command_type=VoiceCommand.CREATE_FUNCTION,
        parameters={
            "name": "validate_email",
            "purpose": "validate email addresses",
            "returns": "boolean",
            "parameters": ["email: str"]
        },
        expected_action="Generate email validation function with regex"
    ),
    
    CommandExample(
        voice_input="Create a class for managing user sessions with login and logout methods",
        command_type=VoiceCommand.CREATE_CLASS,
        parameters={
            "name": "SessionManager",
            "methods": ["login", "logout", "is_authenticated"],
            "attributes": ["user_id", "session_token", "expiry"]
        },
        expected_action="Generate SessionManager class with specified methods"
    ),
    
    CommandExample(
        voice_input="Add a method to calculate total price with tax",
        command_type=VoiceCommand.ADD_METHOD,
        parameters={
            "class_context": "current",
            "method_name": "calculate_total_with_tax",
            "parameters": ["price: float", "tax_rate: float"],
            "returns": "float"
        },
        expected_action="Add calculate_total_with_tax method to current class"
    ),
    
    # Code Modification
    CommandExample(
        voice_input="Refactor this function to use list comprehension",
        command_type=VoiceCommand.REFACTOR_CODE,
        parameters={
            "target": "current_function",
            "refactor_type": "list_comprehension",
            "maintain_functionality": True
        },
        expected_action="Convert loops to list comprehension while preserving behavior"
    ),
    
    CommandExample(
        voice_input="Rename all instances of user_data to user_profile",
        command_type=VoiceCommand.RENAME_VARIABLE,
        parameters={
            "old_name": "user_data",
            "new_name": "user_profile",
            "scope": "project-wide"
        },
        expected_action="Rename variable across entire project"
    ),
    
    CommandExample(
        voice_input="Extract the validation logic into a separate method",
        command_type=VoiceCommand.EXTRACT_METHOD,
        parameters={
            "selection": "current_selection",
            "method_name": "validate_input",
            "visibility": "private"
        },
        expected_action="Extract selected code into new private method"
    ),
    
    # Testing
    CommandExample(
        voice_input="Write unit tests for the authentication module",
        command_type=VoiceCommand.WRITE_TEST,
        parameters={
            "target": "authentication module",
            "test_framework": "pytest",
            "coverage": ["happy_path", "edge_cases", "error_handling"]
        },
        expected_action="Generate comprehensive pytest tests for authentication"
    ),
    
    CommandExample(
        voice_input="Debug why this function returns null",
        command_type=VoiceCommand.DEBUG_CODE,
        parameters={
            "issue": "returns null",
            "function": "current",
            "add_logging": True
        },
        expected_action="Add debug logging and analyze potential null return causes"
    ),
    
    # Documentation
    CommandExample(
        voice_input="Add documentation to all public methods",
        command_type=VoiceCommand.ADD_DOCSTRING,
        parameters={
            "target": "public_methods",
            "style": "google",
            "include": ["parameters", "returns", "examples"]
        },
        expected_action="Generate Google-style docstrings for all public methods"
    ),
    
    CommandExample(
        voice_input="Explain what this recursive function does",
        command_type=VoiceCommand.EXPLAIN_CODE,
        parameters={
            "target": "current_function",
            "detail_level": "comprehensive",
            "include_complexity": True
        },
        expected_action="Provide detailed explanation of recursive function logic"
    ),
]


class VoiceCommandProcessor:
    """Process natural language voice commands into structured actions"""
    
    def __init__(self):
        self.command_patterns = self._build_command_patterns()
        
    def _build_command_patterns(self) -> Dict[VoiceCommand, List[str]]:
        """Build patterns for recognizing commands"""
        return {
            VoiceCommand.CREATE_FILE: [
                "create a new", "make a new", "new file", "create file"
            ],
            VoiceCommand.CREATE_FUNCTION: [
                "create a function", "make a function", "new function",
                "write a function", "implement function"
            ],
            VoiceCommand.CREATE_CLASS: [
                "create a class", "make a class", "new class",
                "define class", "implement class"
            ],
            VoiceCommand.REFACTOR_CODE: [
                "refactor", "improve", "optimize", "clean up",
                "make better", "reorganize"
            ],
            VoiceCommand.WRITE_TEST: [
                "write test", "create test", "add test",
                "test for", "unit test"
            ],
            VoiceCommand.DEBUG_CODE: [
                "debug", "fix bug", "why doesn't", "not working",
                "investigate", "troubleshoot"
            ],
            VoiceCommand.EXPLAIN_CODE: [
                "explain", "what does", "how does", "understand",
                "clarify", "describe"
            ],
        }
        
    def parse_voice_command(self, voice_input: str) -> Dict[str, Any]:
        """Parse natural language into structured command"""
        voice_lower = voice_input.lower()
        
        # Identify command type
        command_type = None
        for cmd, patterns in self.command_patterns.items():
            if any(pattern in voice_lower for pattern in patterns):
                command_type = cmd
                break
                
        if not command_type:
            return {
                "type": "unknown",
                "original_input": voice_input,
                "suggestion": "Please be more specific about what you want to do"
            }
            
        # Extract parameters based on command type
        parameters = self._extract_parameters(voice_input, command_type)
        
        return {
            "type": command_type.value,
            "parameters": parameters,
            "original_input": voice_input
        }
        
    def _extract_parameters(self, voice_input: str, command_type: VoiceCommand) -> Dict[str, Any]:
        """Extract relevant parameters from voice input"""
        parameters = {}
        
        if command_type == VoiceCommand.CREATE_FUNCTION:
            # Extract function name and purpose
            if " to " in voice_input:
                purpose = voice_input.split(" to ", 1)[1]
                parameters["purpose"] = purpose
                
            # Try to extract function name
            words = voice_input.split()
            if "called" in words:
                idx = words.index("called")
                if idx + 1 < len(words):
                    parameters["name"] = words[idx + 1]
                    
        elif command_type == VoiceCommand.CREATE_CLASS:
            # Extract class name
            if " for " in voice_input:
                purpose = voice_input.split(" for ", 1)[1]
                parameters["purpose"] = purpose
                
            # Extract methods if mentioned
            if " with " in voice_input:
                with_part = voice_input.split(" with ", 1)[1]
                # Simple method extraction
                methods = [m.strip() for m in with_part.split(" and ")]
                parameters["methods"] = methods
                
        elif command_type == VoiceCommand.RENAME_VARIABLE:
            # Extract old and new names
            if " to " in voice_input:
                parts = voice_input.split(" to ")
                if len(parts) >= 2:
                    # Extract old name (last word before "to")
                    old_parts = parts[0].split()
                    if old_parts:
                        parameters["old_name"] = old_parts[-1]
                    parameters["new_name"] = parts[1].split()[0]
                    
        return parameters


def generate_claude_prompt(parsed_command: Dict[str, Any]) -> str:
    """Generate a Claude-friendly prompt from parsed voice command"""
    command_type = parsed_command.get("type")
    params = parsed_command.get("parameters", {})
    
    prompts = {
        "create_function": f"Create a function {params.get('name', '')} to {params.get('purpose', 'perform the requested task')}",
        "create_class": f"Create a class for {params.get('purpose', 'the requested functionality')} with methods: {', '.join(params.get('methods', []))}",
        "refactor_code": f"Refactor the current code to {params.get('improvement', 'improve readability and performance')}",
        "write_test": f"Write comprehensive unit tests for {params.get('target', 'the current module')}",
        "debug_code": f"Debug the issue: {params.get('issue', 'identify and fix the problem')}",
        "explain_code": f"Explain how this code works: {params.get('context', 'provide a clear explanation')}",
    }
    
    return prompts.get(command_type, parsed_command.get("original_input", ""))


# Example usage and testing
if __name__ == "__main__":
    processor = VoiceCommandProcessor()
    
    # Test various voice commands
    test_commands = [
        "Create a function called validate_password to check password strength",
        "Create a class for managing database connections with connect and disconnect methods",
        "Refactor this code to use async await",
        "Write unit tests for the user authentication module",
        "Debug why this function returns undefined",
        "Explain what this recursive fibonacci function does",
        "Rename all instances of temp_var to meaningful_name",
        "Add documentation to all public methods in this class",
    ]
    
    print("Voice Command Processing Examples:\n")
    for command in test_commands:
        print(f"Voice: \"{command}\"")
        parsed = processor.parse_voice_command(command)
        print(f"Parsed: {json.dumps(parsed, indent=2)}")
        prompt = generate_claude_prompt(parsed)
        print(f"Claude Prompt: {prompt}")
        print("-" * 60)