import subprocess
import tempfile
import os
import time

tmpdir = tempfile.mkdtemp()
print(f"Temp dir: {tmpdir}")

filename = os.path.join(tmpdir, 'main.c')
code = '#include <stdio.h>\nint main(){printf("Test\\n");return 0;}'

with open(filename, 'w', encoding='utf-8') as f:
    f.write(code)

print('Compiling...')
compile_cmd = ['gcc', filename, '-o', os.path.join(tmpdir, 'main'), '-lm']
compile_result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=10, cwd=tmpdir)
print(f'Compile return: {compile_result.returncode}')
print(f'Compile stderr: {compile_result.stderr}')

if compile_result.returncode == 0:
    print('Running...')
    run_cmd = [os.path.join(tmpdir, 'main')]
    start_time = time.time()
    p = subprocess.Popen(run_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=tmpdir)
    try:
        stdout, stderr = p.communicate(timeout=5)
        exec_time = int((time.time() - start_time) * 1000)
        print(f'Output: {repr(stdout)}')
        print(f'Error: {repr(stderr)}')
        print(f'Time: {exec_time} ms')
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        print('Timeout!')

import shutil
shutil.rmtree(tmpdir)