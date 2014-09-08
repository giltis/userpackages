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
import time
from vistrails.core.modules.vistrails_module import (Module, ModuleSettings,
                                                     ModuleError)
from vistrails.core.modules.config import IPort, OPort


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


def docstring_class(pyobj):
    """Get the docstring dictionary of a class

    Parameters
    ----------
    pyobj : function name or class name
        Any object in Python for which you want the docstring

    Returns
    -------
    ClassDoc
        If pyobj is a class

    A dictionary of the formatted numpy docstring can be
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
    if inspect.isclass(pyobj):
        return ClassDoc(pyobj)
    else:
        raise ValueError("The pyobj input parameter is not a class."
                         "Your parameter returned {0} from "
                         "type(pyobj)".format(type(pyobj)))


def docstring_func(pyobj):
    """Get the docstring dictionary of a function

    Parameters
    ----------
    pyobj : function name
        Any object in Python for which you want the docstring

    Returns
    -------
    FunctionDoc
        If pyobj is a function or class method

    A dictionary of the formatted numpy docstring can be
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
    else:
        raise ValueError("The pyobj input parameter is not a function."
                         "Your parameter returned {0} from "
                         "type(pyobj)".format(type(pyobj)))

sig_map = {
    'basic:Variant': ['ndarray'],
    'basic:List': ['list'],
    'basic:Integer': ['int'],
    'basic:Float': ['float'],

}


def get_signature(arg_type):
    """Transform 'arg_type' into a vistrails port signature

    Parameters
    ----------
    arg_type : type
        The type of the parameter from the library function to be wrapped

    Returns
    -------
    port_sig : str
        The VisTrails port signature
    """
    for port_sig, pytypes in six.iteritems(sig_map):
        if arg_type in pytypes:
            return port_sig

    # if no arg_type matches the pytypes that relate to VisTrails port sigs
    # raise a value error
    raise ValueError("The arg_type doesn't match any of the options.  Your "
                     "arg_type is: {0}.  See the sig_type dictionary in "
                     "userpackages/autowrap/wrap_nsls2.py".format(arg_type))


def define_input_ports(docstring):
    """Turn the 'Parameters' fields into VisTrails input ports

    Parameters
    ----------
    docstring : NumpyDocString
        The scraped docstring from the

    Returns
    -------
    input_ports : list
        List of input_ports (Vistrails type IPort)
    """
    input_ports = []
    if 'Parameters' in docstring:
        for (the_name, the_type, the_description) in docstring['Parameters']:
            optional = False
            the_type = the_type.split(',')
            if len(the_type) == 1:
                the_type = the_type[0]
            elif len(the_type) == 2 and the_type[1].strip().lower() == 'optional':
                # optional = the_type[1].strip()
                # print('after stripping: [{0}]'.format(optional))
                # if the_type[1].strip().lower() is 'optional':
                optional = True
                the_type = the_type[0]
            elif len(the_type) is not 1:
                # print('the_type[1][0:1]: {0}'.format(the_type[1][0:1]))
                raise ValueError("There are two fields for the type in the"
                                 " numpy doc string, but I don't "
                                 "understand what the second variable "
                                 "is. Expected either 'type' or 'type, "
                                 "optional'. Anything else is incorrect. "
                                 "You passed in: {0}".format(the_type))

            print("the_name is {0}. \n\tthe_type is {1} and it is optional: "
                  "{3}. \n\tthe_description is {2}"
                  "".format(the_name, the_type, the_description, optional))

            input_ports.append(IPort(name=the_name, label=the_description,
                                     signature=get_signature(the_type),
                                     optional=optional))

    else:
        # raised if 'Parameters' is not in the docstring
        raise KeyError('Docstring is not formatted correctly. There is no '
                       '"Parameters" field. Your docstring: {0}'
                       ''.format(docstring))

    return input_ports


def define_output_ports(docstring):
    """Turn the 'Returns' fields into VisTrails output ports

    Parameters
    ----------
    docstring : NumpyDocString
        The scraped docstring from the

    Returns
    -------
    input_ports : list
        List of input_ports (Vistrails type IPort)
    """

    output_ports = []
    if 'Parameters' in docstring:
        for (the_name, the_type, the_description) in docstring['Returns']:
            print("the_name is {0}. \n\tthe_type is {1}. "
                  "\n\tthe_description is {2}"
                  "".format(the_name, the_type, the_description))

            output_ports.append(OPort(name=the_name,
                                      signature=get_signature(the_type)))
    else:
        # raised if 'Returns' is not in the docstring.
        # This should probably just create an empty list if there is no
        # Returns field in the docstring. Though if there is no returns field,
        # why would we be wrapping the module automatically... what to do...
        # What. To. Do.?
        raise KeyError('Docstring is not formatted correctly. There is no '
                       '"Returns" field. Your docstring: {0}'
                       ''.format(docstring))

    return output_ports


def do_wrap(output_path, import_list):
    for (func_name, mod_name) in import_list:
        t1 = time.time()
        # func_name, mod_name = imp
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        doc = docstring_func(func)
        input_ports = define_input_ports(doc._parsed_data)
        output_ports = define_output_ports(doc._parsed_data)
        pprint.pprint(input_ports)
        pprint.pprint(output_ports)
        # pprint.pprint(doc._parsed_data)
        src = obj_src(func)
        print('func_name {0}, module_name {1}. Time: {2}'
              ''.format(func_name, mod_name, format(time.time() - t1)))


if __name__ == "__main__":
    # perform the automagic wrapping
    output_path = os.path.expanduser('~/.vistrails/userpackages/')
    import_list = [
        ('grid3d', 'nsls2.core'),
        # ('process_to_q', 'nsls2.recip'),
        # ('Element', 'nsls2.constants'),
        # ('emission_line_search', 'nsls2.constants'),
        # ('snip_method', 'nsls2.fitting.model.background'),
        # ('gauss_peak', 'nsls2.fitting.model.physics_peak'),
        # ('gauss_step', 'nsls2.fitting.model.physics_peak'),
        # ('gauss_tail', 'nsls2.fitting.model.physics_peak'),
        # ('elastic_peak', 'nsls2.fitting.model.physics_peak'),
        # ('compton_peak', 'nsls2.fitting.model.physics_peak'),
        # ('read_binary', 'nsls2.io.binary'),
        # ('fit_quad_to_peak', 'nsls2.spectroscopy'),
        # ('align_and_scale', 'nsls2.spectroscopy'),
        # ('find_largest_peak', 'nsls2.spectroscopy'),
        # ('integrate_ROI_spectrum', 'nsls2.spectroscopy'),
        # ('integrate_ROI', 'nsls2.spectroscopy'),
    ]
    do_wrap(output_path, import_list)

"""
Runtime generation of classes:
https://github.com/BrookhavenNationalLaboratory/pyRafters/blob/master/pyRafters/tools/basic.py#L136

Hard coding classes:
- Jinja2 Templates
http://jinja.pocoo.org/

"""
