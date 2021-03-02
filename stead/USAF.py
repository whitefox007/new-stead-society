list  = []
name = ''
while name != 'q':
    name = input('Enter guest name:\n')
    if name != 'q':
        list.append(name)
    else:
        print(list)