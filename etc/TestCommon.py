"""
TestCommon.py:  a testing framework for commands and scripts
                with commonly useful error handling

The TestCommon module provides a simple, high-level interface for writing
tests of executable commands and scripts, especially commands and scripts
that interact with the file system.  All methods throw exceptions and
exit on failure, with useful error messages.  This makes a number of
explicit checks unnecessary, making the test scripts themselves simpler
to write and easier to read.

The TestCommon class is a subclass of the TestCmd class.  In essence,
TestCommon is a wrapper that handles common TestCmd error conditions in
useful ways.  You can use TestCommon directly, or subclass it for your
program and add additional (or override) methods to tailor it to your
program's specific needs.  Alternatively, the TestCommon class serves
as a useful example of how to define your own TestCmd subclass.

As a subclass of TestCmd, TestCommon provides access to all of the
variables and methods from the TestCmd module.  Consequently, you can
use any variable or method documented in the TestCmd module without
having to explicitly import TestCmd.

A TestCommon environment object is created via the usual invocation:

    import TestCommon
    test = TestCommon.TestCommon()

You can use all of the TestCmd keyword arguments when instantiating a
TestCommon object; see the TestCmd documentation for details.

Here is an overview of the methods and keyword arguments that are
provided by the TestCommon class:

    test.must_exist('file1', ['file2', ...])

    test.must_match('file', "expected contents\n")

    test.must_not_exist('file1', ['file2', ...])

    test.run(options = "options to be prepended to arguments",
             stdout = "expected standard output from the program",
             stderr = "expected error output from the program",
             status = expected_status)

The TestCommon module also provides the following variables

    TestCommon.python_executable
    TestCommon.exe_suffix
    TestCommon.obj_suffix
    TestCommon.shobj_suffix
    TestCommon.lib_prefix
    TestCommon.lib_suffix
    TestCommon.dll_prefix
    TestCommon.dll_suffix

"""

# Copyright 2000, 2001, 2002, 2003, 2004 Steven Knight
# This module is free software, and you may redistribute it and/or modify
# it under the same terms as Python itself, so long as this copyright message
# and disclaimer are retained in their original form.
#
# IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
# SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
# THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
#
# THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
# AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.

__author__ = "Steven Knight <knight at baldmt dot com>"
__revision__ = "TestCommon.py 0.6.D002 2004/03/29 06:21:41 knight"
__version__ = "0.6"

import os
import os.path
import string
import sys
import types
import UserList

from TestCmd import *
from TestCmd import __all__

__all__.extend([ 'TestCommon',
                 'exe_suffix',
                 'obj_suffix',
                 'shobj_suffix',
                 'lib_prefix',
                 'lib_suffix',
                 'dll_prefix',
                 'dll_suffix',
               ])

# Variables that describe the prefixes and suffixes on this system.
if sys.platform == 'win32':
    exe_suffix   = '.exe'
    obj_suffix   = '.obj'
    shobj_suffix = '.obj'
    lib_prefix   = ''
    lib_suffix   = '.lib'
    dll_prefix   = ''
    dll_suffix   = '.dll'
elif sys.platform == 'cygwin':
    exe_suffix   = '.exe'
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = ''
    dll_suffix   = '.dll'
elif string.find(sys.platform, 'irix') != -1:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.o'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'
else:
    exe_suffix   = ''
    obj_suffix   = '.o'
    shobj_suffix = '.os'
    lib_prefix   = 'lib'
    lib_suffix   = '.a'
    dll_prefix   = 'lib'
    dll_suffix   = '.so'

def is_List(e):
    return type(e) is types.ListType \
        or isinstance(e, UserList.UserList)

class TestFailed(Exception):
    def __init__(self, args=None):
        self.args = args

class TestNoResult(Exception):
    def __init__(self, args=None):
        self.args = args

if os.name == 'posix':
    def _failed(self, status = 0):
        if self.status is None or status is None:
            return None
        if os.WIFSIGNALED(self.status):
            return None
        return _status(self) != status
    def _status(self):
        if os.WIFEXITED(self.status):
            return os.WEXITSTATUS(self.status)
        else:
            return None
elif os.name == 'nt':
    def _failed(self, status = 0):
        return not (self.status is None or status is None) and \
               self.status != status
    def _status(self):
        return self.status

class TestCommon(TestCmd):

    # Additional methods from the Perl Test::Cmd::Common module
    # that we may wish to add in the future:
    #
    #  $test->subdir('subdir', ...);
    #
    #  $test->copy('src_file', 'dst_file');
    #
    #  $test->chmod($mode, 'file', ...);
    #
    #  $test->touch('file', ...);

    def __init__(self, **kw):
        """Initialize a new TestCommon instance.  This involves just
        calling the base class initialization, and then changing directory
        to the workdir.
        """
        apply(TestCmd.__init__, [self], kw)
        os.chdir(self.workdir)

    def must_exist(self, *files):
        """Ensures that the specified file(s) must exist.  An individual
        file be specified as a list of directory names, in which case the
        pathname will be constructed by concatenating them.  Exits FAILED
        if any of the files does not exist.
        """
        files = map(lambda x: is_List(x) and os.path.join(x) or x, files)
        missing = filter(lambda x: not os.path.exists(x), files)
        if missing:
            print "Missing files: `%s'" % string.join(missing, "', `")
            self.fail_test(missing)

    def must_match(self, file, expect):
        """Matches the contents of the specified file (first argument)
        against the expected contents (second argument).  The expected
        contents are a list of lines or a string which will be split
        on newlines.
        """
        file_contents = self.read(file)
        try:
            self.fail_test(not self.match(file_contents, expect))
        except:
            print "Unexpected contents of `%s'" % file
	    print "EXPECTED contents ======"
            print expect
            print "ACTUAL contents ========"
            print file_contents
            raise

    def must_not_exist(self, *files):
        """Ensures that the specified file(s) must not exist.
        An individual file be specified as a list of directory names, in
        which case the pathname will be constructed by concatenating them.
        Exits FAILED if any of the files exists.
        """
        files = map(lambda x: is_List(x) and os.path.join(x) or x, files)
        existing = filter(os.path.exists, files)
        if existing:
            print "Unexpected files exist: `%s'" % string.join(existing, "', `")
            self.fail_test(existing)

    def run(self, options = None, arguments = None,
                  stdout = None, stderr = '', status = 0, **kw):
	"""Runs the program under test, checking that the test succeeded.

        The arguments are the same as the base TestCmd.run() method,
        with the addition of:

                options Extra options that get appended to the beginning
                        of the arguments.

		stdout	The expected standard output from
			the command.  A value of None means
			don't test standard output.

		stderr	The expected error output from
			the command.  A value of None means
			don't test error output.

                status  The expected exit status from the
                        command.  A value of None means don't
                        test exit status.

        By default, this expects a successful exit (status = 0), does
        not test standard output (stdout = None), and expects that error
        output is empty (stderr = "").
	"""
        if options:
            if arguments is None:
                arguments = options
            else:
                arguments = options + " " + arguments
        kw['arguments'] = arguments
	try:
	    apply(TestCmd.run, [self], kw)
	except:
	    print "STDOUT ============"
	    print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise
	if _failed(self, status):
            expect = ''
            if status != 0:
                expect = " (expected %s)" % str(status)
            print "%s returned %s%s" % (self.program, str(_status(self)), expect)
            print "STDOUT ============"
            print self.stdout()
	    print "STDERR ============"
	    print self.stderr()
	    raise TestFailed
	if not stdout is None and not self.match(self.stdout(), stdout):
            print "Expected STDOUT =========="
            print stdout
            print "Actual STDOUT ============"
            print self.stdout()
            stderr = self.stderr()
            if stderr:
                print "STDERR ==================="
                print stderr
            raise TestFailed
	if not stderr is None and not self.match(self.stderr(), stderr):
            print "STDOUT ==================="
            print self.stdout()
	    print "Expected STDERR =========="
	    print stderr
	    print "Actual STDERR ============"
	    print self.stderr()
	    raise TestFailed