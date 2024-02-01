import random

A_win = 0
for i in range(1000000):
    current_round = []
    while len(current_round) < 2 or (current_round[-2:] != ['H','T'] and current_round[-2:] != ['T','T']):
        current_round.append(random.choice(['H','T']))
    if current_round[-2:] == ['T','T']:
        A_win += 1
    print(i)

print(A_win/1000000)