import os
from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.contrib.auth.models import User

# FIXME: The following, unnecessary import is necessary to resolve a circular dependency in 'export_tools'
from onadata.apps.viewer.models.data_dictionary import DataDictionary
from onadata.apps.logger.models import XForm
import onadata.libs.utils.export_tools

from pyxform.builder import create_survey_element_from_json
import pyxform.get_label_mappings
import pyxform.survey_from
import odk_to_spss_syntax


VARIABLE_LABELS_DICT, VALUE_LABELS_DICT= 'variable_labels_dict', 'value_labels_dict'


def get_spss_variable_name(variable_name):
    '''
    Convert the provided variable name into an SPSS-compatible one.
    See http://www-01.ibm.com/support/knowledgecenter/SSLVMB_22.0.0/com.ibm.spss.statistics.help/spss/base/dataedit_variable_names.htm.
    
    :param str variable_name: The variable name to be converted.
    :return: An SPSS-compatible version of the variable name.
    :rtype: str
    '''

    # Remove any slash or space characters.
    spss_variable_name= variable_name.replace('/', '')
    spss_variable_name= spss_variable_name.replace(' ', '')
    
    # Prepend a "@" character to the variable name if its first character is not legal.
    first_character= spss_variable_name[0]
    if (not first_character.isalpha()) and (first_character != '@'):
        spss_variable_name= '@' + spss_variable_name
        
    return spss_variable_name


def get_per_language_labels(question_label_mappings, option_label_mappings, label_languages, question_name_transform=None):
    per_language_labels= dict()

    for question_name, question_labels in question_label_mappings.iteritems():
        
        if question_name_transform:
            final_question_name= question_name_transform(question_name)
        else:
            final_question_name= question_name
        question_options= option_label_mappings.get(question_name, dict())

        for language in label_languages:
            if language in question_labels:
                per_language_labels.setdefault(language, dict()).setdefault(VARIABLE_LABELS_DICT, OrderedDict())[final_question_name]= question_labels[language]

#                 # DEBUG
#                 if question_name == u'A04':
#                     import ipdb
#                     ipdb.set_trace()

            for option_name, option_labels in question_options.iteritems():
                if language in option_labels:
                    per_language_labels.setdefault(language, dict()).setdefault(VALUE_LABELS_DICT, OrderedDict()).setdefault(final_question_name, OrderedDict())[option_name]= option_labels[language]

    return per_language_labels


class Command(BaseCommand):
    option_list = BaseCommand.option_list \
    + (make_option('--xlsform',
        action='store_true',
        dest='xlsform',
        help='Export labels corresponding to the provided XLSForm.'),) \
     + (make_option('--xform',
        action='store_true',
        dest='xform',
        help='Export labels corresponding to the provided XForm.'),) \
     + (make_option('--sav',
        action='store_true',
        dest='sav',
        help='Use variable names the correspond to an SPSS ".sav" file export .'),)
   
    args = "generate sav file for [user] [XForm]"
    help = "Create a SAV spss file with the form definition"

    def handle(self, *args, **options):
        if options['xlsform']:
            survey= pyxform.survey_from.xls(args[0])
        elif options['xform']:
            survey= pyxform.survey_from.xform(args[0])
        else:
            if len(args) != 2:
                raise CommandError("Command takes 2 arguments")

            try:
                user = User.objects.get(username=args[0])
            except User.DoesNotExist:
                raise CommandError("That user doesn't exist")
    
            try:
                xform = user.xforms.get(id_string=args[1])
            except XForm.DoesNotExist:
                raise CommandError("That xform does not exist")
    
            survey = create_survey_element_from_json(xform.json)

        question_label_mappings, option_label_mappings, label_languages= pyxform.get_label_mappings.get_label_mappings(survey, variable_paths=True)

        # FIXME: This works, but I get the feeling something's not quite right...
        exportable_label_mappings= dict()
        for language in label_languages:
            exportable_label_mappings[language]= {VARIABLE_LABELS_DICT: dict(), VALUE_LABELS_DICT: dict()}

        if options['sav']:
            # Recreate the actions taken in 'ExportBuilder.to_zipped_sav()' in hopes of reproducing the same variable-label mappings generated there.
            export_builder= onadata.libs.utils.export_tools.ExportBuilder()
            export_builder.set_survey(survey)
            for section in export_builder.sections:
                fields = [element['title'] for element in section['elements']]\
                    + export_builder.EXTRA_FIELDS
                c = 0
                for field in fields:
                    c += 1
                    exported_var_name = 'var%d' % c
                    original_variable_name= field

                    # FIXME: Slop...
                    question_labels= question_label_mappings.get(original_variable_name)
                    if question_labels:
                        question_options= option_label_mappings.get(original_variable_name, dict())

                        for language in label_languages:
                            if language in question_labels:
                                exportable_label_mappings[language][VARIABLE_LABELS_DICT][exported_var_name]= question_labels[language]

                            for option_name, option_labels in question_options.iteritems():
                                if language in option_labels:
                                    if exported_var_name not in exportable_label_mappings[language][VALUE_LABELS_DICT]:
                                        exportable_label_mappings[language][VALUE_LABELS_DICT][exported_var_name]= dict()

                                    exportable_label_mappings[language][VALUE_LABELS_DICT][exported_var_name][option_name]= option_labels[language]
        else:
            question_name_transform= get_spss_variable_name
            exportable_label_mappings= get_per_language_labels(question_label_mappings, option_label_mappings, label_languages, question_name_transform)

        for language in label_languages:
            variable_labels_dict= exportable_label_mappings.get(language, dict()).get(VARIABLE_LABELS_DICT)
            value_labels_dict= exportable_label_mappings.get(language, dict()).get(VALUE_LABELS_DICT)

            spss_label_syntax_string= odk_to_spss_syntax.from_dicts(variable_labels_dict, value_labels_dict)

            with open(language + '_labels.sps', 'w') as f:
                if spss_label_syntax_string.strip():
                    f.write(spss_label_syntax_string.encode('UTF-8'))
                    print 'SPSS labels syntax file written for language "{}".'.format(language.encode('UTF-8'))
