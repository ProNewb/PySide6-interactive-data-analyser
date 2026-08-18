class HeaderReader:

    '''
    Class to strip headers from a file
    '''
    def read_headers(self, filename):

        with open(filename, "r", encoding="utf-8") as file:

            first_line = file.readline().strip()

        return [
            header.strip()
            for header in first_line.split(",")
        ]