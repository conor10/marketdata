import xlrd


SP500_URL = 'http://us.spindices.com/idsexport/file.xls?' \
            'selectedModule=Constituents' \
            '&selectedSubModule=ConstituentsFullList' \
            '&indexId=340'

ASX200_URL = 'http://au.spindices.com/idsexport/file.xls?' \
             'selectedModule=Constituents' \
             '&selectedSubModule=ConstituentsFullList' \
             '&indexId=124611'


def parse_response(response):

    book = xlrd.open_workbook(file_contents=response.read())
    sheet = book.sheet_by_index(0)

    headers = sheet.row_values(9, start_colx=0, end_colx=2)
    if headers == [u'Constituent', u'Symbol']:
        symbols = []
        for i in range(10, sheet.nrows):
            symbol = sheet.row_values(i, start_colx=1, end_colx=2)
            if symbol[0] is not '':
                symbols.append(symbol[0])
        return symbols
    else:
        raise ProcessingException('Invalid sheet format')


class ProcessingException(Exception):
    pass