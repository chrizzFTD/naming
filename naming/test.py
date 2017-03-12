# -*- coding: utf-8 -*-
"""
Names testing module.
"""
# standard
import os
import unittest
from pathlib import Path
# package
from naming import *


class TestName(unittest.TestCase):

    def test_empty_name(self):
        n = Name()
        self.assertEqual('[base]', n.get_name())

    def test_init_name(self):
        n = Name('initname')
        self.assertEqual('initname', n.get_name())
        with self.assertRaises(NameError):
            Name(dict(my_name='dict'))
        n = Name(dict())
        self.assertFalse(None, n.get_name())

    def test_set_name(self):
        n = Name()
        n.set_name('setname')
        self.assertEqual('setname', n.get_name())


class TestEasyName(unittest.TestCase):

    def test_empty_name(self):
        n = Name()
        self.assertEqual('[base]', n.get_name())
        self.assertEqual({}, n.get_values())

    def test_new_empty_name(self):
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        Project = type('Project', (Name,), dict(config=extra_fields))
        p = Project()
        self.assertEqual('[base]_[year]_[username]_[anotherfield]_[lastfield]', p.get_name())
        p.set_name('this_is_my_base_name_2017_christianl_constant_iamlast')
        self.assertEqual('2017', p.year)

    def test_set_name(self):
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        ProjectFile = type('ProjectFile', (PipeFile,), dict(config=extra_fields))
        pf = ProjectFile('this_is_my_base_name_2017_christianl_constant_iamlast.base.17.abc')
        self.assertEqual('this_is_my_base_name_2017_christianl_constant_iamlast', pf.nice_name)
        self.assertEqual('this_is_my_base_name_2017_christianl_constant_iamlast.base.17', pf.pipe_name)
        self.assertEqual('2017', pf.year)
        self.assertEqual('iamlast', pf.lastfield)
        self.assertEqual('abc', pf.extension)

    def test_separator(self):
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        Project = type('Project', (Name,), dict(config=extra_fields))
        p = Project('this_is_my_base_name_2017_christianl_constant_iamlast')
        self.assertEqual('_', p.separator)
        p.separator = '  '
        self.assertEqual('this_is_my_base_name  2017  christianl  constant  iamlast', p.name)

class TestPipe(unittest.TestCase):

    def test_empty_name(self):
        p = Pipe()
        self.assertEqual('[base].[pipe]', p.get_name())
        self.assertEqual('[base].10', p.get_name(version=10))
        self.assertEqual('[base].geo.10', p.get_name(version=10, output='geo'))
        self.assertEqual('[base].geo.10.25', p.get_name(version=10, output='geo', frame=25))
        self.assertEqual('[base].[output].10.25', p.get_name(version=10, frame=25))
        self.assertEqual('[base].[output].[version].101', p.get_name(frame=101))
        self.assertEqual('[base].cache.[version]', p.get_name(output='cache'))
        self.assertEqual('[base]', p.get_name(pipe=None))

    def test_empty_name_separator(self):
        p = Pipe()
        for sep in ' ', '.', '/', '/ .':
            p.separator = sep
            self.assertEqual(f'[base].[pipe]', p.get_name())
            self.assertEqual('[base].10', p.get_name(version=10))
            self.assertEqual(f'[base].geo.10', p.get_name(version=10, output='geo'))
            self.assertEqual(f'[base].geo.10.25', p.get_name(version=10, output='geo', frame=25))
            self.assertEqual(f'[base].[output].10.25', p.get_name(version=10, frame=25))
            self.assertEqual(f'[base].[output].[version].101', p.get_name(frame=101))
            self.assertEqual(f'[base].cache.[version]', p.get_name(output='cache'))
            self.assertEqual('[base]', p.get_name(pipe=None))

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
        p.set_name('setname.pipeline.0')
        self.assertEqual('.pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        self.assertEqual('0', p.version)
        p.set_name('setname.pipeline.0.5')
        self.assertEqual('5', p.frame)
        self.assertEqual('setname', p.nice_name)

    def test_values(self):
        p = Pipe()
        p.set_name('my_pipe_file.1')
        self.assertEqual({'base': 'my_pipe_file', 'version': '1'}, p.get_values())

    def test_get_empty_name(self):
        p = Pipe()
        self.assertEqual('[base].[pipe]', p.pipe_name)
        self.assertEqual('[base].[pipe]', p.get_name())
        self.assertEqual('[base].out.7', p.get_name(pipe='.out.7'))
        self.assertEqual('[base].out.[version]', p.get_name(output='out'))
        self.assertEqual('[base].7', p.get_name(version=7))
        self.assertEqual('[base].[output].[version].101', p.get_name(frame=101))

    def test_get_init_name(self):
        p = Pipe('my_pipe_file.7')
        self.assertEqual('my_pipe_file.[output].7.101', p.get_name(frame=101))
        self.assertEqual('my_pipe_file.cache.7', p.get_name(output='cache'))
        self.assertEqual('my_pipe_file.8', p.get_name(version=int(p.version) + 1))


class TestFile(unittest.TestCase):

    def test_empty_name(self):
        f = File()
        self.assertEqual('[base].[extension]', f.get_name())
        self.assertEqual('[base].abc', f.get_name(extension='abc'))
        self.assertEqual('[base].[extension]', f.get_name(extension=''))
        with self.assertRaises(AttributeError):
            f.extension
        f.set_name('myfile.ext')
        self.assertEqual('ext', f.extension)
        self.assertEqual('myfile', f.base)
        self.assertEqual(f.get_name(), str(f.path))
        self.assertEqual(os.path.join(Path.home(), f.get_name()), str(f.full_path))


class TestPipeFile(unittest.TestCase):

    def test_empty_name(self):
        f = PipeFile()
        self.assertEqual('[base].[pipe].[extension]', f.get_name())
        self.assertEqual('[base].[pipe].abc', f.get_name(extension='abc'))
        self.assertEqual('[base].[pipe].[extension]', f.get_name(extension=''))
        with self.assertRaises(AttributeError):
            f.extension
        f.set_name('myfile.data.0.ext')
        self.assertEqual('ext', f.extension)
        self.assertEqual('myfile', f.base)
        self.assertEqual('.data.0', f.pipe)
        self.assertEqual('0', f.version)
        self.assertEqual(f.get_name(), str(f.path))


class TestDrops(unittest.TestCase):

    def test_empty_name(self):
        Dropper = type('Dropper', (PipeFile,), dict(config=dict(without=r'[a-zA-Z0-9]+', basename=r'[a-zA-Z0-9]+'),
                                                    drops=('base',)))
        d = Dropper()
        self.assertEqual('[without]_[basename].[pipe].[extension]', d.get_name())
        self.assertEqual('awesome_[basename].[pipe].[extension]', d.get_name(without='awesome'))
        self.assertEqual('[without]_replaced.[output].[version].101.[extension]',
                         d.get_name(basename='replaced', frame=101))

        Subdropper = type('Dropper', (Dropper,), dict(config=dict(subdrop='[\w]')))
        s = Subdropper()
        self.assertEqual('[without]_[basename]_[subdrop].[pipe].[extension]', s.get_name())
        self.assertEqual('awesome_[basename]_[subdrop].[pipe].[extension]', s.get_name(without='awesome'))
        self.assertEqual('[without]_replaced_[subdrop].[output].[version].101.[extension]',
                         s.get_name(basename='replaced', frame=101))


class TestCompound(unittest.TestCase):

    def test_empty_name(self):
        Compound = type('Compound', (PipeFile,), dict(config=dict(first=r'[\d]+', second=r'[a-zA-Z]+'),
                                                      compounds=dict(base=('first', 'second'))))
        c = Compound()
        self.assertEqual('[base].[pipe].[extension]', c.get_name())
        self.assertEqual('[base].[pipe].[extension]', c.get_name(first=50))
        self.assertEqual('50abc.[pipe].[extension]', c.get_name(first=50, second='abc'))
        c.set_name(c.get_name(base='101dalmatians', version=1, extension='png'))
        self.assertEqual('101dalmatians', c.nice_name)
        self.assertEqual(
            {'base': '101dalmatians', 'first': '101', 'second': 'dalmatians', 'version': '1', 'extension': 'png'},
            c.get_values())
        self.assertEqual('200dalmatians.1.png', c.get_name(first=200))


class TestPropertyField(unittest.TestCase):

    def test_empty_name(self):
        class PropertyField(PipeFile):
            config = dict(extrafield='[a-z0-9]+')

            @property
            def prop(self):
                return 'propertyfield'

            def _get_path_pattern_list(self):
                result = super()._get_pattern_list()
                result.append('prop')
                return result

        pf = PropertyField()
        self.assertEqual(Path('[base]/[extrafield]/[prop]/[base]_[extrafield].[pipe].[extension]'), pf.path)
        pf.set_name(pf.get_name(base='simple', extrafield='property', version=1, extension='abc'))
        self.assertEqual({'base': 'simple', 'extrafield': 'property', 'version': '1', 'extension': 'abc'},
                         pf.get_values())
        self.assertEqual('simple_property', pf.nice_name)
        self.assertEqual(Path('simple/property/propertyfield/simple_property.1.abc'), pf.path)
