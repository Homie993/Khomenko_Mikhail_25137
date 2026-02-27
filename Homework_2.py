#1
# def fib(n):
#     if n == 1 or n == 2:
#         return 1
#     else:
#         return fib(n-1) + fib(n-2)
#     
# f1, f2 = 1, 1
# n = int(input())
# result = 0
# 
# for i in range(n-2):
#     result = f1 + f2
#     f1 = f2
#     f2 = result
#     
# print(result)

#2
# def is_correct_brackets_seq(st):
#     n = len(st)
#     k = 0;
#     for i in range(len(st)):
#         if k < 0: return False
#         if st[i] == '(':
#             k+=1
#         else:
#             k-=1
#     return k==0
#         
# print(is_correct_brackets_seq(input()))

#3
# def plus_one(a):
#     a.reverse()
#     k = len(a)
#     for i in range(k):
#         a[i] += 1
#         if a[i] == 10:
#             a[i] = 0
#             continue
#         else:
#             a.reverse()
#             return a
#     a.append(1)
#     a.reverse()
#     return a
# 
# print(plus_one(list(map(int, input().split()))))

#4
# def number_of_unique_characters(a):
#     answer_dict = dict()
#     for i in a:
#         if i not in answer_dict:
#             answer_dict[i] = 1
#             #answer_dict[i] = i
#         else:
#             answer_dict[i] += 1
#     return answer_dict
# 
# print(number_of_unique_characters(input()))

#5
# def two_sum(a, n):
#     p1,p2 = 0,len(a)-1
#     while(p1 < p2):
#         if a[p1][0] + a[p2][0] > n:
#             p2 -= 1
#         elif a[p1][0] + a[p2][0] < n:
#             p1 += 1
#         else:
#             return [a[p1][1], a[p2][1]]
#     return list()
# 
# a = list(map(int, input().split()))
# n = int(input())
'''if list a is not sorted:
# k = len(a)
# for i in range(k): a[i] = (a[i], i)
# a.sort()'''
# print(two_sum(a,n))

#6
# def format_number(n):
#     return f"{round(n,3):,.3f}".replace(',',' ').replace('.',' .').center(30,'*')
# 
# print(format_number(float(input())))
