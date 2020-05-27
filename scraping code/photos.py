class PhotoScraper():
    def save_table(self, site,pageSource):
        from bs4 import BeautifulSoup
        import pandas as pd

        # open file
        with open(site, "r") as f:
            contents = f.read()
            f.close()        
        
        # parse
        soup = BeautifulSoup(contents, "lxml")

        # get contents
        mpList = soup.find('ul',class_ = 'list')
        mpNames = mpList.find_all('div', class_ = 'mp-sort-name')
        mpParties = mpList.find_all('div', class_ = 'party')
        mpImages = mpList.find_all('img')
        mpParliament = mpList.find_all('div', {"class": ['col-md-2 col-xs-11 mp-sort']})
        assert len(mpNames) == len(mpParties) == len(mpImages) == len(mpParliament), "Mismatch length"

        # parse contents
        mpNames = [x.string.strip() for x in mpNames]
        mpParties = [x.string.strip() for x in mpParties]
        mpImages = [x['src'] for x in mpImages]
        mpParliament = [x.string.strip() for x in mpParliament]

        # put everything in df
        results = pd.DataFrame(data = {
            'names': mpNames,
            'parties': mpParties,
            'imageLink': mpImages,
            'parliament': mpParliament,
            'page': pageSource
        })
        return(results)
        
if __name__ == '__main__':    
    import pandas as pd
    # fileNames
    path = '/Users/AAA/Parliament Analysis/data/images html'
    
    # get outputc
    final = pd.DataFrame()
    for p in ['10th','11th','12th','13th']:
        results = PhotoScraper().save_table(site = f"{path}/{p}.html", pageSource = p)
        final = pd.concat([final, results],sort = False)
    
    # save results
    final.to_excel(f"{path}/members_images.xlsx", index = False)
    
    