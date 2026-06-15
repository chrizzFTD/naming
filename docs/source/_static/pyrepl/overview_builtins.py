"""Interactive Overview examples for the built-in naming classes."""

from pprint import pprint

from naming import File, Name, Pipe, PipeFile


class BasicName(Name):
    config = dict(base=r'\w+')


class BasicPipe(Pipe):
    config = dict(base=r'\w+')


class BasicFile(File):
    config = dict(base=r'\w+')


class BasicPipeFile(PipeFile):
    config = dict(base=r'\w+')


def show(expression, value):
    print(f">>> {expression}")
    pprint(value)


def run_name_example():
    global n

    print("\nName")
    n = BasicName()
    show("n.get()", n.get())
    show("n.values", n.values)

    print(">>> n.name = 'hello_world'")
    n.name = 'hello_world'
    show("n", n)
    show("str(n)", str(n))
    show("n.values", n.values)

    print(">>> n.base = 'through_field_name'")
    n.base = 'through_field_name'
    show("n.values", n.values)
    show("n.base", n.base)


def run_pipe_example():
    global p

    print("\nPipe")
    p = BasicPipe()
    show("p.get()", p.get())
    show("p.get(version=10)", p.get(version=10))
    show("p.get(output='data')", p.get(output='data'))
    show("p.get(output='cache', version=7, index=24)", p.get(output='cache', version=7, index=24))

    print(">>> p = BasicPipe('my_wip_data.1')")
    p = BasicPipe('my_wip_data.1')
    show("p.version", p.version)
    show("p.values", p.values)
    show("p.get(output='exchange')", p.get(output='exchange'))
    show("p.name", p.name)

    print(">>> p.output = 'exchange'")
    p.output = 'exchange'
    show("p.name", p.name)

    print(">>> p.index = 101")
    p.index = 101
    print(">>> p.version = 7")
    p.version = 7
    show("p.name", p.name)
    show("p.values", p.values)


def run_file_example():
    global f

    print("\nFile")
    f = BasicFile()
    show("f.get()", f.get())
    show("f.get(suffix='png')", f.get(suffix='png'))

    print(">>> f = BasicFile('hello.world')")
    f = BasicFile('hello.world')
    show("f.values", f.values)
    show("f.suffix", f.suffix)

    print(">>> f.suffix = 'abc'")
    f.suffix = 'abc'
    show("f.name", f.name)
    show("f.path", f.path)


def run_pipefile_example():
    global pf

    print("\nPipeFile")
    print(">>> pf = BasicPipeFile('wipfile.7.ext')")
    pf = BasicPipeFile('wipfile.7.ext')
    show("pf.values", pf.values)
    show("[pf.get(index=x, output='render') for x in range(10)]", [
        pf.get(index=x, output='render') for x in range(10)
    ])


def run_all_examples():
    run_name_example()
    run_pipe_example()
    run_file_example()
    run_pipefile_example()


def setup():
    print("Loaded BasicName, BasicPipe, BasicFile, and BasicPipeFile.")
    print("The overview examples are running now; use the prompt afterward to experiment.")
    run_all_examples()
    print("\nTry: n.base = 'new_value', p.get(version=12), f.suffix = 'txt', or pf.values")
