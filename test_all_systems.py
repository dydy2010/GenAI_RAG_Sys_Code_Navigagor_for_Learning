"""
Comprehensive Test Suite for GenAI RAG System
Tests all modules, imports, file paths, and functionality
UPDATED to match actual directory structure
"""

import sys
import os
from pathlib import Path
import importlib
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestReport:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"{Colors.GREEN}✓{Colors.RESET} {test_name}")

    def add_fail(self, test_name, error):
        self.failed.append((test_name, error))
        print(f"{Colors.RED}✗{Colors.RESET} {test_name}: {error}")

    def add_warning(self, test_name, message):
        self.warnings.append((test_name, message))
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {test_name}: {message}")

    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

        print(f"{Colors.GREEN}Passed:{Colors.RESET} {len(self.passed)}")
        print(f"{Colors.RED}Failed:{Colors.RESET} {len(self.failed)}")
        print(f"{Colors.YELLOW}Warnings:{Colors.RESET} {len(self.warnings)}")

        if self.failed:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for test, error in self.failed:
                print(f"  • {test}: {error}")

        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings:{Colors.RESET}")
            for test, message in self.warnings:
                print(f"  • {test}: {message}")

        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")

        if len(self.failed) == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}ALL SYSTEMS OPERATIONAL ✓{Colors.RESET}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}SOME SYSTEMS NEED ATTENTION{Colors.RESET}")

        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def test_directory_structure(report):
    """Test if all expected directories exist"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[1] Testing Directory Structure{Colors.RESET}")

    expected_dirs = [
        'Final',
        'Final/chroma-db',
        'Final/data',
        'Final/data/parsed',
        'Final/data/raw',
        'Final/data/raw/Materials_code_learning',
        'Final/Evaluation',
        'Final/Evaluation/Results',
        'Final/Rag_Core',
        'Final/Rag_Core/module',
    ]

    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            report.add_pass(f"Directory exists: {dir_path}")
        else:
            report.add_warning(f"Directory missing: {dir_path}", "May need to be created")

def test_file_existence(report):
    """Test if all expected files exist - UPDATED PATHS"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[2] Testing File Existence{Colors.RESET}")

    expected_files = [
        'Final/Rag_Core/module/__init__.py',
        'Final/Rag_Core/module/data_collection.py',
        'Final/Rag_Core/module/database.py',
        'Final/Rag_Core/module/preprocessing.py',
        'Final/Rag_Core/RAG_Core.py',  # UPDATED - in Rag_Core folder
        'Final/Rag_Core/Streamlit_App.py',  # UPDATED - in Rag_Core folder
        'Final/Evaluation/check_eval.py',
        'Final/Evaluation/Evaluate_Ragas.py',
        'Final/Evaluation/Evaluation_Dataset.py',
    ]

    for file_path in expected_files:
        if os.path.exists(file_path):
            report.add_pass(f"File exists: {file_path}")
        else:
            report.add_fail(f"File missing: {file_path}", "Required file not found")

def test_imports(report):
    """Test if all modules can be imported"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[3] Testing Module Imports{Colors.RESET}")

    # Change to Final directory for imports
    original_dir = os.getcwd()
    try:
        os.chdir('Final/Rag_Core')  # UPDATED - go into Rag_Core folder
        sys.path.insert(0, os.getcwd())

        # Test module imports
        modules_to_test = [
            ('module.data_collection', 'Data Collection Module'),
            ('module.database', 'Database Module'),
            ('module.preprocessing', 'Preprocessing Module'),
        ]

        for module_name, display_name in modules_to_test:
            try:
                importlib.import_module(module_name)
                report.add_pass(f"Import {display_name}")
            except Exception as e:
                report.add_fail(f"Import {display_name}", str(e))

        # Test main scripts (check if they can be read, not executed)
        main_scripts = [
            ('RAG_Core.py', 'RAG Core Script'),
            ('Streamlit_App.py', 'Streamlit App Script'),
        ]

        for script_file, display_name in main_scripts:
            try:
                with open(script_file, 'r') as f:
                    content = f.read()
                    if len(content) > 0:
                        report.add_pass(f"{display_name} readable")
                    else:
                        report.add_warning(f"{display_name}", "File is empty")
            except Exception as e:
                report.add_fail(f"{display_name}", str(e))

    except Exception as e:
        report.add_fail("Import test setup", str(e))
    finally:
        os.chdir(original_dir)
        sys.path.pop(0)

def test_python_syntax(report):
    """Test Python syntax for all .py files"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[4] Testing Python Syntax{Colors.RESET}")

    python_files = [
        'Final/Rag_Core/module/data_collection.py',
        'Final/Rag_Core/module/database.py',
        'Final/Rag_Core/module/preprocessing.py',
        'Final/Rag_Core/RAG_Core.py',  # UPDATED
        'Final/Rag_Core/Streamlit_App.py',  # UPDATED
        'Final/Evaluation/check_eval.py',
        'Final/Evaluation/Evaluate_Ragas.py',
        'Final/Evaluation/Evaluation_Dataset.py',
    ]

    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                report.add_pass(f"Syntax valid: {os.path.basename(file_path)}")
            except SyntaxError as e:
                report.add_fail(f"Syntax error in {os.path.basename(file_path)}",
                              f"Line {e.lineno}: {e.msg}")
            except Exception as e:
                report.add_fail(f"Error reading {os.path.basename(file_path)}", str(e))
        else:
            report.add_warning(f"Cannot check syntax for {os.path.basename(file_path)}",
                             "File not found")

def test_dependencies(report):
    """Test if required dependencies are installed"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[5] Testing Dependencies{Colors.RESET}")

    required_packages = [
        'langchain',
        'langchain_core',
        'langchain_community',
        'langchain_text_splitters',
        'langchain_huggingface',
        'chromadb',
        'streamlit',
        'pandas',
        'numpy',
    ]

    optional_packages = [
        ('ragas', 'For evaluation'),
        ('openai', 'For OpenAI models'),
        ('langsmith', 'For LangSmith tracing'),
    ]

    for package in required_packages:
        try:
            importlib.import_module(package)
            report.add_pass(f"Package installed: {package}")
        except ImportError:
            report.add_fail(f"Package not installed: {package}",
                          "Required package missing")

    for package, purpose in optional_packages:
        try:
            importlib.import_module(package)
            report.add_pass(f"Optional package installed: {package}")
        except ImportError:
            report.add_warning(f"Optional package not installed: {package}",
                             f"{purpose} - install with: pip install {package}")

def test_database_files(report):
    """Test ChromaDB database files"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[6] Testing Database Files{Colors.RESET}")

    chroma_db_path = 'Final/chroma-db'

    if os.path.exists(chroma_db_path):
        report.add_pass("ChromaDB directory exists")

        # Check for SQLite file
        sqlite_file = os.path.join(chroma_db_path, 'chroma.sqlite3')
        if os.path.exists(sqlite_file):
            report.add_pass("ChromaDB SQLite file exists")

            # Check file size
            size = os.path.getsize(sqlite_file)
            if size > 0:
                report.add_pass(f"ChromaDB has data ({size:,} bytes)")
            else:
                report.add_warning("ChromaDB SQLite file is empty",
                                 "Database may need to be populated")
        else:
            report.add_warning("ChromaDB SQLite file not found",
                             "Database may need to be initialized")
    else:
        report.add_fail("ChromaDB directory not found",
                       "Vector database needs to be created")

def test_data_files(report):
    """Test if data files exist"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[7] Testing Data Files{Colors.RESET}")

    raw_data_path = 'Final/data/raw/Materials_code_learning'
    parsed_data_path = 'Final/data/parsed'

    # Check raw data
    if os.path.exists(raw_data_path):
        files = list(Path(raw_data_path).rglob('*.*'))
        if files:
            report.add_pass(f"Raw data found: {len(files)} files")
        else:
            report.add_warning("No raw data files found",
                             "May need to add source materials")
    else:
        report.add_warning("Raw data directory not found", "Check data path")

    # Check parsed data
    if os.path.exists(parsed_data_path):
        files = list(Path(parsed_data_path).glob('*.json'))
        if files:
            report.add_pass(f"Parsed data found: {len(files)} files")
        else:
            report.add_warning("No parsed data files found",
                             "May need to run preprocessing")
    else:
        report.add_warning("Parsed data directory not found", "Check data path")

def test_evaluation_files(report):
    """Test evaluation results files"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[8] Testing Evaluation Files{Colors.RESET}")

    results_path = 'Final/Evaluation/Results'

    if os.path.exists(results_path):
        csv_files = list(Path(results_path).glob('*.csv'))
        if csv_files:
            report.add_pass(f"Evaluation results found: {len(csv_files)} files")
            for csv_file in csv_files:
                size = os.path.getsize(csv_file)
                if size > 0:
                    report.add_pass(f"  • {csv_file.name} ({size:,} bytes)")
        else:
            report.add_warning("No evaluation results found",
                             "Run evaluation scripts to generate results")
    else:
        report.add_warning("Evaluation results directory not found",
                         "Directory may need to be created")

def test_config_paths(report):
    """Test if configuration paths in RAG_Core.py are correct"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[9] Testing Configuration Paths{Colors.RESET}")

    rag_core_file = 'Final/Rag_Core/RAG_Core.py'

    if os.path.exists(rag_core_file):
        try:
            with open(rag_core_file, 'r') as f:
                content = f.read()

            # Check for common configuration issues
            if 'JSON_FOLDER' in content:
                report.add_pass("JSON_FOLDER configuration found")
            else:
                report.add_warning("JSON_FOLDER not found in config",
                                 "May need to configure paths")

            if 'CHROMA_DIR' in content:
                report.add_pass("CHROMA_DIR configuration found")
            else:
                report.add_warning("CHROMA_DIR not found in config",
                                 "May need to configure paths")

            # Check for absolute paths that might need updating
            if '/Users/' in content or 'C:\\' in content:
                report.add_warning("Absolute paths found in configuration",
                                 "Consider using relative paths for portability")
            else:
                report.add_pass("No absolute paths detected")

        except Exception as e:
            report.add_fail("Error reading RAG_Core.py", str(e))
    else:
        report.add_fail("RAG_Core.py not found", "Cannot test configuration")

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}GenAI RAG System - Comprehensive Test Suite{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    report = TestReport()

    try:
        test_directory_structure(report)
        test_file_existence(report)
        test_python_syntax(report)
        test_imports(report)
        test_dependencies(report)
        test_database_files(report)
        test_data_files(report)
        test_evaluation_files(report)
        test_config_paths(report)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")

    report.print_summary()

    # Return exit code based on failures
    return 0 if len(report.failed) == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)