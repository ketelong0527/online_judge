import subprocess
import tempfile
import os
import time
import json
from typing import Tuple, Optional


class CodeExecutor:
    TIME_LIMIT = 5
    MEMORY_LIMIT = 256
    
    LANGUAGE_CONFIG = {
        'python': {
            'extension': '.py',
            'compile_command': None,
            'run_command': ['python', '{filename}'],
            'timeout': 5
        },
        'c': {
            'extension': '.c',
            'compile_command': ['gcc', '{filename}', '-o', '{output}', '-lm'],
            'run_command': ['{output}'],
            'timeout': 5
        },
        'cpp': {
            'extension': '.cpp',
            'compile_command': ['g++', '{filename}', '-o', '{output}', '-std=c++17'],
            'run_command': ['{output}'],
            'timeout': 5
        },
        'java': {
            'extension': '.java',
            'compile_command': ['javac', '{filename}'],
            'run_command': ['java', '-cp', '{dir}', '{classname}'],
            'timeout': 10
        },
        'javascript': {
            'extension': '.js',
            'compile_command': None,
            'run_command': ['node', '{filename}'],
            'timeout': 5
        }
    }
    
    def __init__(self, language: str, time_limit: int = None, memory_limit: int = None):
        self.language = language
        self.time_limit = time_limit or self.TIME_LIMIT
        self.memory_limit = memory_limit or self.MEMORY_LIMIT
        
        if language not in self.LANGUAGE_CONFIG:
            raise ValueError(f"Unsupported language: {language}")
        
        self.config = self.LANGUAGE_CONFIG[language]
    
    def execute(self, code: str, input_data: str = '') -> Tuple[str, str, int]:
        output = ''
        error = ''
        execution_time = 0
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                filename = os.path.join(tmpdir, f'main{self.config["extension"]}')
                
                if self.language == 'java':
                    filename = os.path.join(tmpdir, 'Main.java')
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                if self.config['compile_command']:
                    compile_cmd = []
                    for cmd in self.config['compile_command']:
                        if cmd == '{dir}':
                            compile_cmd.append(tmpdir)
                        elif cmd == '{classname}':
                            compile_cmd.append('Main')
                        elif cmd == '{filename}':
                            compile_cmd.append(filename)
                        elif cmd == '{output}':
                            if self.language == 'c':
                                compile_cmd.append(os.path.join(tmpdir, 'main'))
                            elif self.language == 'cpp':
                                compile_cmd.append(os.path.join(tmpdir, 'main'))
                        else:
                            compile_cmd.append(cmd)
                    
                    compile_result = subprocess.run(
                        compile_cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=tmpdir
                    )
                    
                    if compile_result.returncode != 0:
                        error = f"编译错误:\n{compile_result.stderr}"
                        return output, error, execution_time
                
                run_cmd = []
                for cmd in self.config['run_command']:
                    if cmd == '{dir}':
                        run_cmd.append(tmpdir)
                    elif cmd == '{classname}':
                        run_cmd.append('Main')
                    elif cmd == '{filename}':
                        run_cmd.append(filename)
                    elif cmd == '{output}':
                        run_cmd.append(os.path.join(tmpdir, 'main'))
                    else:
                        run_cmd.append(cmd)
                
                start_time = time.time()
                
                process = subprocess.Popen(
                    run_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=tmpdir
                )
                
                try:
                    stdout, stderr = process.communicate(
                        input=input_data.strip(),
                        timeout=self.config['timeout']
                    )
                    execution_time = int((time.time() - start_time) * 1000)
                    
                    if process.returncode != 0:
                        error = f"运行错误:\n{stderr}"
                    else:
                        output = stdout
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    error = 'Time Limit Exceeded (TLE)'
                    execution_time = self.config['timeout'] * 1000
                    
        except Exception as e:
            error = f"执行错误: {str(e)}"
        
        return output, error, execution_time
    
    def judge(self, code: str, test_input: str, expected_output: str) -> dict:
        output, error, exec_time = self.execute(code, test_input)
        
        result = {
            'output': output,
            'error': error,
            'execution_time': exec_time,
            'status': 'Accepted'
        }
        
        if error:
            if 'Time Limit' in error or 'TLE' in error:
                result['status'] = 'Time Limit Exceeded'
            else:
                result['status'] = 'Runtime Error'
        elif self.normalize_output(output) != self.normalize_output(expected_output):
            result['status'] = 'Wrong Answer'
        
        return result
    
    @staticmethod
    def normalize_output(output: str) -> str:
        return output.strip().replace('\r\n', '\n')


class CodeJudge:
    def __init__(self, language: str = 'python'):
        self.language = language
        self.executor = CodeExecutor(language)
    
    def judge_submission(self, code: str, test_cases: list) -> dict:
        total_score = 0
        max_score = sum(tc.get('score', 10) for tc in test_cases)
        results = []
        
        for tc in test_cases:
            input_data = tc.get('input', '')
            expected_output = tc.get('output', '')
            score = tc.get('score', 10)
            
            result = self.executor.judge(code, input_data, expected_output)
            result['test_case_id'] = tc.get('id', 0)
            result['score'] = score if result['status'] == 'Accepted' else 0
            
            if result['status'] == 'Accepted':
                total_score += score
            
            results.append(result)
        
        overall_status = 'Accepted' if total_score == max_score else 'Wrong Answer'
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'status': overall_status,
            'results': results
        }
