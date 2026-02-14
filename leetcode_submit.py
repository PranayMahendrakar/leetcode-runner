import json, time, os, random
from urllib.request import Request, urlopen

CSRF = os.environ["LEETCODE_CSRF"]
SESSION = os.environ["LEETCODE_SESSION"]
COOKIE = f"csrftoken={CSRF}; LEETCODE_SESSION={SESSION}"

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "Origin": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
    "Cookie": COOKIE,
    "x-csrftoken": CSRF,
}

# Pool of easy problems with their solutions
PROBLEMS = [
    {
        "slug": "palindrome-number",
        "code": """class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0:
            return False
        return str(x) == str(x)[::-1]"""
    },
    {
        "slug": "two-sum",
        "code": """class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, n in enumerate(nums):
            if target - n in seen:
                return [seen[target - n], i]
            seen[n] = i"""
    },
    {
        "slug": "roman-to-integer",
        "code": """class Solution:
    def romanToInt(self, s: str) -> int:
        m = {'I':1,'V':5,'X':10,'L':50,'C':100,'D':500,'M':1000}
        ans = 0
        for i in range(len(s)):
            if i + 1 < len(s) and m[s[i]] < m[s[i+1]]:
                ans -= m[s[i]]
            else:
                ans += m[s[i]]
        return ans"""
    },
    {
        "slug": "valid-parentheses",
        "code": """class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        mapping = {')':'(',']':'[','}':'{'}
        for c in s:
            if c in mapping:
                if not stack or stack[-1] != mapping[c]:
                    return False
                stack.pop()
            else:
                stack.append(c)
        return not stack"""
    },
    {
        "slug": "merge-two-sorted-lists",
        "code": """class Solution:
    def mergeTwoLists(self, list1, list2):
        if not list1: return list2
        if not list2: return list1
        if list1.val <= list2.val:
            list1.next = self.mergeTwoLists(list1.next, list2)
            return list1
        else:
            list2.next = self.mergeTwoLists(list1, list2.next)
            return list2"""
    },
    {
        "slug": "best-time-to-buy-and-sell-stock",
        "code": """class Solution:
    def maxProfit(self, prices) -> int:
        min_price = float('inf')
        max_profit = 0
        for p in prices:
            min_price = min(min_price, p)
            max_profit = max(max_profit, p - min_price)
        return max_profit"""
    },
    {
        "slug": "valid-anagram",
        "code": """class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        return sorted(s) == sorted(t)"""
    },
    {
        "slug": "contains-duplicate",
        "code": """class Solution:
    def containsDuplicate(self, nums) -> bool:
        return len(nums) != len(set(nums))"""
    },
]


def get_question_id(slug):
    req = Request("https://leetcode.com/graphql", json.dumps({
        "query": "query q($s:String!){question(titleSlug:$s){questionId title}}",
        "variables": {"s": slug}
    }).encode(), HEADERS, method="POST")
    info = json.loads(urlopen(req).read())["data"]["question"]
    return info


def submit_solution(slug, code, question_id):
    req = Request(f"https://leetcode.com/problems/{slug}/submit/",
        json.dumps({"lang": "python3", "question_id": question_id, "typed_code": code}).encode(),
        HEADERS, method="POST")
    sid = json.loads(urlopen(req).read())["submission_id"]
    return sid


def check_result(sid):
    for _ in range(20):
        time.sleep(2)
        req = Request(f"https://leetcode.com/submissions/detail/{sid}/check/", headers=HEADERS)
        result = json.loads(urlopen(req).read())
        if result.get("state") == "SUCCESS":
            return result
    return None


# Pick 1-3 random problems to submit
num_submissions = random.randint(1, 3)
chosen = random.sample(PROBLEMS, min(num_submissions, len(PROBLEMS)))

print(f"Will submit {len(chosen)} problem(s) this run")

for i, problem in enumerate(chosen):
    if i > 0:
        # Random delay between submissions (1-5 minutes)
        delay = random.randint(60, 300)
        print(f"Waiting {delay // 60}m {delay % 60}s before next submission...")
        time.sleep(delay)

    slug = problem["slug"]
    code = problem["code"]

    print(f"\n--- Submitting: {slug} ---")
    try:
        info = get_question_id(slug)
        print(f"Problem: {info['questionId']}. {info['title']}")

        sid = submit_solution(slug, code, info["questionId"])
        print(f"Submitted! ID: {sid}")

        result = check_result(sid)
        if result:
            print(f"Result: {result.get('status_msg')} | Runtime: {result.get('status_runtime')} | Memory: {result.get('status_memory')}")
        else:
            print("Timed out waiting for result")
    except Exception as e:
        print(f"Error submitting {slug}: {e}")

print("\nDone!")
