def add(a, b):
    return a + b


def main():
    tmp = 0
    for i in range(100000):
        tmp += add(i, i % 17) % 100000
    return tmp


if __name__ == "__main__":
    main()
