from chemdataextractor import Document
from chemdataextractor.model import Compound
from chemdataextractor.doc import Paragraph, Heading

d = Document(
    Heading(u'Synthesis of 2,4,6-trinitrotoluene (3a)'),
    Paragraph(u'The procedure was followed to yield a pale yellow solid (boiling point 240 °C)')
)

print(d.records.serialize())

from chemdataextractor.model.units import TemperatureModel, Temperature, Kelvin
from chemdataextractor.model import ListType, ModelType, StringType, Compound
from chemdataextractor.parse import I, AutoSentenceParser, join

class BoilingPoint(TemperatureModel):
    specifier = StringType(parse_expression=(I('Boiling') + I('Point')).add_action(join))
    compound = ModelType(Compound, required=True, contextual=True)
    parsers = [AutoSentenceParser()]


d = Document(
    Heading(u'Synthesis of 2,4,6-trinitrotoluene (3a)'),
    Paragraph(u'The procedure was followed to yield a pale yellow solid (boiling point 240 °C)'),
    models = [BoilingPoint]
)

print(d.records.serialize())



# Writing a New Parser

import re
from chemdataextractor.parse import R, I, W, Optional, merge

prefix = (R(u'^b\.?p\.?$', re.I) | I(u'boiling') + I(u'point')).hide()
units = (Optional(W(u'°')) + Optional(R(u'^°?[CFK]\.?$')))(u'units').add_action(merge)
value = R(u'^\d+(\.\d+)?$')(u'value')
bp = (prefix + value + units)(u'bp')



from chemdataextractor.parse.base import BaseSentenceParser
from chemdataextractor.utils import first
from lxml import etree

class BpParser(BaseSentenceParser):
    root = bp

    def interpret(self, result, start, end):
        raw_value = first(result.xpath('./value/text()'))
        raw_units = first(result.xpath('./units/text()'))
        melting_point = self.model(raw_value=raw_value,
                    raw_units=raw_units,
                    value=self.extract_value(raw_value),
                    error=self.extract_error(raw_value),
                    units=self.extract_units(raw_units, strict=True))
        cem_el = first(result.xpath('./cem'))
        if cem_el is not None:
            melting_point.compound = Compound()
            melting_point.compound.names = cem_el.xpath('./name/text()')
            melting_point.compound.labels = cem_el.xpath('./label/text()')
        yield melting_point

BoilingPoint.parsers = [BpParser()]

d = Document(
    Heading(u'Synthesis of 2,4,6-trinitrotoluene (3a)'),
    Paragraph(u'The procedure was followed to yield a pale yellow solid (boiling point 240 °C)'),
    models = [BoilingPoint]
)

print(d.records.serialize())