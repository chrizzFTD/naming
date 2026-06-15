"""Interactive Overview examples for extending naming classes."""

from pprint import pprint

from naming import File, PipeFile


class BasicPipeFile(PipeFile):
    config = dict(base=r'\w+')


class ProjectFile(BasicPipeFile):
    config = dict(
        year='[0-9]{4}',
        user='[a-z]+',
        another='(constant)',
        last='[a-zA-Z0-9]+',
    )


class Dropper(BasicPipeFile):
    config = dict(without=r'[a-zA-Z0-9]+', basename=r'[a-zA-Z0-9]+')
    drop = ('base',)


Subdropper = type('Dropper', (Dropper,), dict(config=dict(subdrop=r'[\w]')))


class Compound(BasicPipeFile):
    config = dict(first=r'\d+', second=r'[a-zA-Z]+')
    join = dict(base=('first', 'second'))


class CompoundByDash(Compound):
    join_sep = '-'


class FilePath(File):
    config = dict(base=r'\w+', extrafield='[a-z0-9]+')

    def get_path_pattern_list(self):
        # The path is solved from the same fields used in the name.
        return super().get_pattern_list()


class PropertyField(PipeFile):
    config = dict(base=r'\w+', extrafield='[a-z0-9]+')

    @property
    def nameproperty(self):
        return 'staticvalue'

    @property
    def pathproperty(self):
        return 'path_field'

    def get_path_pattern_list(self):
        result = super().get_pattern_list()
        result.append('pathproperty')
        return result

    def get_pattern_list(self):
        result = super().get_pattern_list()
        result.append('nameproperty')
        return result


def show(expression, value):
    print(f">>> {expression}")
    pprint(value)


def run_project_file_example():
    global project_file

    print("\nInheriting from an existing name")
    print(">>> project_file = ProjectFile('project_data_name_2017_christianl_constant_iamlast.data.17.abc', sep='_')")
    project_file = ProjectFile('project_data_name_2017_christianl_constant_iamlast.data.17.abc', sep='_')
    show("project_file.values", project_file.values)
    show("project_file.nice_name", project_file.nice_name)
    show("project_file.year", project_file.year)

    print(">>> project_file.year = 'nondigits'")
    try:
        project_file.year = 'nondigits'
    except ValueError as exc:
        print(f"ValueError: {exc}")

    print(">>> project_file.year = 1907")
    project_file.year = 1907
    show("project_file", project_file)
    show("project_file.suffix", project_file.suffix)

    print(">>> project_file.sep = '  '")
    project_file.sep = '  '
    show("project_file.name", project_file.name)


def run_dropper_example():
    global dropper, subdropper

    print("\nDropping fields from bases")
    dropper = Dropper()
    show("dropper.get()", dropper.get())

    subdropper = Subdropper()
    show("subdropper.get()", subdropper.get())


def run_compound_example():
    global compound, compound_by_dash

    print("\nSetting compound fields")
    compound = Compound()
    show("compound.get()", compound.get())
    show("compound.get(first=50, second='abc')", compound.get(first=50, second='abc'))

    print(">>> compound.name = compound.get(base='101dalmatians', version=1, suffix='png')")
    compound.name = compound.get(base='101dalmatians', version=1, suffix='png')
    show("compound.nice_name", compound.nice_name)
    show("compound.get(first=200)", compound.get(first=200))

    print(">>> compound_by_dash = CompoundByDash('101-dalmatians.1.png')")
    compound_by_dash = CompoundByDash('101-dalmatians.1.png')
    show("compound_by_dash.get(first=300)", compound_by_dash.get(first=300))


def run_file_path_example():
    global file_path

    print("\nDefining path rules for File subclasses")
    file_path = FilePath()
    show("file_path.get()", file_path.get())
    show("file_path.path", file_path.path)


def run_property_field_example():
    global property_field

    print("\nUsing properties as fields while solving names")
    property_field = PropertyField()
    show("property_field.get()", property_field.get())

    print(">>> property_field.name = 'simple props staticvalue.1.abc'")
    property_field.name = 'simple props staticvalue.1.abc'
    show("property_field.values", property_field.values)
    show("property_field.path", property_field.path)


def run_all_examples():
    run_project_file_example()
    run_dropper_example()
    run_compound_example()
    run_file_path_example()
    run_property_field_example()


def setup():
    print("Loaded ProjectFile, Dropper, Compound, FilePath, and PropertyField examples.")
    print("The extension examples are running now; use the prompt afterward to experiment.")
    run_all_examples()
    print("\nTry: project_file.year = 2026, dropper.get(), compound.get(first=404), or property_field.values")
