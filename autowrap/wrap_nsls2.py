# ######################################################################
# Copyright (c) 2014, Brookhaven Science Associates, Brookhaven        #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# Redistribution and use in source and binary forms, with or without   #
# modification, are permitted provided that the following conditions   #
# are met:                                                             #
#                                                                      #
# * Redistributions of source code must retain the above copyright     #
#   notice, this list of conditions and the following disclaimer.      #
#                                                                      #
# * Redistributions in binary form must reproduce the above copyright  #
#   notice this list of conditions and the following disclaimer in     #
#   the documentation and/or other materials provided with the         #
#   distribution.                                                      #
#                                                                      #
# * Neither the name of the Brookhaven Science Associates, Brookhaven  #
#   National Laboratory nor the names of its contributors may be used  #
#   to endorse or promote products derived from this software without  #
#   specific prior written permission.                                 #
#                                                                      #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT    #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS    #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE       #
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,           #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES   #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR   #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)   #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,  #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OTHERWISE) ARISING   #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                          #
########################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from numpydoc.docscrape import FunctionDoc, ClassDoc, NumpyDocString
import inspect
import importlib
import os
import pprint


def obj_src(py_obj, escape_docstring=True):
    """Get the source for the python object that gets passed in

    Parameters
    ----------
    py_obj : obj
        Any python object
    escape_doc_string : bool
        If true, prepend the escape character to the docstring triple quotes

    Returns
    -------
    list
        Source code lines

    Raises
    ------
    IOError
        Raised if the source code cannot be retrieved
    """
    src = inspect.getsource(py_obj)
    if escape_docstring:
        src.replace("'''", "\\'''")
        src.replace('"""', '\\"""')
    return src.split('\n')


def docstring(pyobj):
    """Get the docstring dictionary of a function

    Parameters
    ----------
    pyobj : function name or class name
        Any object in Python for which you want the docstring

    Returns
    -------
    FunctionDoc
        If pyobj is a function or class method
    ClassDoc
        If pyobj is a class

    In either case, a dictionary of the formatted numpy docstring can be
        accessed by :code:`return_val._parsed_data`
        Keys:
            'Signature': '',
            'Summary': [''],
            'Extended Summary': [],
            'Parameters': [],
            'Returns': [],
            'Raises': [],
            'Warns': [],
            'Other Parameters': [],
            'Attributes': [],
            'Methods': [],
            'See Also': [],
            'Notes': [],
            'Warnings': [],
            'References': '',
            'Examples': '',
            'index': {}
    Taken from:
        https://github.com/numpy/numpydoc/blob/master/numpydoc/docscrape.py#L94
    """
    if inspect.isfunction(pyobj) or inspect.ismethod(pyobj):
        return FunctionDoc(pyobj)
    elif inspect.isclass(pyobj):
        return ClassDoc(pyobj)
    else:
        raise ValueError("The pyobj input parameter is not a function or a "
                         "class.  A function would return 'function' from "
                         "type(pyobj) and a class would return 'type' from "
                         "type(pyobj).  Your parameter returned {0} from "
                         "type(pyobj)".format(type(pyobj)))


def do_wrap(output_path, import_list):
    for (func_name, mod_name) in import_list:
        # func_name, mod_name = imp
        print('func_name, mod_name: {0}, {1}'.format(func_name, mod_name))
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        doc = docstring(func)
        pprint.pprint(doc._parsed_data)
        src = obj_src(func)


if __name__ == "__main__":
    # perform the automagic wrapping
    output_path = os.path.expanduser('~/.vistrails/userpackages/')
    import_list = [
        ('grid3d', 'nsls2.core'),
        ('process_to_q', 'nsls2.recip'),
        ('Element', 'nsls2.fitting.base.element'),
        ('emission_line_search', 'nsls2.fitting.base.element_finder'),
        ('snip_method', 'nsls2.fitting.model.background'),
        ('gauss_peak', 'nsls2.fitting.model.physics_peak'),
        ('gauss_step', 'nsls2.fitting.model.physics_peak'),
        ('gauss_tail', 'nsls2.fitting.model.physics_peak'),
        ('elastic_peak', 'nsls2.fitting.model.physics_peak'),
        ('compton_peak', 'nsls2.fitting.model.physics_peak'),
        ('read_binary', 'nsls2.io.binary'),
        ('fit_quad_to_peak', 'nsls2.spectroscopy'),
        ('align_and_scale', 'nsls2.spectroscopy'),
        ('find_largest_peak', 'nsls2.spectroscopy'),
        ('integrate_ROI_spectrum', 'nsls2.spectroscopy'),
        ('integrate_ROI', 'nsls2.spectroscopy'),
    ]
    do_wrap(output_path, import_list)

"""
Runtime generation of classes:
https://github.com/BrookhavenNationalLaboratory/pyRafters/blob/master/pyRafters/tools/basic.py#L136

Hard coding classes:
- Jinja2 Templates
http://jinja.pocoo.org/

"""
