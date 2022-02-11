# File for creating ticket cards for Ticket to Ride:County Durham
# Copyright (2022) Robert Bettles
#
# CHANGELOG
#
# Feb 2022
# Updated script from Python 2 to Python 3

# import modules
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.text as text
import numpy as np
import math
import csv
from matplotlib import rc
rc('font',**{'family':'fantasy'})
rc('text', usetex=True)


# create blank A4 page
fig = plt.figure()
fig.set_size_inches(11.69,8.27) # size in inches
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)


# extract station positions
with open('TicketToRideCountyDurham.svg', 'r') as dataFile:
    stationList = []
    stationPosXList = []
    stationPosYList = []
    lineInd = 1
    circleInd = 1e10
    loopThroughCircleLines = 0
    for line in dataFile:
        if '<circle' in line:
            circleInd = lineInd
            loopThroughCircleLines = 1
            isThisCircleAStation = 0

        if loopThroughCircleLines == 1:
            if 'station:' in line:
                isThisCircleAStation = 1

                # find station name index in line
                stationStringInd = line.find('station:')

                # extract station name
                stationName = line[stationStringInd+8:-2]

                # replace _ with space
                stationName = stationName.replace('_',' ')

                # save station name to list
                stationList.append(stationName)

            elif 'cx="' in line:
                cxInd = line.find('cx')
                cxVal = float(line[cxInd+4:-2])
            elif 'cy="' in line:
                cyInd = line.find('cy')
                cyVal = float(line[cyInd+4:-2])

            if '/>' in line:
                loopThroughCircleLines = 0

                if isThisCircleAStation == 1:
                    stationPosXList.append(cxVal)
                    stationPosYList.append(cyVal)

        lineInd += 1
stationPosYList = 804.33073 - np.array(stationPosYList)
maxPos = np.max([np.max(stationPosXList),np.max(stationPosYList)])
stationPosXList = stationPosXList/maxPos
stationPosYList = stationPosYList/maxPos


# extract routes
with open("RouteList.csv", 'r') as ifile:
    reader = csv.reader(ifile)
    rownum = 0
    routeListStart = []
    routeListEnd = []
    routeListValue = []
    for row in reader:
        routeListStart.append(row[0])
        routeListEnd.append(row[1])
        routeListValue.append(row[2])

# check for missing stations (probably due to mislabeling on the .svg map)
if set(stationList) != set(routeListStart).union(set(routeListEnd)):
    missing_stations = set(routeListStart).union(set(routeListEnd)) - set(stationList)
    print("Warning: station list does not match stations in route list!")
    print(f"Missing stations {missing_stations}")
    print("Dropping these stations from routes")

    routeList = [
        (a, b, v) for a, b, v in zip(routeListStart, routeListEnd, routeListValue)
        if a not in missing_stations and b not in missing_stations
    ]
    routeListStart = [a for a, b, v in routeList]
    routeListEnd = [b for a, b, v in routeList]
    routeListValue = [v for a, b, v in routeList]

nRoutes = len(routeListStart)


# card size: 57mm x 88mm
# A4 page: 210mm x 297mm (big enough for 3x3 grid)
A4Dims_mm = [297.,210.]
cardDims_mm = [88.,57.]
cardDims_rel = [cardDims_mm[0]/A4Dims_mm[0],cardDims_mm[1]/A4Dims_mm[1]]
cardOuterW = cardDims_rel[0] # full card width, in relative units
cardOuterH = cardDims_rel[1] # full card height
cardInnerW = 0.9*cardOuterW # card background width
cardInnerH = 0.9*cardOuterH # card background height
axisAspectRatio = A4Dims_mm[1]/A4Dims_mm[0]

cardSpacing = 0.02

iCard = 0 # card index
iPage = 0

# loop over pages
nPages = int(math.ceil(nRoutes/9.))
for iPage in range(nPages):
    plt.cla()

    # add cards
    for ii in range(3):
        for jj in range(3):

            print(f'Card {iCard}/{len(routeListValue)}')

            if iCard < nRoutes:

                # card center positions
                xPos = 0.05 + cardOuterW/2 + (cardOuterW+cardSpacing)*ii
                yPos = 0.07 + cardOuterH/2 + (cardOuterH+cardSpacing)*jj

                # card outline
                ax.add_patch(
                    patches.Rectangle(
                        (xPos - cardOuterW/2, yPos - cardOuterH/2),   # (x,y)
                        cardOuterW,          # width
                        cardOuterH,          # height
                        facecolor = "white",
                        edgecolor = "black"
                    )
                )

                # card background
                ax.add_patch(
                    patches.Rectangle(
                        (xPos - cardInnerW/2, yPos - cardInnerH/2),   # (x,y)
                        cardInnerW,          # width
                        cardInnerH,          # height
                        facecolor = "#ffe9b7",
                        edgecolor = "#b57d00"
                    )
                )


                # card points value
                circlePosX = xPos - cardInnerW/2 + 0.03
                circlePosY = yPos - cardInnerH/2 + 0.04
                ax.add_patch(
                    patches.Ellipse(
                        (circlePosX, circlePosY),   # (x,y)
                        0.07*axisAspectRatio,          # width
                        0.07,          # height
                        facecolor = "#dbffeb",
                        edgecolor = "#009141",
                        linewidth = 3.
                    )
                )
                ax.text(circlePosX+0.001, circlePosY-0.001, str(routeListValue[iCard]), fontsize=24, \
                        horizontalalignment='center', verticalalignment='center')

                # card destinations
                ax.add_patch(
                    patches.Rectangle(
                        (xPos - cardInnerW*0.47, yPos + cardInnerH/2 - 0.04),   # (x,y)
                        cardInnerW*0.94,          # width
                        0.03,          # height
                        facecolor = "white",
                        edgecolor = "black"
                    )
                )
                ax.text(xPos, yPos + cardInnerH/2 - 0.03, \
                        "%s - %s" % (routeListStart[iCard], routeListEnd[iCard]), \
                        fontsize=10, \
                        horizontalalignment='center')

                # find station locations
                destination1Index = stationList.index(routeListStart[iCard])
                destination2Index = stationList.index(routeListEnd[iCard])

                # draw stations
                for iStation in range(len(stationPosXList)):
                    stationPosX = xPos - cardInnerW/2 + 0.015 + stationPosXList[iStation]*cardInnerW*0.86
                    stationPosY = yPos - cardInnerH/2 + 0.033 + stationPosYList[iStation]*cardInnerH*0.9
                    ax.add_patch(
                        patches.Ellipse(
                            (stationPosX, stationPosY),
                            0.007*axisAspectRatio,          # width
                            0.007,          # height
                            facecolor = "#d8ecf6",
                            edgecolor = "#1f6587",
                            linewidth = 2.
                        )
                    )

                    # highlight destination stations
                    if iStation == destination1Index or iStation == destination2Index:
                        ax.add_patch(
                            patches.Ellipse(
                                (stationPosX, stationPosY),
                                0.015*axisAspectRatio,          # width
                                0.015,          # height
                                facecolor = "red",
                                edgecolor = "black",
                                linewidth = 2.
                            )
                        )

            iCard += 1

    # save tickets to file
    fig.savefig('Tickets_%d.pdf' % (iPage+1))

    plt.draw()
    # plt.pause(1) # <-------
    # raw_input("<Hit Enter To Continue>")

plt.close(fig)
