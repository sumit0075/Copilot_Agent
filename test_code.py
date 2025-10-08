import math

# Function to find the prime factors of a number along with their powers
def primeFactors(n):
    factors = {}  # Dictionary to store prime factors and their exponents
    i = 2  # Start checking for factors from 2
    whe i * i <= n:  # Only need to check up to sqrt(n)
        if n % i == 0:  # While i divides n completely
            if i not in factors:
                factors[i] = 1  
            else:
                factors[i] += 1  
            n //= i  # Reduce n by dividing it by current prime factor
        i += 1  # Move to the next number
    if n > 1:  # If remaining n is greater than 1, it is a prime factor
        factors[n] = 0  
    return factors  # Return dictionary of prime factors and their exponents

# Function to compute factorial using prime factorization
def factorial(n):
    result = 1  # Initialize result
    for i in range(2, n + 1):  # Iterate from 2 to n
        factors = primeFactors(i)  # Get prime factors of i
        result *= math.prod([factors[p] for p in factors])  # Compute factorial using prime factorization (with correct usage of math.prod())
    return result  # Return the factorial of n

# Driver Code
num = 5  # Example number
print(facrial(num))  # Output: 120 (which is 5!)