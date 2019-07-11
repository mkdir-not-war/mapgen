from time import time

def steps(n, k):
    strn = str(n)
    if (len(strn) == 1):
        return k
    elif ('0' in strn):
        return k+1
    elif ('5' in strn and '2' in strn):
        return k+2
    else:
        nums = [int(i) for i in str(n)]

        result = 1
        for j in nums:
            result *= j
        return steps(result, k+1)

def run(n):
    return steps(n, 0)

def search():
    i = 1
    max_steps = 0
    t0 = time()
    
    while max_steps < 8:
        s = run(i)
        if (s > max_steps):
            print('steps: %d\t%d' % (s, i))
            max_steps = s
        i += 1

    t1 = time()
    result = t1-t0
    print('TIME %f' % result)

if __name__ == '__main__':
    search()
    
        
