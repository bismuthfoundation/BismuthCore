#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `bismuthcore` package."""

import pytest
import sys

sys.path.append('../')
# from bismuthcore.clientcommands import ClientCommands
from bismuthcore.bismuthconfig import BismuthConfig


def test_create():
    """Can create a config object"""
    config = BismuthConfig()
    assert config.genesis == '4edadac9093d9326ee4b17f869b14f1a2534f96f9c5d7b48dc9acaed'
