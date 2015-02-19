# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
from flask import Flask
import flask_mako as fmako  # pylint: disable=unused-import
from flask_mako import MakoTemplates

app = Flask(__name__)  # pylint: disable=invalid-name
mako = MakoTemplates(app)  # pylint: disable=invalid-name
app.template_folder = "templates"
