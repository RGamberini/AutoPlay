import json
import pytesseract
import sys
import imagehash
import csv
import os
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
        self.config_home = "config\\" + ScrapeLocJSON + "\\"
        self.illegal_chars = ("/", ":", "*", "?", ",", "<", ">", "|")

        ScrapeLocJSON = self.config_home + ScrapeLocJSON + ".json"

        #self.md5 = hashlib.md5()
        # Opening the file and testing for valid input
        try:
            with open(ScrapeLocJSON, "r") as infile:
                # Locations to scrape from
                self.blob = json.load(infile)

                # allItems so that later we can copy over only the items we need
                # as dictated by the scenario
                self.allItems = self.blob["items"]

                # We need to convert all the bounding boxes into a format usable by PIL
                for key, item in self.allItems.iteritems():
                    item["bbox"] = self.makeBox(*item["bbox"])

                    #Hashmap creation
                    #The hashmap exists so that we can further refine the results of Tesseract OCR image translation
                    self.createHashmap(key)
                    ### DEBUG
                    print self.allItems[key]["hashmap"]

                self.changeScenario(Scenario)
        except IOError:
            print ScrapeLocJSON + " either could not be found or is invalid!"
            raise

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
        sys.stdout.write("New scenario scraping for the following items: ")

        for i, item in enumerate(self.scenario.items):
            # Push the the needed items into itemsNeeded
            itemsNeeded[item] = None
            # We need some place to keep the value of these items
            #itemsNeeded[item]["value"] = None

            # Print out what we're scraping
            if i != 0:
                sys.stdout.write(", ")
            sys.stdout.write(item)
        print ""
        self.items = itemsNeeded

    def createHashmap(self, key):
        """
        Contains the method for checking if a hashmap already exists and if not
        create a new one
        """
        hashmap_path = self.config_home + key + ".map"
        if (os.path.isfile(hashmap_path)):
            with open(hashmap_path, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                self.allItems[key]["hashmap"] = dict((rows[0],rows[1]) for rows in reader)
        else:
            self.allItems[key]["hashmap"] = {}

    def makeBox(self,left,top,width,height):
        """
        A small function needed to convert from a tuble of left, top, width,
        and height to one with the locations of each corner
        """
    	return (left, top, left+width, top+height)

    def sanitize(self, strin):
        for illegalchar in self.illegal_chars:
            strin = strin.replace(illegalchar, '_')
        return strin

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

            #images[len(images) - 1][1].save(key + ".png")
        # Each entry in images is a tuple with the name of the item and the it's captured image
        return images

    def scrape(self):
        """
        This function converts captured images into text
        """
        item_images = self.capture()
        for entry in item_images:
            key = entry[0]
            image = entry[1]
            _type = self.allItems[key]["type"]
            #_hash = hashlib.md5(image.tobytes()).hexdigest()
            _hash = str(imagehash.dhash(image))
            _map = self.allItems[key]["hashmap"]

            #If the hash of this image does not already exist use Tesseract OCR to give us a first guess
            if _hash not in _map:
                #Run each image through tesseract OCR to get a string representation of that image
                _map[_hash] = pytesseract.image_to_string(image)
            self.items[key] = _map[_hash]

            ###DEBUG
            image.save(self.config_home + "DEBUG\\" + str(key) + " " + (self.sanitize(self.items[key]) + " " + str(_hash)).replace("\\", "") + ".png")
            ###END DEBUG


            #Stop there if the type of the item is string but otherwise we have more parsing to do
            if _type != "String":
                self.items[key] = self.scenario.parse(self.items[key], _type)
            print key + "\t" + str(self.items[key])

    def validate(self):
        return self.scenario.validate(self.items)

    #Safe exit saves our hashes
    def exit(self):
        for key, item in self.allItems.iteritems():
            if len(item["hashmap"]) > 0:
                hashmap_path = self.config_home + key + ".map"
                with open(hashmap_path, 'wb') as csvfile:
                    writer = csv.writer(csvfile)
                    for _key, value in item["hashmap"].iteritems():
                        writer.writerow([_key, value])
