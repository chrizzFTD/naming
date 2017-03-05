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
        extra_fields = dict(year='[0-9]{4}', username='[a-z]+', anotherfield='(constant)', lastfield='[a-zA-Z0-9]+')
        ProjectFile = type('ProjectFile', (EasyName, PipeFile), dict(config=extra_fields))
        pf = ProjectFile('project_data_name_2017_christianl_constant_iamlast.base.17.abc')
        self.assertEqual('project_data_name_2017_christianl_constant_iamlast', pf.nice_name)
        self.assertEqual('project_data_name_2017_christianl_constant_iamlast.base.17', pf.pipe_name)
        self.assertEqual('2017', pf.year)
        self.assertEqual('iamlast', pf.lastfield)
        self.assertEqual('abc', pf.extension)


class TestEasyName(unittest.TestCase):

    def test_empty_name(self):
        n = EasyName()
        self.assertEqual('[base]', n.get_name())
        self.assertEqual({}, n.get_values())



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
