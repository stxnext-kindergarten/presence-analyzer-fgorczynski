# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
from flask import Flask
import flask_mako as fmako  # pylint: disable=unused-import

app = Flask(__name__)  # pylint: disable=invalid-name
mako = fmako.MakoTemplates(app)  # pylint: disable=invalid-name
app.template_folder = "templates"
