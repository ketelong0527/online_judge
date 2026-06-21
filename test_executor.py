import subprocess
import tempfile
import os
import time

language = 'python'
code = 'print("Hello World!")\nprint("2 + 2 =", 2 + 2)'
input_data = ''

with tempfile.TemporaryDirectory() as tmpdir:
    filename = os.path.join(tmpdir, 'main.py')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
    
    run_cmd = ['python', filename]
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
            timeout=5
        )
        exec_time = int((time.time() - start_time) * 1000)
        
        if process.returncode != 0:
            error = f"运行错误:\n{stderr}"
            print('Error:', repr(error))
        else:
            print('Output:', repr(stdout))
            print('Time:', exec_time, 'ms')
            
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        print('Timeout!')