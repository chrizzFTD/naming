# -*- coding: utf-8 -*-
"""
Names testing module.
"""
# standard
import unittest
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


class TestPipe(unittest.TestCase):

    def test_empty_name(self):
        p = Pipe()
        self.assertEqual('[base]_[pipe]', p.get_name())
        self.assertEqual('[base].10', p.get_name(version=10))
        self.assertEqual('[base]_geo.10', p.get_name(version=10, output='geo'))
        self.assertEqual('[base]_geo.10.25', p.get_name(version=10, output='geo', frame=25))
        self.assertEqual('[base]_[output].10.25', p.get_name(version=10, frame=25))
        self.assertEqual('[base]_[output].[version].101', p.get_name(frame=101))
        self.assertEqual('[base]_cache.[version]', p.get_name(output='cache'))
        self.assertEqual('[base]', p.get_name(pipe=None))

    def test_empty_name_separator(self):
        p = Pipe()
        for sep in ' ', '.', '/', '/ .':
            p.separator = sep
            self.assertEqual(f'[base]{sep}[pipe]', p.get_name())
            self.assertEqual('[base].10', p.get_name(version=10))
            self.assertEqual(f'[base]{sep}geo.10', p.get_name(version=10, output='geo'))
            self.assertEqual(f'[base]{sep}geo.10.25', p.get_name(version=10, output='geo', frame=25))
            self.assertEqual(f'[base]{sep}[output].10.25', p.get_name(version=10, frame=25))
            self.assertEqual(f'[base]{sep}[output].[version].101', p.get_name(frame=101))
            self.assertEqual(f'[base]{sep}cache.[version]', p.get_name(output='cache'))
            self.assertEqual('[base]', p.get_name(pipe=None))

    def test_init_name(self):
        p = Pipe('initname_pipeline.0')
        self.assertEqual('initname_pipeline.0', p.get_name())
        self.assertEqual('_pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        p = Pipe('initname.7')
        self.assertEqual('7', p.version)
        p = Pipe('initname_geo.0.1')
        self.assertEqual('0', p.version)
        self.assertEqual('1', p.frame)
        self.assertEqual('initname', p.nice_name)

        p = Pipe('name_with_underscores_pipeline.0')
        self.assertEqual('name_with_underscores_pipeline.0', p.get_name())
        self.assertEqual('_pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        p = Pipe('name_with_underscores.7')
        self.assertEqual('7', p.version)
        p = Pipe('name_with_underscores_geo.0.1')
        self.assertEqual('0', p.version)
        self.assertEqual('1', p.frame)
        self.assertEqual('name_with_underscores', p.nice_name)

    def test_set_name(self):
        p = Pipe()
        p.set_name('setname_pipeline.0')
        self.assertEqual('_pipeline.0', p.pipe)
        self.assertEqual('pipeline', p.output)
        self.assertEqual('0', p.version)
        p.set_name('setname_pipeline.0.5')
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


class TestPipeFile(unittest.TestCase):

    def test_empty_name(self):
        f = PipeFile()
        self.assertEqual('[base]_[pipe].[extension]', f.get_name())
        self.assertEqual('[base]_[pipe].abc', f.get_name(extension='abc'))
        self.assertEqual('[base]_[pipe].[extension]', f.get_name(extension=''))
        with self.assertRaises(AttributeError):
            f.extension
        f.set_name('myfile_data.0.ext')
        self.assertEqual('ext', f.extension)
        self.assertEqual('myfile', f.base)
        self.assertEqual('_data.0', f.pipe)
        self.assertEqual('0', f.version)
        self.assertEqual(f.get_name(), str(f.path))
