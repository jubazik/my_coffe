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