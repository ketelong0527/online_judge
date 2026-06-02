import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'online_judge.settings')
django.setup()

from oj_problems.models import Problem, TestCase, DifficultyLevel
from oj_users.models import User


def create_sample_problems():
    problems = [
        {
            'title': '两数之和',
            'slug': 'two-sum',
            'description': '给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。\n\n你可以假设每种输入只会对应一个答案，并且你不能使用两次相同的元素。\n\n你可以按任意顺序返回答案。',
            'input_description': '第一行输入一个整数 n，表示数组长度。\n第二行输入 n 个整数，表示数组元素。\n第三行输入目标值 target。',
            'output_description': '输出两个整数，表示两个数的下标。',
            'sample_input': '4\n2 7 11 15\n9',
            'sample_output': '0 1',
            'hint': '可以使用哈希表来优化时间复杂度。',
            'difficulty': DifficultyLevel.EASY,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '反转链表',
            'slug': 'reverse-linked-list',
            'description': '给你单链表的头节点 head，请你反转链表，并返回反转后的链表。',
            'input_description': '第一行输入链表节点个数 n。\n第二行输入 n 个整数，表示链表各节点的值。',
            'output_description': '输出反转后的链表节点值，用空格分隔。',
            'sample_input': '5\n1 2 3 4 5',
            'sample_output': '5 4 3 2 1',
            'hint': '可以使用迭代或递归两种方法。',
            'difficulty': DifficultyLevel.EASY,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '最长回文子串',
            'slug': 'longest-palindromic-substring',
            'description': '给你一个字符串 s，找到 s 中最长的回文子串。\n\n如果字符串的反序与原始字符串相同，则该字符串称为回文字符串。',
            'input_description': '输入一个字符串 s。',
            'output_description': '输出最长的回文子串。',
            'sample_input': 'babad',
            'sample_output': 'bab',
            'hint': '可以使用动态规划或中心扩展算法。',
            'difficulty': DifficultyLevel.MEDIUM,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '二叉树的最大深度',
            'slug': 'maximum-depth-of-binary-tree',
            'description': '给定一个二叉树 root，返回其最大深度。\n\n二叉树的最大深度是指从根节点到最远叶子节点的最长路径上的节点数。',
            'input_description': '输入二叉树的层序遍历序列，空节点用 -1 表示。',
            'output_description': '输出二叉树的最大深度。',
            'sample_input': '3 9 20 -1 -1 15 7',
            'sample_output': '3',
            'hint': '可以使用递归或 BFS 方法。',
            'difficulty': DifficultyLevel.EASY,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '合并区间',
            'slug': 'merge-intervals',
            'description': '以数组 intervals 表示若干个区间的集合，其中单个区间为 intervals[i] = [starti, endi] 。请你合并所有重叠的区间。',
            'input_description': '第一行输入区间个数 n。\n接下来 n 行每行输入两个整数，表示区间的起点和终点。',
            'output_description': '输出合并后的区间，每个区间一行。',
            'sample_input': '4\n1 3\n2 6\n8 10\n15 18',
            'sample_output': '1 6\n8 10\n15 18',
            'hint': '先按区间起点排序。',
            'difficulty': DifficultyLevel.MEDIUM,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '接雨水',
            'slug': 'trapping-rain-water',
            'description': '给定 n 个非负整数表示每个宽度为 1 的柱子的高度图，计算按此排列的柱子，下雨之后能接多少雨水。',
            'input_description': '第一行输入柱子个数 n。\n第二行输入 n 个整数，表示柱子高度。',
            'output_description': '输出能接的雨水量。',
            'sample_input': '6\n0 1 0 2 1 0 1 3 2 1 2 1',
            'sample_output': '6',
            'hint': '可以使用双指针或单调栈方法。',
            'difficulty': DifficultyLevel.HARD,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '爬楼梯',
            'slug': 'climbing-stairs',
            'description': '假设你正在爬楼梯。需要 n 阶你才能到达楼顶。\n\n每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？',
            'input_description': '输入一个整数 n。',
            'output_description': '输出爬楼梯的方法数。',
            'sample_input': '3',
            'sample_output': '3',
            'hint': '这是一个斐波那契数列问题。',
            'difficulty': DifficultyLevel.EASY,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '三数之和',
            'slug': 'three-sum',
            'description': '给你一个整数数组 nums，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k ，同时还满足 nums[i] + nums[j] + nums[k] == 0 。请你返回所有和为 0 且不重复的三元组。',
            'input_description': '第一行输入整数 n。\n第二行输入 n 个整数。',
            'output_description': '输出所有满足条件的三元组。',
            'sample_input': '6\n-1 0 1 2 -1 -4',
            'sample_output': '-1 -1 2\n-1 0 1',
            'hint': '先排序，然后使用双指针。',
            'difficulty': DifficultyLevel.MEDIUM,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '无重复字符的最长子串',
            'slug': 'longest-substring-without-repeating-characters',
            'description': '给定一个字符串 s，请你找出其中不含有重复字符的最长子串的长度。',
            'input_description': '输入一个字符串 s。',
            'output_description': '输出最长无重复子串的长度。',
            'sample_input': 'abcabcbb',
            'sample_output': '3',
            'hint': '可以使用滑动窗口方法。',
            'difficulty': DifficultyLevel.MEDIUM,
            'time_limit': 2000,
            'memory_limit': 256
        },
        {
            'title': '合并两个有序链表',
            'slug': 'merge-two-sorted-lists',
            'description': '将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。',
            'input_description': '第一行输入第一个链表节点数 n1 和节点值。\n第二行输入第二个链表节点数 n2 和节点值。',
            'output_description': '输出合并后的链表节点值。',
            'sample_input': '3 1 2 4\n3 1 3 4',
            'sample_output': '1 1 2 3 4 4',
            'hint': '可以使用递归或迭代方法。',
            'difficulty': DifficultyLevel.EASY,
            'time_limit': 2000,
            'memory_limit': 256
        }
    ]

    for idx, data in enumerate(problems, 1):
        problem, created = Problem.objects.get_or_create(
            title=data['title'],
            defaults=data
        )
        if created:
            print(f"Created problem {idx}: {data['title']}")
            
            test_cases = get_test_cases(idx)
            for tc_data in test_cases:
                TestCase.objects.create(problem=problem, **tc_data)
                print(f"  Created test case for {data['title']}")


def get_test_cases(problem_idx):
    test_cases = {
        1: [
            {'input_data': '4\n2 7 11 15\n9', 'expected_output': '0 1', 'is_sample': True, 'order': 1},
            {'input_data': '3\n3 2 4\n6', 'expected_output': '1 2', 'is_sample': False, 'order': 2},
            {'input_data': '2\n3 3\n6', 'expected_output': '0 1', 'is_sample': False, 'order': 3}
        ],
        2: [
            {'input_data': '5\n1 2 3 4 5', 'expected_output': '5 4 3 2 1', 'is_sample': True, 'order': 1},
            {'input_data': '1\n1', 'expected_output': '1', 'is_sample': False, 'order': 2},
            {'input_data': '2\n1 2', 'expected_output': '2 1', 'is_sample': False, 'order': 3}
        ],
        3: [
            {'input_data': 'babad', 'expected_output': 'bab', 'is_sample': True, 'order': 1},
            {'input_data': 'cbbd', 'expected_output': 'bb', 'is_sample': False, 'order': 2},
            {'input_data': 'a', 'expected_output': 'a', 'is_sample': False, 'order': 3}
        ],
        4: [
            {'input_data': '3 9 20 -1 -1 15 7', 'expected_output': '3', 'is_sample': True, 'order': 1},
            {'input_data': '1 -1', 'expected_output': '1', 'is_sample': False, 'order': 2},
            {'input_data': '1 2 -1 -1 3 -1 -1', 'expected_output': '3', 'is_sample': False, 'order': 3}
        ],
        5: [
            {'input_data': '4\n1 3\n2 6\n8 10\n15 18', 'expected_output': '1 6\n8 10\n15 18', 'is_sample': True, 'order': 1},
            {'input_data': '2\n1 4\n4 5', 'expected_output': '1 5', 'is_sample': False, 'order': 2}
        ],
        6: [
            {'input_data': '12\n0 1 0 2 1 0 1 3 2 1 2 1', 'expected_output': '6', 'is_sample': True, 'order': 1},
            {'input_data': '2\n4 2 0 3 2 5', 'expected_output': '9', 'is_sample': False, 'order': 2}
        ],
        7: [
            {'input_data': '3', 'expected_output': '3', 'is_sample': True, 'order': 1},
            {'input_data': '4', 'expected_output': '5', 'is_sample': False, 'order': 2},
            {'input_data': '1', 'expected_output': '1', 'is_sample': False, 'order': 3}
        ],
        8: [
            {'input_data': '6\n-1 0 1 2 -1 -4', 'expected_output': '-1 -1 2\n-1 0 1', 'is_sample': True, 'order': 1},
            {'input_data': '0', 'expected_output': '', 'is_sample': False, 'order': 2},
            {'input_data': '1\n0', 'expected_output': '', 'is_sample': False, 'order': 3}
        ],
        9: [
            {'input_data': 'abcabcbb', 'expected_output': '3', 'is_sample': True, 'order': 1},
            {'input_data': 'bbbbb', 'expected_output': '1', 'is_sample': False, 'order': 2},
            {'input_data': 'pwwkew', 'expected_output': '3', 'is_sample': False, 'order': 3}
        ],
        10: [
            {'input_data': '3 1 2 4\n3 1 3 4', 'expected_output': '1 1 2 3 4 4', 'is_sample': True, 'order': 1},
            {'input_data': '0\n1 0', 'expected_output': '0', 'is_sample': False, 'order': 2},
            {'input_data': '1 1\n0', 'expected_output': '1', 'is_sample': False, 'order': 3}
        ]
    }
    return test_cases.get(problem_idx, [])


def create_sample_users():
    users = [
        {
            'username': 'coder001',
            'email': 'coder001@example.com',
            'password': '123456',
            'bio': '热爱算法的大学生',
            'rating': 1500,
            'rank': '入门选手',
            'total_solved': 50,
            'total_submissions': 120,
            'accepted_submissions': 50,
            'school': '清华大学',
            'github_url': 'https://github.com/coder001'
        },
        {
            'username': 'algorithm_master',
            'email': 'master@example.com',
            'password': '123456',
            'bio': 'ACM选手，多次获得区域赛金牌',
            'rating': 2500,
            'rank': '大师',
            'total_solved': 500,
            'total_submissions': 800,
            'accepted_submissions': 500,
            'school': '北京大学',
            'github_url': 'https://github.com/algorithm_master'
        },
        {
            'username': 'python_lover',
            'email': 'python@example.com',
            'password': '123456',
            'bio': 'Python爱好者，喜欢简洁优雅的代码',
            'rating': 1800,
            'rank': '进阶选手',
            'total_solved': 120,
            'total_submissions': 200,
            'accepted_submissions': 120,
            'location': '北京',
            'blog_url': 'https://pythonlover.com'
        }
    ]

    for data in users:
        password = data.pop('password')
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults=data
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created user: {data['username']}")


if __name__ == '__main__':
    print("Creating sample problems...")
    create_sample_problems()
    
    print("\nCreating sample users...")
    create_sample_users()
    
    print("\n✅ 示例数据添加完成！")
