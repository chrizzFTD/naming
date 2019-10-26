import unittest
from pathlib import Path

import naming


class Name(naming.Name):
    config = dict(base=r'\w+')


class Pipe(naming.Pipe):
    config = dict(base=r'\w+')


class File(naming.File):
    config = dict(base=r'\w+')


class PipeFile(File, Pipe):
    pass


class TestName(unittest.TestCase):

    def test_empty_name(self):
        n = Name()
        self.assertEqual('{base}', n.get_name())
        self.assertEqual('{base}', str(n))

    def test_init_name(self):
        n = Name('initname')
        self.assertEqual('initname', n.get_name())
        with self.assertRaises(ValueError):
            Name(dict(my_name='dict'))
        n = Name(dict())
        self.assertFalse(None, n.get_name())

    def test_set_name(self):
        n = Name()
        n.name = 'setname'
        self.assertEqual('setname', n.get_name())

    def test_class_field_access(self):
        self.assertEqual(Name.base, None)


class TestConfig(unittest.TestCase):

    def test_assignment(self):
        n = Name()
        with self.assertRaises(AttributeError):
            n.config = 'foo'
        cfg = n.config
        with self.assertRaises(TypeError):
            cfg['base'] = 10
        self.assertTrue(cfg == n.config)


class TestEasyName(unittest.TestCase):

    def test_empty_name(self):
        n = Name()
        self.assertEqual('{base}', n.get_name())
        self.assertEqual({}, n.values)

    def test_new_empty_name(self):
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        Project = type('Project', (Name,), dict(config=extra_fields))
        p = Project(sep='_')
        self.assertEqual('{base}_{year}_{username}_{anotherfield}_{lastfield}', p.get_name())
        p.name = 'this_is_my_base_name_2017_christianl_constant_iamlast'
        self.assertEqual('2017', p.year)

    def test_separator(self):
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        Project = type('Project', (Name,), dict(config=extra_fields))
        p = Project('this_is_my_base_name_2017_christianl_constant_iamlast', sep='_')
        self.assertEqual('_', p.sep)
        p.sep = '  '
        self.assertEqual('this_is_my_base_name  2017  christianl  constant  iamlast', p.name)


class TestPipe(unittest.TestCase):

    def test_empty_name(self):
        p = Pipe()
        self.assertEqual('{base}.{pipe}', p.get_name())
        self.assertEqual('{base}.10', p.get_name(version=10))
        self.assertEqual('{base}.geo.10', p.get_name(version=10, output='geo'))
        self.assertEqual('{base}.geo.10.25', p.get_name(version=10, output='geo', frame=25))
        self.assertEqual('{base}.{output}.10.25', p.get_name(version=10, frame=25))
        self.assertEqual('{base}.{output}.{version}.101', p.get_name(frame=101))
        self.assertEqual('{base}.cache.{version}', p.get_name(output='cache'))
        self.assertEqual('{base}', p.get_name(pipe=None))

    def test_empty_name_separator(self):
        p = Pipe()
        for sep in ' ', '.', '/', '/ .':
            p.sep = sep
            self.assertEqual('{base}.{pipe}', p.get_name())
            self.assertEqual('{base}.10', p.get_name(version=10))
            self.assertEqual('{base}.geo.10', p.get_name(version=10, output='geo'))
            self.assertEqual('{base}.geo.10.25', p.get_name(version=10, output='geo', frame=25))
            self.assertEqual('{base}.{output}.10.25', p.get_name(version=10, frame=25))
            self.assertEqual('{base}.{output}.{version}.101', p.get_name(frame=101))
            self.assertEqual('{base}.cache.{version}', p.get_name(output='cache'))
            self.assertEqual('{base}', p.get_name(pipe=None))

    def test_init_name(self):
        p = Pipe('initname.pipeline.0')
        self.assertEqual('initname.pipeline.0', p.get_name())
        self.assertEqual('.pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        p = Pipe('initname.7')
        self.assertEqual('7', p.version)
        p = Pipe('initname.geo.0.1')
        self.assertEqual('0', p.version)
        self.assertEqual('1', p.frame)
        self.assertEqual('initname', p.nice_name)

        p = Pipe('name_with_underscores.pipeline.0')
        self.assertEqual('name_with_underscores.pipeline.0', p.get_name())
        self.assertEqual('.pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        p = Pipe('name_with_underscores.7')
        self.assertEqual('7', p.version)
        p = Pipe('name_with_underscores.geo.0.1')
        self.assertEqual('0', p.version)
        self.assertEqual('1', p.frame)
        self.assertEqual('name_with_underscores', p.nice_name)

    def test_set_name(self):
        p = Pipe()
        p.name = 'setname.pipeline.0'
        self.assertEqual('.pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        self.assertEqual('0', p.version)
        p.name = 'setname.pipeline.0.5'
        self.assertEqual('5', p.frame)
        self.assertEqual('setname', p.nice_name)

    def test_values(self):
        p = Pipe()
        p.name = 'my_pipe_file.1'
        self.assertEqual({'base': 'my_pipe_file', 'version': '1', 'pipe': '.1'}, p.values)

    def test_get_empty_name(self):
        p = Pipe()
        self.assertEqual('{base}.{pipe}', p.pipe_name)
        self.assertEqual('{base}.{pipe}', p.get_name())
        self.assertEqual('{base}.out.7', p.get_name(pipe='.out.7'))
        self.assertEqual('{base}.out.{version}', p.get_name(output='out'))
        self.assertEqual('{base}.7', p.get_name(version=7))
        self.assertEqual('{base}.{output}.{version}.101', p.get_name(frame=101))

    def test_get_init_name(self):
        p = Pipe('my_pipe_file.7')
        self.assertEqual('my_pipe_file.{output}.7.101', p.get_name(frame=101))
        self.assertEqual('my_pipe_file.cache.7', p.get_name(output='cache'))
        self.assertEqual('my_pipe_file.8', p.get_name(version=int(p.version) + 1))


class TestFile(unittest.TestCase):

    def test_empty_name(self):
        f = File()
        self.assertEqual('{base}.{suffix}', f.get_name())
        self.assertEqual('{base}.abc', f.get_name(suffix='abc'))
        self.assertEqual('{base}.{suffix}', f.get_name(suffix=''))

        f.name = 'myfile.ext'
        self.assertEqual('ext', f.suffix)
        self.assertEqual('myfile', f.base)
        self.assertEqual(f.get_name(), str(f.path))


class TestPipeFile(unittest.TestCase):

    def test_empty_name(self):
        f = PipeFile()
        self.assertEqual('{base}.{pipe}.{suffix}', f.get_name())
        self.assertEqual('{base}.{pipe}.abc', f.get_name(suffix='abc'))
        self.assertEqual('{base}.{pipe}.{suffix}', f.get_name(suffix=''))
        f.name = 'myfile.data.0.ext'
        self.assertEqual('ext', f.suffix)
        self.assertEqual('myfile', f.base)
        self.assertEqual('.data.0', f.pipe)
        self.assertEqual('0', f.version)
        self.assertEqual(f.get_name(), str(f.path))

    def test_set_property(self):
        pf = PipeFile()
        self.assertEqual('{base}.{pipe}.{suffix}', pf.get_name())
        with self.assertRaises(ValueError):
            pf.name = 'awesome'
        pf.name = 'hello_world.1.png'
        pf.base = 'awesome'
        self.assertEqual('awesome', pf.nice_name)
        self.assertEqual({'base': 'awesome', 'version': '1', 'pipe': '.1', 'suffix': 'png'}, pf.values)

        p = PipeFile('my_pipe_file.1.png')
        self.assertEqual({'base': 'my_pipe_file', 'version': '1', 'suffix': 'png', 'pipe': '.1'}, p.values)
        p.suffix = 'abc'
        self.assertEqual('my_pipe_file.1.abc', p.name)
        p.output = 'geometry'
        self.assertEqual('my_pipe_file.geometry.1.abc', p.name)
        p.version = 17
        self.assertEqual('my_pipe_file.geometry.17.abc', p.name)
        p.output = None
        self.assertEqual('my_pipe_file.geometry.17.abc', p.name)
        p.version = 0
        self.assertEqual('my_pipe_file.geometry.0.abc', p.name)
        self.assertEqual('PipeFile("my_pipe_file.geometry.0.abc")', repr(p))

    def test_set_name(self):
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        ProjectFile = type('ProjectFile', (PipeFile,), dict(config=extra_fields))
        pf = ProjectFile('this_is_my_base_name_2017_christianl_constant_iamlast.base.17.abc', sep='_')
        self.assertEqual('this_is_my_base_name_2017_christianl_constant_iamlast', pf.nice_name)
        self.assertEqual('this_is_my_base_name_2017_christianl_constant_iamlast.base.17', pf.pipe_name)
        # setting same fields should be returning early
        pf.year = 2017
        self.assertEqual('2017', pf.year)
        self.assertEqual('iamlast', pf.lastfield)
        self.assertEqual('abc', pf.suffix)
        pf = ProjectFile()
        self.assertEqual('{base} {year} {username} {anotherfield} {lastfield}.{pipe}.{suffix}', pf.get_name())
        self.assertEqual('', pf.name)
        pf.name = 'hello 2008 c constant last.1.abc'
        with self.assertRaises(ValueError):
            pf.year = 2
        v = pf.values.copy()
        self.assertEqual({'base': 'hello', 'year': '2008', 'username': 'c', 'anotherfield': 'constant',
                          'lastfield': 'last', 'pipe': '.1', 'version': '1', 'suffix': 'abc'}, v)
        self.assertFalse(v is pf.values)
        pf.sep = ' - '
        self.assertEqual('hello - 2008 - c - constant - last.1.abc', pf.name)
        self.assertTrue(pf.values == v)


class TestDrops(unittest.TestCase):

    def test_empty_name(self):
        Dropper = type('Dropper', (PipeFile,), dict(config=dict(without=r'[a-zA-Z0-9]+', basename=r'[a-zA-Z0-9]+'),
                                                    drop=('base',)))
        d = Dropper(sep='_')
        self.assertEqual('{without}_{basename}.{pipe}.{suffix}', d.get_name())
        self.assertEqual('awesome_{basename}.{pipe}.{suffix}', d.get_name(without='awesome'))
        self.assertEqual('{without}_replaced.{output}.{version}.101.{suffix}',
                         d.get_name(basename='replaced', frame=101))

        Subdropper = type('Dropper', (Dropper,), dict(config=dict(subdrop='[\w]')))
        s = Subdropper(sep='_')
        self.assertEqual('{without}_{basename}_{subdrop}.{pipe}.{suffix}', s.get_name())
        self.assertEqual('awesome_{basename}_{subdrop}.{pipe}.{suffix}', s.get_name(without='awesome'))
        self.assertEqual('{without}_replaced_{subdrop}.{output}.{version}.101.{suffix}',
                         s.get_name(basename='replaced', frame=101))


class TestCompound(unittest.TestCase):

    def test_empty_name(self):
        Compound = type('Compound', (PipeFile,), dict(config=dict(first=r'[\d]+', second=r'[a-zA-Z]+'),
                                                      join=dict(base=('first', 'second'))))
        c = Compound(sep='_')
        self.assertEqual('{base}.{pipe}.{suffix}', c.get_name())
        self.assertEqual('{base}.{pipe}.{suffix}', c.get_name(first=50))
        self.assertEqual('50abc.{pipe}.{suffix}', c.get_name(first=50, second='abc'))
        c.name = c.get_name(base='101dalmatians', version=1, suffix='png')
        self.assertEqual('101dalmatians', c.nice_name)
        self.assertEqual(
            {'base': '101dalmatians', 'first': '101', 'second': 'dalmatians', 'version': '1', 'suffix': 'png',
             'pipe': '.1'},
            c.values)
        self.assertEqual('200dalmatians.1.png', c.get_name(first=200))

        class CompUnused(Name):
            config = dict(first='1',
                          second='2')
            join = dict(cmp=('first', 'second'))

        class CompUsed(CompUnused):
            def get_pattern_list(self):
                return ['cmp'] + super().get_pattern_list()

        class CompAndPropsInvalid(CompUnused):
            # by compounding 'base', get_pattern_list will return an empty list, should fail to initialise
            join = dict(cmp2=('base', 'prop'))

            @property
            def prop(self):
                return 'constant'

        class CompAndPropsValid(CompAndPropsInvalid):
            def get_pattern_list(self):
                return ['cmp', 'cmp2']

        c = CompUnused()
        self.assertEqual('{base}', c.get_name())
        c.name = 'hello_world'
        self.assertEqual(None, c.cmp)
        self.assertEqual({'base': 'hello_world'}, c.values)

        c = CompUsed()
        self.assertEqual('{cmp} {base}', c.get_name())
        self.assertEqual(None, c.cmp)
        c.name = '12 hello_world'
        self.assertEqual('12', c.cmp)
        self.assertEqual({'base': 'hello_world', 'cmp': '12', 'first': '1', 'second': '2'}, c.values)

        with self.assertRaises(ValueError):
            CompAndPropsInvalid()

        c = CompAndPropsValid()
        self.assertEqual('{cmp} {cmp2}', c.get_name())
        c.name = '12 hello_worldccconstant'
        self.assertEqual('12', c.cmp)
        self.assertEqual('hello_worldccconstant', c.cmp2)
        self.assertEqual({'base': 'hello_worldcc',
                          'cmp': '12',
                          'cmp2': 'hello_worldccconstant',
                          'first': '1',
                          'prop': 'constant',
                          'second': '2'}, c.values)


class TestPropertyField(unittest.TestCase):

    def test_empty_name(self):
        class PropertyField(PipeFile):
            config = dict(extrafield='[a-z0-9]+')

            @property
            def nameprop(self):
                return 'staticvalue'

            @property
            def pathprop(self):
                return 'propertyfield'

            def get_path_pattern_list(self):
                result = super().get_pattern_list()
                result.append('pathprop')
                return result

            def get_pattern_list(self):
                result = super().get_pattern_list()
                result.append('nameprop')
                return result

        pf = PropertyField(sep='_')
        self.assertEqual(Path('{base}/{extrafield}/propertyfield/{base}_{extrafield}_staticvalue.{pipe}.{suffix}'),
                         pf.path)
        pf.name = 'simple_property_staticvalue.1.abc'
        self.assertEqual({'base': 'simple', 'extrafield': 'property', 'version': '1', 'suffix': 'abc', 'pipe': '.1',
                          'nameprop': 'staticvalue'},
                         pf.values)
        self.assertEqual('simple_property_staticvalue', pf.nice_name)
        self.assertEqual(Path('simple/property/propertyfield/simple_property_staticvalue.1.abc'), pf.path)


class TestSubclassing(unittest.TestCase):
    SubName = type('SubName', (Name,), dict(config=dict(base=r'\w+', second_field='(2nd)', third_field='(3rd)')))
    SubName2 = type('SubName2', (SubName,), dict(config=dict(second_field='(notsec)')))
    Replace = type('Replace', (SubName2,), dict(config=dict(base='(repl)', fourth_field='(4th)', fifth_field='(5th)')))
    SubName3 = type('SubName3', (SubName2,), dict(config=dict(base='(mrb)', second_field='(dos)')))
    Drop = type('Drop', (Replace,), dict(drop=('fourth_field',)))

    class Compounds(Drop):
        config = dict(subfirst='(s1st)', subscnd='(s2nd)', f1='(f1)', f2='(f2)', lastfield='(last)')
        join = dict(second_field=('subfirst', 'subscnd'), fifth_field=('f1', 'f2'))

    class Subcoms(Compounds):
        join = dict(base=('second_field', 'third_field'), fifth_field=('fifth_field', 'lastfield'))

    class Subcoms2(Compounds):
        config = dict(another='(another)', nested='(nested)')
        join = dict(base=('second_field', 'third_field'), fifth_field=('f1', 'f2', 'lastfield'))

    class Subcoms3(Subcoms2):
        config = dict(nombre='(nombre)', apellido='(apellido)', middlename='(medio)')

    class SS5(Subcoms3):
        config = dict(morename='(masnombres)')
        join = dict(nombre=('nombre', 'middlename', 'another'), apellido=('morename', 'apellido'))

    def test_sep(self):
        n = self.SubName()
        self.assertEqual('{base} {second_field} {third_field}', n.get_name())
        n.sep = 'p'
        self.assertEqual('p', n.sep)
        self.assertEqual('hellop{second_field}p{third_field}', n.get_name(base='hello'))
        self.assertEqual({}, n.values)
        newname = n.get_name(base='hello', second_field='2nd', third_field='3r')
        with self.assertRaises(ValueError):
            n.name = newname
        n.name = n.get_name(base='hello', second_field='2nd', third_field='3rd')
        self.assertEqual({'base': 'hello', 'second_field': '2nd', 'third_field': '3rd'}, n.values)
        n.sep = '?'
        self.assertEqual('hello?2nd?3rd', n.name)
        self.assertEqual('sups?2nd?3rd', n.get_name(base='sups'))
        n.sep = '?*&'
        self.assertEqual('hello?*&2nd?*&3rd', n.name)

    def test_config_only(self):
        n = self.SubName()
        self.assertEqual('{base} {second_field} {third_field}', n.get_name())
        n.name = 'word 2nd 3rd'
        self.assertEqual('2nd', n.second_field)
        with self.assertRaises(ValueError):
            n.second_field = 'notsec'
        n = self.SubName2(n.get_name(second_field='notsec'))
        self.assertEqual('word notsec 3rd', n.name)
        values = n.values
        SubNamePF = type('SubNamePF', (self.SubName, PipeFile), {})
        n = SubNamePF()
        n.sep = ' - '
        n.name = n.get_name(base='word', second_field='2nd', third_field='3rd', version=11, suffix='png')
        self.assertEqual('word - 2nd - 3rd.11.png', n.name)
        self.assertEqual('3rd', n.third_field)
        self.assertEqual('11', n.version)
        n = self.Replace()
        with self.assertRaises(ValueError):
            n.base = 'repl'
        values.update(base='repl', fourth_field='4th', fifth_field='5th')
        n.name = n.get_name(**values)
        self.assertEqual('repl notsec 3rd 4th 5th', n.name)
        with self.assertRaises(ValueError):
            self.SubName3('mrb dos 3r')
        n = self.SubName3('mrb dos 3rd')
        self.assertEqual('mrb', n.base)

    def test_drops(self):
        n = self.Drop()
        self.assertEqual('{base} {second_field} {third_field} {fifth_field}', n.get_name())
        n.name = 'repl notsec 3rd 5th'
        self.assertEqual('notsec', n.second_field)
        with self.assertRaises(ValueError):
            n.third_field = 'tres'
        n = self.Compounds()
        self.assertEqual('{base} {second_field} {third_field} {fifth_field} {lastfield}', n.get_name())
        n.name = 'repl s1sts2nd 3rd f1f2 last'
        self.assertEqual('s1st', n.subfirst)
        values = n.values
        n = self.Subcoms()
        self.assertEqual('{base} {fifth_field} {f1} {f2}', n.get_name())
        values.update(base=rf'{values["second_field"]}{values["third_field"]}',
                      fifth_field=rf'5th{values["lastfield"]}')
        n.name = n.get_name(**values)
        self.assertEqual('s1sts2nd3rd 5thlast f1 f2', n.name)
        self.assertEqual('s1sts2nd3rd', n.base)
        self.assertEqual('3rd', n.third_field)
        self.assertEqual('5thlast', n.fifth_field)
        self.assertEqual('last', n.lastfield)
        with self.assertRaises(ValueError):
            n.base = 'repls'
        n = self.Subcoms2()
        self.assertEqual('{base} {fifth_field} {another} {nested}', n.get_name())
        self.assertEqual('s1sts2nd3rd {fifth_field} {another} {nested}', n.get_name(f1='f1', f2='f2',
                                                                                    second_field=values['second_field'],
                                                                                    third_field=values['third_field']))
        n = self.SS5()
        self.assertEqual('{base} {fifth_field} {nested} {nombre} {apellido}', n.get_name())
        values['fifth_field'] = None
        # compounds that were redeclared with a nested name should have precedence
        values.update(nombre='nombremedioanother', apellido='masnombresapellido', middlename='medio',
                      morename='masnombres', another='another', nested='nested', f1='f1', f2='f2')
        n.name = n.get_name(**values)
        self.assertEqual('s1sts2nd3rd f1f2last nested nombremedioanother masnombresapellido', n.name)
        with self.assertRaises(ValueError):
            self.SubName3('mrb dos 3r')
        self.assertEqual('masnombres', n.morename)

    def test_compounds(self):
        class ComplicatedCompound(Name):
            config = dict(one='1st', two='2nd', three='3rd', four='4th', five='5th', six='6th', seven='7th',
                          eight='8th', nine='9th', zero='0')
            join = dict(two=('two', 'one', 'base'),
                             one=('seven', 'six', 'five'),
                             six=('three', 'four'),
                             base=('nine', 'eight')
                             )

        n = ComplicatedCompound('2nd7th3rd4th5th9th8th 0')
        self.assertEqual('7th3rd4th5th', n.one)
        self.assertEqual('2nd7th3rd4th5th9th8th', n.two)
        self.assertEqual('3rd', n.three)
        self.assertEqual('4th', n.four)
        self.assertEqual('5th', n.five)
        self.assertEqual('3rd4th', n.six)
        self.assertEqual('7th', n.seven)
        self.assertEqual('8th', n.eight)
        self.assertEqual('9th', n.nine)
        self.assertEqual('0', n.zero)
        self.assertEqual('9th8th', n.base)
        with self.assertRaises(ValueError):
            n.six = 'madman'

        class ComplicatedCompoundWithSep(ComplicatedCompound):
            join_sep = '-'
        n = ComplicatedCompoundWithSep('2nd-7th-3rd-4th-5th-9th-8th 0')
        self.assertEqual('7th-3rd-4th-5th', n.one)
        self.assertEqual('2nd-7th-3rd-4th-5th-9th-8th', n.two)
        self.assertEqual('3rd', n.three)
        self.assertEqual('4th', n.four)
        self.assertEqual('5th', n.five)
        self.assertEqual('3rd-4th', n.six)
        self.assertEqual('7th', n.seven)
        self.assertEqual('8th', n.eight)
        self.assertEqual('9th', n.nine)
        self.assertEqual('0', n.zero)
        self.assertEqual('9th-8th', n.base)
