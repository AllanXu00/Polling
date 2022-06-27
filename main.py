import argparse
import util

if __name__ == '__main__':
    # Command line arguements
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--grainularity", help="seconds between polls", default = 60)
    parser.add_argument("-t", "--total", help="number of polls", default = 2)
    parser.add_argument("-e", "--event", help="pub key of event queue", default = "AgtsKGytmt4vyU2U5ziPyQYEgHsNjizU4HWrv5sK1T24")
    args = parser.parse_args()
    grainularity = float(args.grainularity)
    total = int(args.total)
    event = args.event


    data = util.parse_json(event, grainularity, total)
    table = util.generate_table(data)
    
    print(table)

