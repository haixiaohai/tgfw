"""闭包closure"""

def outer_func(msg):
    def inner_func():
        print(msg)
    return inner_func


# 错误示例
def create_checks():
    funcs = []
    for i in range(3):
        funcs.append(lambda: i) # 闭包引用了 i
    return funcs

results = [f() for f in create_checks()]
# 你以为是 [0, 1, 2]，结果却是 [2, 2, 2]！

if __name__ == '__main__':
    print(results)