class Scraper():
    def save_table_details(self,
                        savePath,
                        site = 'https://www.parliament.gov.sg/parliamentary-business/votes-and-proceedings?parliament=&fromDate=&toDate=&page={}&pageSize=10',
                        ):
        """Save links, date, Parliament from table into JSON
        
        Args:
            site: (str) Link of webpage to start scraping from
            savePath: (str) Directory to save result json
        """
        import requests
        import json
        import os
        from datetime import datetime
        from bs4 import BeautifulSoup

        # init
        continueScrape = True
        page = 1
        result = {}

        # start loop
        while continueScrape:
            # request website
            r = requests.get(site.format(page))
            
            # check status
            if r.status_code == 404:
                continueScrape = False
            else:
                errorMsg = f"Error {r.status_code} getting site."
                assert r.status_code == 200, errorMsg
                
            # find table column tags
            soup = BeautifulSoup(r.content, "lxml")
            rows = soup.find_all("div", "row vp-title")
            if rows is None or rows == []:
                continueScrape = False
            else:
                for row in rows:
                    num, rowResult = self.grab_content(row)
                    result[num] = rowResult

            # change link
            print(f"Finished scraping page {page}")
            page +=1

        # save json
        fileName = f"{datetime.now().strftime('%Y-%B-%d')} table details.json"
        fileName = os.path.join(savePath, fileName)

        with open(fileName, 'w') as output:
            json.dump(result, output)
        return(result)
    
    def grab_content(self, row):
        """Parse beautifulsoup content into dict
        
        Args:
            row (NavigableString): Div which contains information
        """
        divs = row.find_all('div')
        fileLink = divs[0].a['href']
        num = divs[0].h5.string

        sittingDate = divs[1].string.strip()

        parliament = divs[2].string.strip()

        result = {
            'num': num,
            'fileLink': 'https://www.parliament.gov.sg/' + fileLink,
            'sittingDate': sittingDate,
            'parliament':parliament
        }
        return([f"{parliament}-{sittingDate}", result])

class Parser():
    def read_content(self, link):
        """Read file and parse content
        
        Args:
            link: (str) pdf/doc file location
        """
        import re
        from tika import parser

        # read file
        parsedPdf = parser.from_file(link)
        lines = parsedPdf['content'].splitlines()
        isPresent = None

        # init results
        results = {}
        index = 0

        # loop through each line to populate results
        for line in lines:
            # switch control
            if 'PRESENT' in line:
                isPresent = True
            elif 'ABSENT' in line:
                isPresent = False
            
            # end prematurely
            endTextCond = 'questions for oral answer ' in line.lower() \
                or '____' in line \
                or 'apers presented to parliament' in line.lower()
            if isPresent == False and endTextCond:
                print(f"Met end {line}")
                break

            # save results if name is detected
            regexp = re.compile(r'Mr|Ms|Dr|Prof|Miss|Madam|Mdm|Mrs|Encik')
            if regexp.search(line):
                # add result
                mp = {}
                mp['status'] = isPresent
                mp['raw'] = line.strip()
                results[index] = mp
                index += 1
        return(results)
    
    def parse_details(self, savePath, results = None, resultPath = None):
        """Parse table details

        Args:
            results: (dict) result from save_table_details
            resultPath: (str) path to retrieve json result if result is None
            savePath: (str) where to save final json output
        """
        import json
        from datetime import datetime
        import os

        # read result
        if resultPath is not None:
            with open(resultPath) as jFile:
                results = json.load(jFile)
            jFile.close()

        # loop through details
        for proceeding in results:
            data = results[proceeding]
            data['parsed'] = self.read_content(data['fileLink'])
        
        # save json
        fileName = f"{datetime.now().strftime('%Y-%B-%d')}Parsed result.json"
        fileName = os.path.join(savePath, fileName)
        with open(fileName, 'w') as output:
            json.dump(results, output)
        print("Parsed successfully")
            

if __name__ == '__main__':
    # save results
    savePath = '/Users/AAA/outputFile'
    
    # read and parse
    results = Scraper().save_table_details(savePath = savePath)
    Parser().parse_details(savePath = savePath, results = results)
