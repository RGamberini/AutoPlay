import json

def quotes(strin):
    return "\"" + strin + "\""

if __name__ == "__main__":
    conditions = {
    "EQUAL": "==",
    "NOT EQUAL":"!=",
    "LESS THAN": "<",
    "GREATER THAN": ">"
    }

    values = {
    "Size":"Small",
    "EXP":"Few"
    }
    boolstring = ""
    try:
        with open("config\\" + "randomdungeon.json", "r") as infile:
            # Locations to scrape from
            blob = json.load(infile)
            for case in blob["scenarios"]["fewandsmall"]:
                tempboolstring = "values[" + quotes(case["item"]) + "]" + conditions[case["condition"]] + quotes(case["value"])
                if case["continue"] != "END":
                    tempboolstring += " " + case["continue"].lower() + " "
                boolstring += tempboolstring
    except IOError:
        print 'oops!'

    print boolstring
    print eval(boolstring)

    # for t,expected in tests:
    #     res = boolExpr.parseString(t)[0]
    #     success = "PASS" if bool(res) == expected else "FAIL"
    #     print (t,'\n', res, '=', bool(res),'\n', success, '\n')
