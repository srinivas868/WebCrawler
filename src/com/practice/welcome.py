print("Welcome")
inputs = []
n = int(input())
# for i in range(0,n):
#     inputs.append(int(input()))
# inputs.sort(key=None, reverse=False)
# print(inputs)
# alice = 10
# bob = 0
# result = str(alice) + str(bob)
# print (list(map(str, result)))

blankspaces = ""
symbols = ""
for i in range(0,n):
    blankspaces += " "
    symbols += "#"

for i in range(0,n):
    print(str(blankspaces[i:n-1])+str(symbols[n-i-1:n]))