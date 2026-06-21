from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Problem, TestCase
from .executor import CodeExecutor
from oj_submissions.models import Submission, Language, SubmissionStatus
from oj_users.models import User
from oj_judge.judge_queue import update_user_statistics
from django.core.paginator import Paginator
import json


def problem_list(request):
    difficulty = request.GET.get('difficulty', '')
    search_query = request.GET.get('search', '')
    
    problems = Problem.objects.filter(is_public=True)
    
    if difficulty:
        problems = problems.filter(difficulty=difficulty)
    
    if search_query:
        problems = problems.filter(title__icontains=search_query)
    
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    difficulties = ['Easy', 'Medium', 'Hard']
    
    return render(request, 'oj_problems/problem_list.html', {
        'page_obj': page_obj,
        'difficulties': difficulties,
        'current_difficulty': difficulty,
        'search_query': search_query,
    })


def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, is_public=True)
    
    test_cases = problem.test_cases.all()
    
    return render(request, 'oj_problems/problem_detail.html', {
        'problem': problem,
        'test_cases': test_cases,
    })


def get_sample_code(problem_title, language):
    sample_codes = {
        'two-sum': {
            'python': '''n = int(input())
nums = list(map(int, input().split()))
target = int(input())
hash_map = {}
for i, num in enumerate(nums):
    complement = target - num
    if complement in hash_map:
        print(hash_map[complement], i)
        break
    hash_map[num] = i''',
            'c': '''#include <stdio.h>

int main() {
    int n, target;
    scanf("%d", &n);
    int nums[10000];
    for (int i = 0; i < n; i++) {
        scanf("%d", &nums[i]);
    }
    scanf("%d", &target);
    
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            if (nums[i] + nums[j] == target) {
                printf("%d %d\\n", i, j);
                return 0;
            }
        }
    }
    return 0;
}''',
            'cpp': '''#include <iostream>
#include <unordered_map>
using namespace std;

int main() {
    int n, target;
    cin >> n;
    int nums[10000];
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }
    cin >> target;
    
    unordered_map<int, int> hash_map;
    for (int i = 0; i < n; i++) {
        int complement = target - nums[i];
        if (hash_map.find(complement) != hash_map.end()) {
            cout << hash_map[complement] << " " << i << endl;
            return 0;
        }
        hash_map[nums[i]] = i;
    }
    return 0;
}''',
            'java': '''import java.util.Scanner;
import java.util.HashMap;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            nums[i] = scanner.nextInt();
        }
        int target = scanner.nextInt();
        
        HashMap<Integer, Integer> hashMap = new HashMap<>();
        for (int i = 0; i < n; i++) {
            int complement = target - nums[i];
            if (hashMap.containsKey(complement)) {
                System.out.println(hashMap.get(complement) + " " + i);
                return;
            }
            hashMap.put(nums[i], i);
        }
    }
}'''
        },
        'reverse-linked-list': {
            'python': '''n = int(input())
nums = list(map(int, input().split()))
print(' '.join(map(str, reversed(nums))))''',
            'c': '''#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);
    int nums[10000];
    for (int i = 0; i < n; i++) {
        scanf("%d", &nums[i]);
    }
    for (int i = n - 1; i >= 0; i--) {
        printf("%d", nums[i]);
        if (i > 0) printf(" ");
    }
    printf("\\n");
    return 0;
}''',
            'cpp': '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    int nums[10000];
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }
    for (int i = n - 1; i >= 0; i--) {
        cout << nums[i];
        if (i > 0) cout << " ";
    }
    cout << endl;
    return 0;
}''',
            'java': '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            nums[i] = scanner.nextInt();
        }
        StringBuilder sb = new StringBuilder();
        for (int i = n - 1; i >= 0; i--) {
            sb.append(nums[i]);
            if (i > 0) sb.append(" ");
        }
        System.out.println(sb.toString());
    }
}'''
        },
        'longest-palindromic-substring': {
            'python': '''s = input().strip()
n = len(s)
if n == 0:
    print("")
    exit()

start = 0
max_len = 1

for i in range(n):
    l, r = i, i
    while l >= 0 and r < n and s[l] == s[r]:
        if r - l + 1 > max_len:
            start = l
            max_len = r - l + 1
        l -= 1
        r += 1
    
    l, r = i, i + 1
    while l >= 0 and r < n and s[l] == s[r]:
        if r - l + 1 > max_len:
            start = l
            max_len = r - l + 1
        l -= 1
        r += 1

print(s[start:start + max_len])''',
            'c': '''#include <stdio.h>
#include <string.h>

int main() {
    char s[1000];
    scanf("%s", s);
    int n = strlen(s);
    if (n == 0) {
        printf("\\n");
        return 0;
    }
    
    int start = 0, max_len = 1;
    
    for (int i = 0; i < n; i++) {
        int l = i, r = i;
        while (l >= 0 && r < n && s[l] == s[r]) {
            if (r - l + 1 > max_len) {
                start = l;
                max_len = r - l + 1;
            }
            l--; r++;
        }
        
        l = i; r = i + 1;
        while (l >= 0 && r < n && s[l] == s[r]) {
            if (r - l + 1 > max_len) {
                start = l;
                max_len = r - l + 1;
            }
            l--; r++;
        }
    }
    
    for (int i = start; i < start + max_len; i++) {
        printf("%c", s[i]);
    }
    printf("\\n");
    return 0;
}''',
            'cpp': '''#include <iostream>
#include <string>
using namespace std;

int main() {
    string s;
    cin >> s;
    int n = s.length();
    if (n == 0) {
        cout << endl;
        return 0;
    }
    
    int start = 0, max_len = 1;
    
    for (int i = 0; i < n; i++) {
        int l = i, r = i;
        while (l >= 0 && r < n && s[l] == s[r]) {
            if (r - l + 1 > max_len) {
                start = l;
                max_len = r - l + 1;
            }
            l--; r++;
        }
        
        l = i; r = i + 1;
        while (l >= 0 && r < n && s[l] == s[r]) {
            if (r - l + 1 > max_len) {
                start = l;
                max_len = r - l + 1;
            }
            l--; r++;
        }
    }
    
    cout << s.substr(start, max_len) << endl;
    return 0;
}''',
            'java': '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String s = scanner.nextLine();
        int n = s.length();
        if (n == 0) {
            System.out.println();
            return;
        }
        
        int start = 0, maxLen = 1;
        
        for (int i = 0; i < n; i++) {
            int l = i, r = i;
            while (l >= 0 && r < n && s.charAt(l) == s.charAt(r)) {
                if (r - l + 1 > maxLen) {
                    start = l;
                    maxLen = r - l + 1;
                }
                l--; r++;
            }
            
            l = i; r = i + 1;
            while (l >= 0 && r < n && s.charAt(l) == s.charAt(r)) {
                if (r - l + 1 > maxLen) {
                    start = l;
                    maxLen = r - l + 1;
                }
                l--; r++;
            }
        }
        
        System.out.println(s.substring(start, start + maxLen));
    }
}'''
        },
        'maximum-depth-of-binary-tree': {
            'python': '''values = list(map(int, input().split()))
if not values:
    print(0)
    exit()

depth = 0
level_size = 1
next_level_size = 0

for val in values:
    level_size -= 1
    if val != -1:
        next_level_size += 2
    if level_size == 0:
        depth += 1
        level_size = next_level_size
        next_level_size = 0

print(depth)''',
            'c': '''#include <stdio.h>

int main() {
    int values[10000];
    int n = 0;
    while (scanf("%d", &values[n]) != EOF) {
        n++;
    }
    
    if (n == 0) {
        printf("0\\n");
        return 0;
    }
    
    int depth = 0;
    int level_size = 1;
    int next_level_size = 0;
    
    for (int i = 0; i < n; i++) {
        level_size--;
        if (values[i] != -1) {
            next_level_size += 2;
        }
        if (level_size == 0) {
            depth++;
            level_size = next_level_size;
            next_level_size = 0;
        }
    }
    
    printf("%d\\n", depth);
    return 0;
}''',
            'cpp': '''#include <iostream>
using namespace std;

int main() {
    int values[10000];
    int n = 0;
    while (cin >> values[n]) {
        n++;
    }
    
    if (n == 0) {
        cout << 0 << endl;
        return 0;
    }
    
    int depth = 0;
    int level_size = 1;
    int next_level_size = 0;
    
    for (int i = 0; i < n; i++) {
        level_size--;
        if (values[i] != -1) {
            next_level_size += 2;
        }
        if (level_size == 0) {
            depth++;
            level_size = next_level_size;
            next_level_size = 0;
        }
    }
    
    cout << depth << endl;
    return 0;
}''',
            'java': '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int[] values = new int[10000];
        int n = 0;
        while (scanner.hasNextInt()) {
            values[n++] = scanner.nextInt();
        }
        
        if (n == 0) {
            System.out.println(0);
            return;
        }
        
        int depth = 0;
        int levelSize = 1;
        int nextLevelSize = 0;
        
        for (int i = 0; i < n; i++) {
            levelSize--;
            if (values[i] != -1) {
                nextLevelSize += 2;
            }
            if (levelSize == 0) {
                depth++;
                levelSize = nextLevelSize;
                nextLevelSize = 0;
            }
        }
        
        System.out.println(depth);
    }
}'''
        },
        'climbing-stairs': {
            'python': '''n = int(input())
if n <= 2:
    print(n)
else:
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    print(b)''',
            'c': '''#include <stdio.h>

int main() {
    int n;
    scanf("%d", &n);
    
    if (n <= 2) {
        printf("%d\\n", n);
        return 0;
    }
    
    int a = 1, b = 2;
    for (int i = 3; i <= n; i++) {
        int temp = b;
        b = a + b;
        a = temp;
    }
    
    printf("%d\\n", b);
    return 0;
}''',
            'cpp': '''#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    
    if (n <= 2) {
        cout << n << endl;
        return 0;
    }
    
    int a = 1, b = 2;
    for (int i = 3; i <= n; i++) {
        int temp = b;
        b = a + b;
        a = temp;
    }
    
    cout << b << endl;
    return 0;
}''',
            'java': '''import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        
        if (n <= 2) {
            System.out.println(n);
            return;
        }
        
        int a = 1, b = 2;
        for (int i = 3; i <= n; i++) {
            int temp = b;
            b = a + b;
            a = temp;
        }
        
        System.out.println(b);
    }
}'''
        }
    }
    
    default_codes = {
        'python': 'print("Hello World!")\nprint("2 + 2 =", 2 + 2)',
        'c': '#include <stdio.h>\n\nint main() {\n    printf("Hello World!\\n");\n    printf("2 + 2 = %d\\n", 2+2);\n    return 0;\n}',
        'cpp': '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello World!" << endl;\n    cout << "2 + 2 = " << 2+2 << endl;\n    return 0;\n}',
        'java': 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello World!");\n        System.out.println("2 + 2 = " + (2+2));\n    }\n}'
    }
    
    slug = problem_title.lower().replace(' ', '-').replace('(', '').replace(')', '')
    if slug in sample_codes and language in sample_codes[slug]:
        return sample_codes[slug][language]
    return default_codes.get(language, default_codes['python'])


def code_editor(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id, is_public=True)
    language = request.GET.get('language', 'python')
    sample_code = get_sample_code(problem.title, language)
    
    sample_input = ''
    sample_test_case = problem.test_cases.filter(is_sample=True).first()
    if sample_test_case:
        sample_input = sample_test_case.input_data
    
    return render(request, 'oj_problems/code_editor.html', {
        'problem': problem,
        'language': language,
        'sample_code': sample_code,
        'sample_input': sample_input,
    })


@csrf_exempt
def submit_code(request, problem_id):
    if request.method == 'POST':
        problem = get_object_or_404(Problem, id=problem_id)
        
        try:
            data = json.loads(request.body)
            is_ajax = True
        except:
            data = request.POST
            is_ajax = False
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        user = request.user if request.user.is_authenticated else None
        
        submission = Submission.objects.create(
            problem=problem,
            user=user,
            code=code,
            language=language,
            status=SubmissionStatus.PENDING,
        )
        
        executor = CodeExecutor(language)
        
        test_cases = problem.test_cases.filter(is_sample=True)
        all_passed = True
        total_time = 0
        max_memory = 0
        
        for tc in test_cases:
            tc_output, tc_error, tc_time, tc_memory = executor.execute(code, tc.input_data)
            total_time += tc_time
            max_memory = max(max_memory, tc_memory)
            
            if tc_error or tc_output.strip() != tc.expected_output.strip():
                all_passed = False
                submission.error_message = tc_error or '答案错误'
                break
        
        if not test_cases.exists():
            output, error, total_time, max_memory = executor.execute(code, '')
            if error:
                all_passed = False
                submission.error_message = error
        
        if all_passed:
            submission.status = SubmissionStatus.ACCEPTED
        else:
            submission.status = SubmissionStatus.WRONG_ANSWER if not submission.error_message else SubmissionStatus.RUNTIME_ERROR
        
        submission.execution_time = total_time
        submission.execution_memory = max_memory
        submission.save()
        
        if user:
            update_user_statistics(user)
        
        if is_ajax:
            redirect_url = f'/submissions/{submission.id}/'
            return JsonResponse({'success': True, 'redirect_url': redirect_url, 'status': submission.status})
        else:
            return redirect('submission_detail', submission_id=submission.id)
    
    return redirect('code_editor', problem_id=problem_id)


class ProblemAPI(View):
    def get(self, request):
        problems = Problem.objects.filter(is_public=True).values(
            'id', 'title', 'slug', 'difficulty', 'total_submissions',
            'accepted_submissions', 'acceptance_rate'
        )
        return JsonResponse({'problems': list(problems)})


class ProblemDetailAPI(View):
    def get(self, request, problem_id):
        problem = get_object_or_404(Problem, id=problem_id, is_public=True)
        data = {
            'id': problem.id,
            'title': problem.title,
            'description': problem.description,
            'input_description': problem.input_description,
            'output_description': problem.output_description,
            'sample_input': problem.sample_input,
            'sample_output': problem.sample_output,
            'hint': problem.hint,
            'difficulty': problem.difficulty,
            'time_limit': problem.time_limit,
            'memory_limit': problem.memory_limit
        }
        return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class RunCodeAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except:
            data = request.POST
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        input_data = data.get('input', '')
        
        executor = CodeExecutor(language)
        output, error, exec_time, exec_memory = executor.execute(code, input_data)
        
        if error:
            return JsonResponse({'success': False, 'error': error})
        else:
            return JsonResponse({'success': True, 'output': output, 'time': exec_time})
