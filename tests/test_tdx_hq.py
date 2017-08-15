# -*- coding: utf-8 -*-
import pytest
from datetime import datetime

from tdx_hq import *


@pytest.mark.parametrize("value,expected", ((20131205, datetime(2013, 12, 5)),))
def test_int2date(value, expected):
    date = int2date(value)
    assert date == expected
