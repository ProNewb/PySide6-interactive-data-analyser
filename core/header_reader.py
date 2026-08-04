class HeaderReader:

    '''
    def read_headers(self, filename):

        with open(filename, "r") as file:

            headers = [
                line.strip()
                for line in file
                if line.strip()
            ]

        return headers
    '''
    def read_headers(self, filename):

        with open(filename, "r", encoding="utf-8") as file:

            first_line = file.readline().strip()

        return [
            header.strip()
            for header in first_line.split(",")
        ]