def _smallandfew(items):
    return items["Size"] == "Small" and items["Number of Enemies"] == "Few"

def _levelover7000(items):
    return items["Enemy LV"] > 7000 and items["Main Object"] == "Grass"

if __name__ == "__main__":
    from Scenario import Scenario
    import dolphininput
    import time

    smallandfew = Scenario(("Number of Enemies", "Size"), _smallandfew)
    levelover7000 = Scenario(("Enemy LV", "Main Object"), _levelover7000)

    gameScraper = GameScraper("randomdungeon.json", levelover7000)
    gameScraper.scrape()
    while not gameScraper.validate():
        dolphininput.tap(dolphininput.B, .1)
        time.sleep(.1)
    	dolphininput.tap(dolphininput.A, .1)
        gameScraper.scrape()
