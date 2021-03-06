# -*- coding: utf-8 -*-

from aiida.orm.implementation.calculation import Calculation

__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file."
__authors__ = "The AiiDA team."
__version__ = "0.7.1"


class WorkCalculation(Calculation):
    """
    Used to represent a calculation generated by a Process from the new
    workflows system.
    """
    pass
