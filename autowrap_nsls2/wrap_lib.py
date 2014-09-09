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
import sys
from vistrails.core.modules.vistrails_module import (Module,
                                                     ModuleSettings,
                                                     ModuleError)
from vistrails.core.modules.config import IPort, OPort
import numpy as np
from collections import namedtuple
import logging
logger = logging.getLogger(__name__)


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
    return src
    # return src.split('\n')


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


sig_map = [
    ('basic:Variant', ['ndarray', 'array']),
    ('basic:List', ['list']),
    ('basic:Integer', ['int', 'integer']),
    ('basic:Float', ['float']),
    ('basic:Tuple', ['tuple']),
    ('basic:Dict', ['dict']),
    ('basic:Bool', ['bool']),
    ('basic:String', ['str', 'string'])
]


enum_map = [
    ('numpy.dtype', [np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                     np.uint8, np.uint16, np.uint64, np.float16, np.float32,
                     np.float64, np.complex64, np.complex128]),
]


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
    for port_sig, pytypes in sig_map:
        if arg_type in pytypes:
            return port_sig

    # if no arg_type matches the pytypes that relate to VisTrails port sigs
    # raise a value error
    raise ValueError("The arg_type doesn't match any of the options.  Your "
                     "arg_type is: {0}.  See the sig_type dictionary in "
                     "userpackages/autowrap/wrap_lib.py".format(arg_type))


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
                the_type = the_type[0].lower()
            elif (len(the_type) == 2 and
                  the_type[1].strip().lower() == 'optional'):
                # optional = the_type[1].strip()
                # logger.debug('after stripping: [{0}]'.format(optional))
                # if the_type[1].strip().lower() is 'optional':
                optional = True
                the_type = the_type[0]
            elif len(the_type) is not 1:
                # logger.debug('the_type[1][0:1]: {0}'.format(the_type[1][0:1]))
                raise ValueError("There are two fields for the type in the"
                                 " numpy doc string, but I don't "
                                 "understand what the second variable "
                                 "is. Expected either 'type' or 'type, "
                                 "optional'. Anything else is incorrect. "
                                 "You passed in: {0}".format(the_type))

            logger.debug("the_name is {0}. \n\tthe_type is {1} and it is "
                         "optional: {3}. \n\tthe_description is {2}"
                         "".format(the_name, the_type, the_description,
                                   optional))
            input_ports.append(IPort(name=the_name, label=the_description,
                                     signature=get_signature(the_type),
                                     optional=optional))
    else:
        # raised if 'Parameters' is not in the docstring
        raise KeyError('Docstring is not formatted correctly. There is no '
                       '"Parameters" field. Your docstring: {0}'
                       ''.format(docstring))

    logger.debug('dir of input_ports[0]: {0}'.format(dir(input_ports[0])))

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
            logger.debug("the_name is {0}. \n\tthe_type is {1}. "
                         "\n\tthe_description is {2}"
                         "".format(the_name, the_type, the_description))
            try:
                signature = get_signature(the_type)
            except ValueError as ve:
                logger.error('ValueError raised for Returns parameter with '
                             'name: {0}\n\ttype: {1}\n\tdescription: {2}'
                             ''.format(the_name, the_type, the_description))
                raise ValueError(ve)

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


def gen_module(input_ports, output_ports, docstring,
               module_name, library_func, module_namespace,
               dict_port=None):

    mandatory = []
    optional = []

    # create the lists of mandatory and optional input ports
    for port in input_ports:
        if port == dict_port:
            # since dict port must be in the input_ports list but we dont want
            # to treat it as a normal input port, do not assign it as
            # optional or mandatory
            continue
        if port.optional:
            optional.append(port.name)
        else:
            mandatory.append(port.name)

    def compute(self):
        params_dict = {}
        if dict_port is not None:
            params_dict = self.get_input(dict_port.name)

        for opt in optional:
            if self.has_input(opt):
                params_dict[opt] = self.get_input(opt)

        for mand in mandatory:
            try:
                params_dict[mand] = self.get_input(mand)
            except ModuleError as me:
                if mand in params_dict:
                    # pass on this exception, as the dictionary on dict_port
                    # has taken care of this key
                    pass
                else:
                    logger.debug('The mandatory port {0} does not have input'
                                 'and the input dictionary is either not '
                                 'present or doesn\'t contain this key'
                                 ''.format(mand))
                    raise ModuleError(me)

        ret = library_func(**params_dict)

        for (out_port, ret_val) in zip(output_ports, ret):
            self.set_output(out_port.name, ret_val)

    _settings = ModuleSettings(namespace=module_namespace)

    new_class = type(str(module_name),
                     (Module,), {'compute': compute,
                                 '__module__': __name__,
                                 '_settings': _settings,
                                 '__doc__': docstring,
                                 '__name__': module_name,
                                 '_input_ports': input_ports,
                                 '_output_ports': output_ports})
    return new_class


def do_wrap(func_name, module_path, add_input_dict=False, namespace=None):
    """Perform the wrapping of functions into VisTrails modules

    Parameters
    ----------
    func_name : str
        Name of the function to wrap into VisTrails. Example 'grid3d'
    module_path : str
        Name of the module which contains the function. Example: 'nsls2.core'
    add_input_dict : bool, optional
        Flag that instructs the wrapping machinery to add a dictionary input
        port to the resultant VisTrails module. This dictionary port is
        solely a convenience function whose main purpose is to unpack the
        dictionary into the wrapped function
    namespace : str
        Path to the function in VisTrails.  This should be a string separated
        by vertical bars: |.  Example: 'vis|test' will put the new VisTrail
        module at the end of expandable lists vis -> test -> func_name
    """
    if namespace is None:
        namespace = '|'.join(module_path.split('.')[1:])
        if not namespace:
            namespace = module_path

    logger.debug('func_name {0} has import path {1} and should be placed in'
                 ' namespace {3}. It should include an '
                 'input dictionary as a port ({2})'
                 ''.format(func_name, module_path, add_input_dict, namespace))
    t1 = time.time()
    # func_name, mod_name = imp
    mod = importlib.import_module(module_path)
    func = getattr(mod, func_name)

    try:
        # get the source of the function
        src = obj_src(func)
    except IOError as ioe:
        # raised if the source cannot be found
        logger.debug("IOError raised when attempting to get the source"
                     "for function {0}".format(func))
        raise IOError(ioe)
    try:
        # get the docstring of the function
        doc = docstring_func(func)
    except ValueError as ve:
        logger.debug("ValueError raised when attempting to get docstring "
                     "for function {0}".format(func))
        raise ValueError(ve)
    try:
        # create the VisTrails input ports
        input_ports = define_input_ports(doc._parsed_data)
    except ValueError as ve:
        logger.error('ValueError raised in attempt to format input_ports'
                     ' in function: {0} in module: {1}'
                     ''.format(func_name, module_path))
        raise ValueError(ve)
    try:
        # create the VisTrails output ports
        output_ports = define_output_ports(doc._parsed_data)
    except ValueError as ve:
        logger.error('ValueError raised in attempt to format output_ports'
                     ' in function: {0} in module: {1}'
                     ''.format(func_name, module_path))
        raise ValueError(ve)
    if add_input_dict:
        # define a dictionary input port if necessary
        dict_port = IPort(name='input_dict', signature=('basic:Dictionary'),
                          label='Dictionary of input parameters.'
                                'Convienence port')
        input_ports.append(dict_port)
    else:
        dict_port = None

    # actually create the VisTrail module
    gen_module(input_ports=input_ports, output_ports=output_ports,
               docstring=src, module_name=func_name,
               module_namespace=namespace, library_func=func,
               dict_port=dict_port)

    logger.info('func_name {0}, module_name {1}. Time: {2}'
                 ''.format(func_name, module_path, format(time.time() - t1)))
    return mod


def run():
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    # perform the automagic wrapping
    import_list_funcs = [
        {'func_name': 'grid3d',
         'module_path': 'nsls2.core',
         'add_input_dict': True,
         'namespace': 'core'},
        {'func_name': 'process_to_q',
         'module_path': 'nsls2.recip',
         'add_input_dict': True,
         'namespace': 'recip'},
        # {'func_name': 'bin_1D',
        #  'module_path': 'nsls2.core',
        #  'namespace': 'core'},
        # {'func_name': 'emission_line_search',
        #  'module_path': 'nsls2.constants',
        #  'add_input_dict': True,
        #  'namespace': 'core'},
        # {'func_name': 'snip_method',
        #  'module_path': 'nsls2.fitting.model.background',
        #  'add_input_dict': True,
        #  'namespace': 'core'},
        # {'func_name': 'gauss_peak',
        #  'module_path': 'nsls2.fitting.model.physics_peak',
        #  'add_input_dict': True,
        #  'namespace': 'core'},
        # {'func_name': 'gauss_step',
        #  'module_path': 'nsls2.fitting.model.physics_peak'},
        # {'func_name': 'gauss_tail',
        #  'module_path': 'nsls2.fitting.model.physics_peak'},
        # {'func_name': 'elastic_peak',
        #  'module_path': 'nsls2.fitting.model.physics_peak'},
        # {'func_name': 'compton_peak',
        #  'module_path': 'nsls2.fitting.model.physics_peak'},
        # {'func_name': 'read_binary',
        #  'module_path': 'nsls2.io.binary'},
        # {'func_name': 'fit_quad_to_peak',
        #  'module_path': 'nsls2.spectroscopy'},
        # {'func_name': 'align_and_scale',
        #  'module_path': 'nsls2.spectroscopy'},
        # {'func_name': 'find_largest_peak',
        #  'module_path': 'nsls2.spectroscopy'},
        # {'func_name': 'integrate_ROI_spectrum',
        #  'module_path': 'nsls2.spectroscopy'},
        # {'func_name': 'integrate_ROI',
        #  'module_path': 'nsls2.spectroscopy'},
    ]
    vt_mod_lst = []
    for func in import_list_funcs:
        vt_mod_lst.append(do_wrap(**func))
    return vt_mod_lst


if __name__ == "__main__":
    run()
    # import_list_classes = [
    #     ('Element', 'nsls2.constants')
    # ]

"""
Runtime generation of classes:
https://github.com/BrookhavenNationalLaboratory/pyRafters/blob/master/pyRafters/tools/basic.py#L136

Hard coding classes:
- Jinja2 Templates
http://jinja.pocoo.org/

"""
