def primeFactors(n):
    factors = {}  
    i = 2  
    while i * i <= n:  
        if n % i == 0:  
            if i not in factors:
                factors[i] = 1  
            else:
                factors[i] += 1  
            n //= i  
        i += 1  
    if n > 1:  
        factors[n] = 0  
    return factors  

def factorial(n):
    result = 1  
    for i in range(2, n + 1):  
        factors = primeFactors(i)  
        result *= math.prod([factors[p] for p in factors]) 
    return result 

import math

num = 5  
print(factorial(num))