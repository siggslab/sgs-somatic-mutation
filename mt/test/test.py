from cloudpathlib import AnyPath

def test():
    with AnyPath(output_path('test.txt')).open('w+') as f:
    f.write('test contents')

if __name__ == "__main__":
    test()
