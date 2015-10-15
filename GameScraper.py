import json
import pytesseract
import sys
from PIL import ImageGrab
from PIL import ImageFilter
from PIL import Image

class GameScraper:
    def __init__(self, ScrapeLocJSON, Scenario):
        """
        Initiates a new GameScraper instance

        ScrapeLocJSON is the path to a file in config that contains a name,
        bounding box and type of each item we want to scrape from the screen.

        Scenario is the circumstances underwhich we want the bot to stop
        """

        # Opening the file and testing for valid input
        try:
            with open("config\\" + ScrapeLocJSON, "r") as infile:
                # Locations to scrape from
                self.blob = json.load(infile)

                # allItems so that later we can copy over only the items we need
                # as dictated by the scenario
                self.allItems = self.blob["items"]

                # We need to convert all the bounding boxes into a format usable by PIL
                for item in self.allItems.itervalues():
                    item["bbox"] = self.makeBox(*item["bbox"])

                self.changeScenario(Scenario)
        except IOError:
            print 'oops!'

    """
    Some configuration, may need to be tweaked in indidual scenarios however
    these defaults seem to work pretty well
    """
    scale = 2
    _filter = ImageFilter.UnsharpMask(radius=2, percent=200)

    def changeScenario(self, Scenario):
        """
        Switches the current Scenario
        Reloading the item list
        and reseting all values
        """

        # The items this scenerio checks against
        itemsNeeded = {}

        # Pull the selected scenario from the master JSON blob
        self.scenario = Scenario

        # Let the user know whats going on
        sys.stdout.write("Scraping for the following items: ")

        for i, item in enumerate(self.scenario.items):
            # Push the the needed items into itemsNeeded
            itemsNeeded[item] = None
            # We need some place to keep the value of these items
            #itemsNeeded[item]["value"] = None

            if i != 0:
                sys.stdout.write(", ")
            sys.stdout.write(item)
        print ""
        self.items = itemsNeeded

    def makeBox(self,left,top,width,height):
        """
        A small function needed to convert from a tuble of left, top, width,
        and height to one with the locations of each corner
        """
    	return (left, top, left+width, top+height)

    def capture(self):
        """
        This function captures the portions of screen dictated in the config
        and returns them

        NOTE: capture does not store the images inside the class they are directly returned

        TODO: Experiment between grabbing the whole screen and cropping VS
        capturing each indidual item preformance wise
        """
        # First we grab the whole screen only in black and white for readabillity
        image = ImageGrab.grab().convert("L")

        images = []
        for key in self.items.iterkeys():
            bbox = self.allItems[key]["bbox"]
            # Now we crop the parts of the screen we're scraping from
            images.append(
            (key, image.crop(bbox) \
            # As well as clean them up and scale
            .resize(((bbox[2] - bbox[0]) * self.scale, (bbox[3] - bbox[1]) * self.scale), Image.ANTIALIAS) \
            .filter(self._filter)))

            images[len(images) - 1][1].save(key + ".png")
        # Each entry in images is a tuple with the name of the item and the it's captured image
        return images

    def scrape(self):
        """
        This function converts captured images into text

        TODO: Implement database of image hashes
        """
        item_images = self.capture()
        for entry in item_images:
            key = entry[0]
            image = entry[1]
            _type = self.allItems[key]["type"]

            #Run each image through tesseract OCR to get a string representation of that image
            self.items[key] = pytesseract.image_to_string(image)
            #Stop there if the type of the item is string but otherwise we have more
            #parsing to do
            if _type != "String":
                self.items[key] = self.scenario.parse(self.items[key], _type)
            print key + "\t" + str(self.items[key])

    def validate(self):
        return self.scenario.validate(self.items)

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
