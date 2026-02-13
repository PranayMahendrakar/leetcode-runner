import json, time, os
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

CODE = """class Solution:
    def isPalindrome(self, x: int) -> bool:
        if x < 0:
            return False
        return str(x) == str(x)[::-1]"""

# Step 1: Get question ID
req = Request("https://leetcode.com/graphql", json.dumps({
    "query": "query q($s:String!){question(titleSlug:$s){questionId title}}",
    "variables": {"s": "palindrome-number"}
}).encode(), HEADERS, method="POST")
info = json.loads(urlopen(req).read())["data"]["question"]
print(f"Problem: {info['questionId']}. {info['title']}")

# Step 2: Submit
req = Request(f"https://leetcode.com/problems/palindrome-number/submit/",
    json.dumps({"lang": "python3", "question_id": info["questionId"], "typed_code": CODE}).encode(),
    HEADERS, method="POST")
sid = json.loads(urlopen(req).read())["submission_id"]
print(f"Submitted! ID: {sid}")

# Step 3: Wait for result
for _ in range(20):
    time.sleep(2)
    req = Request(f"https://leetcode.com/submissions/detail/{sid}/check/", headers=HEADERS)
    result = json.loads(urlopen(req).read())
    if result.get("state") == "SUCCESS":
        print(f"Result: {result.get('status_msg')} | Runtime: {result.get('status_runtime')} | Memory: {result.get('status_memory')}")
        break
