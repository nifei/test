__author__ = 'test'

import jinja2
import config
import unicodedata
TemplatePath = config.TemplatePath

def get_template(file):
    templateLoader = jinja2.FileSystemLoader( searchpath= TemplatePath)
    templateEnv = jinja2.Environment(loader = templateLoader, trim_blocks=True, keep_trailing_newline=True)
    template = templateEnv.get_template(file)
    return template

def render_template(template, vars):
    output = template.render(vars)
    return unicodedata.normalize("NFKD", output).encode("utf-8", "ignore")
