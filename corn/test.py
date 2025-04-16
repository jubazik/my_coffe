import re
test_text = '12@31fds@_.3fvd#$%& \t,sMDSl'
pattern_grammar = ['\d', '\D', '\s', '\S', '\w','\W', '.','[lmn]']
print(re.findall(r'f|d', test_text))
print(re.findall(r's|v',test_text ))
print(re.findall(r'1|2',test_text ))
print(re.findall(r'(fds)',test_text ))
print(re.findall(r'[^d,f,1,2]',test_text ))
for pattern in pattern_grammar:
    print(f'pattern: {pattern: <20} -----> {re.findall(pattern, test_text)}')

text_data = """
101, Homework; Complete physics and math
some random nonsense
102, Laundry; Wash all the clothes today
S4, random; record 
103, Museum; All about Egypt
1234, random; record
Another random record"""

tasks = []
# test = re.compile(r'(\d{3}), (\w+); (.+)')
test = re.compile(r"(?P<task_id>\d{3}), (?P<task_title>\w+); (?P<task_disc>.+) ")
for line in text_data.split("\n"):
    match = test.match(line)
    if match:
        task = (match.group("task_id"), match.group('task_title'), match.group('task_disc'))
        tasks.append(task)
        print(f"{'Matched:': <12}{match.groupdict()}")
    else:
        print(f"{'No Match:' :<12}{line}")

print(tasks)

for item in tasks:
    print(item)

print(tasks.__sizeof__())
print(text_data.__sizeof__())

task_text = [
    {'title': 'homework', 'desc': 'Physics + Math', 'urgency' : 3},
    {'title': 'desc', 'desc': 'Wash clothes', 'urgency': 5},
    {'title': 'Museum', 'desc': 'Egyptian things', 'urgency': 2}
]

def using_urgency_level(task_):
    return task_['urgency']


task_text.sort(key=using_urgency_level, reverse=True)
print(task_text)

class Task:
    def __init__(self, title, desc, urgency):
        pass