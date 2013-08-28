""" This document defines the excel_handler module """
import xlrd
import xlwt
from fields import Field


class FieldNotFound(Exception):
    pass


class ExcelHandlerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        fieldname_to_field = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                field = attrs.pop(k)
                field.name = k
                fieldname_to_field[k] = field

        attrs['fieldname_to_field'] = fieldname_to_field
        sup = super(ExcelHandlerMetaClass, cls)
        return sup.__new__(cls, name, bases, attrs)


class ExcelHandler():
    """ ExcelHandler is a class that is used to wrap common operations in
    excel files """

    __metaclass__ = ExcelHandlerMetaClass

    def __init__(self, path=None, excel_file=None, mode='r'):
        if path is None and excel_file is None:
            raise Exception("path or excel_file requried")
        if path is not None and excel_file is not None:
            raise Exception("Only specify path or excel_file, not both")
        if mode == 'r':
            if path:
                excel_file = open(path, mode)

            self.workbook = xlrd.open_workbook(file_contents=excel_file.read())
            self.sheet = self.workbook.sheet_by_index(0)
        else:
            self.path = path
            self.workbook = xlwt.Workbook()

        self.parser = None

    def add_sheet(self, name):
        self.sheet = self.workbook.add_sheet(name)

    def set_sheet(self, sheet_index):
        """ sets the current sheet with the given sheet_index """
        self.sheet = self.workbook.sheet_by_index(sheet_index)

    def read_rows(self, column_structure, starting_row=0, max_rows=-1):
        """ Reads the current sheet from the starting row to the last row or up
        to a max of max_rows if greater than 0

        returns an array with the data

        """
        data = []
        row = starting_row

        while max_rows != 0:
            column_data = {}

            for column_name in column_structure:
                try:
                    value = self.sheet.cell(
                        colx=column_structure[column_name],
                        rowx=row
                    ).value
                    column_data[column_name] = value
                except:
                    return data

            row += 1
            max_rows -= 1

            data.append(column_data)

        return data

    def read(self):
        """
        Using the structure defined with the Field attributes, reads the excel
        and returns the data in an array of dicts
        """
        data = []
        row = 0

        while True:
            column_data = {}
            data_read = False

            for field_name, field in self.fieldname_to_field.items():
                try:
                    value = self.sheet.cell(
                        colx=field.col,
                        rowx=row
                    ).value
                except:
                    pass
                else:
                    column_data[field.name] = field.cast(value)
                    data_read = True

            row += 1

            if not data_read:
                return data

            data.append(column_data)

        return data

    def save(self):
        """ Save document """

        self.workbook.save(self.path)

    def write_rows(self, rows):
        """ Write rows in the current sheet """

        for x, row in enumerate(rows):
            for y, value in enumerate(row):
                self.sheet.write(x, y, value)

    def write(self, data):
        for row, row_data in enumerate(data):
            for field_name, value in row_data.items():
                try:
                    field = self.fieldname_to_field[field_name]
                except KeyError:
                    raise FieldNotFound(field_name)

                self.sheet.write(row, field.col,  value)