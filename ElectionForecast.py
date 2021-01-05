#File: ElectionForecast.py
import csv
from datetime import date
from datetime import datetime
import math
import statistics
from random import *

class State:

    def __init__(self,stateName,pollList,electoralVotes):

        #initialize instance variables

        self.stateName = stateName
        self.electoralVotes = electoralVotes
        self.pollList = []

        #add polls from list, passed as a parameter.

        for poll in pollList:
            if poll.getState() == self.stateName:
                self.pollList.append(poll)

    def getName(self): return self.stateName

    def weightPolls(self):

        #depending on distance to election, weigh polls differently
        
        electionDate = date(2020,11,4)
        self.weightedPollList = []
        
        for poll in self.pollList:
            
            pollDate = poll.getDate().split("/")
            pollDate = date(int(pollDate[2]),int(pollDate[0]),int(pollDate[1]))
            dateDiff = pollDate - electionDate
            dateDiff = dateDiff.days

            #determine poll's weight as an exponential function relating to date difference.
            #note that dateDiff is negative, and that zeroValue has a significant impact on
            #standard deviation.

            #a more rigorous model would test different zeroValues against past data.
            
            try:
                zeroValue = 5
                pollWeight = int(zeroValue*((1.1) ** dateDiff)) + 1
            except:
                print(dateDiff)
                print(pollDate)
                print(electionDate)
            for i in range(pollWeight):
                self.weightedPollList.append(poll)

    def genProbs(self,natError):

        #Determine each candidate's probability of winning a state given a national polling adjustment.
        #Again, a more rigorous model could outline this error by geographic location.

        self.allMargins = []
        for poll in self.weightedPollList:
            pollMargin = float(poll.getResult()[0]) - float(poll.getResult()[1]) #Biden - Trump
            self.allMargins.append(pollMargin)

        #use a normal distribution of polling margins to determine candidate win probabilities.

        stDev = statistics.stdev(self.allMargins)
        mean = sum(self.allMargins)/len(self.allMargins) + natError

        erf = math.erf((0 - mean)/((2 ** 0.5) * stDev))

        self.trumpProb = 0.5 * (1 + erf)
        self.bidenProb = 1 - self.trumpProb

        return [self.trumpProb,self.bidenProb]

    def getProbs(self): return [self.trumpProb,self.bidenProb]

    def simState(self):

        #simulate the state using random number generator.
        
        randNum = random()
        if randNum < self.trumpProb:
            return "Trump",self.electoralVotes
        else:
            return "Biden",self.electoralVotes

    def marginDist(self):

        #creates a rough normal distribution of polling margins. Useful in generating broader,
        #national polling probabilities.
        
        self.allMargins = []
        for poll in self.weightedPollList:
            pollMargin = float(poll.getResult()[0]) - float(poll.getResult()[1]) #Biden - Trump
            self.allMargins.append(pollMargin)
            
        stDev = statistics.stdev(self.allMargins) + 3
        mean = sum(self.allMargins)/len(self.allMargins)

        self.marginDist = []

        prevMarginProb = 0

        for margin in range(-300,301):
            marginProb = 0.5 * (1 + math.erf((margin / 10 - mean)/((2 ** 0.5) * stDev)))
            self.marginDist.append([margin / 10,prevMarginProb,marginProb]) #prob for less than margin
            prevMarginProb = marginProb

        self.marginDist.append([30.1,marginProb,1])

    def simVote(self):

        #useful for generating national popular vote forecast.

        voteVar = random()
        for marginProb in self.marginDist:
            if marginProb[1] <= voteVar < marginProb[2]:
                popVote = marginProb[0]

        expectedPopVote = sum(self.allMargins)/len(self.allMargins)

        return popVote,expectedPopVote
        

class Poll:
    def __init__(self,sampleSize,state,date,bidenPoll,trumpPoll):

        #create an object to store all relevant poll information.
        
        self.stateName = state
        self.date = date
        self.pollResult = [bidenPoll,trumpPoll]

    def getPollData(self):
        return [self.stateName,self.date,self.pollResult]

    def getState(self):
        return self.stateName

    def getDate(self):
        return self.date

    def getResult(self):
        return self.pollResult

def gatherPolls():
    wb = open("president_polls.csv","r")
    wb = wb.read().split("\n")
    pollIds = []


    pollList = []

    #find all pollIds, read each row in excel.
    
    for pollLine in wb:
        if not(pollLine.split(",")[0] in pollIds):
            pollIds.append(pollLine.split(",")[0])

    #generate list of all polls. Note that in the excel spreadsheet, each row is a candidate's result,
    #not an individual poll.

    lastIndex = 0

    for pollId in pollIds:
        trumpPoll = 0
        bidenPoll = 0
        stateName = 0
        endDate = 0
        sampleSize = 0
        
        for pollLineIndex in range(lastIndex,len(wb)):
            if wb[pollLineIndex].split(",")[0] == pollId:

                try:

                    #gather data from each row in excel.
                    
                    if wb[pollLineIndex].split(",")[3] != "":
                        stateName = wb[pollLineIndex].split(",")[3]
                    else:
                        stateName = "NATL"
                    endDate = wb[pollLineIndex].split(",")[20]
                    sampleSize = wb[pollLineIndex].split(",")[12]
                    
                    if wb[pollLineIndex].split(",")[33] == "Biden":
                        bidenPoll = wb[pollLineIndex].split(",")[37]
                    elif wb[pollLineIndex].split(",")[33] == "Trump":
                        trumpPoll = wb[pollLineIndex].split(",")[37]

                    if bidenPoll != 0 and trumpPoll != 0:
                        lastIndex = pollLineIndex
                        pollList.append(Poll(sampleSize,stateName,endDate,bidenPoll,trumpPoll))
                        break

                except:
                    break
                    break

    return pollList


def main():

    #note NE1, NE3 are simply counted with the rest of Nebraska, since all are safe red states regardless,
    #and since no polling data exists on NE1.

    stateNameList = [['District of Columbia',3],['Maine CD-1',1],['Maine CD-2',1],['Nebraska CD-2',1],['Alabama', 9], ['Alaska', 3], ['Arizona', 11], ['Arkansas', 6], ['California', 55], ['Colorado', 9], ['Connecticut', 7], ['Delaware', 3], ['Florida', 29], ['Georgia', 16], ['Hawaii', 4], ['Idaho', 4], ['Illinois', 20], ['Indiana', 11], ['Iowa', 6], ['Kansas', 6], ['Kentucky', 8], ['Louisiana', 8], ['Maine', 2], ['Maryland', 10], ['Massachusetts', 11], ['Michigan', 16], ['Minnesota', 10], ['Mississippi', 6], ['Missouri', 10], ['Montana', 3], ['Nebraska', 4], ['Nevada', 6], ['New Hampshire', 4], ['New Jersey', 14], ['New Mexico', 5], ['New York', 29], ['North Carolina', 15], ['North Dakota', 3], ['Ohio', 18], ['Oklahoma', 7], ['Oregon', 7], ['Pennsylvania', 20], ['Rhode Island', 4], ['South Carolina', 9], ['South Dakota', 3], ['Tennessee', 11], ['Texas', 38], ['Utah', 6], ['Vermont', 3], ['Virginia', 13], ['Washington', 12], ['West Virginia', 5], ['Wisconsin', 10], ['Wyoming', 3]]
    stateObjList = []
    pollList = gatherPolls()

    #treat national polls as a state to generate national error later.

    natlPolls = State("NATL",pollList,538)
    natlPolls.weightPolls()
    natlPolls.genProbs(0)
    natlPolls.marginDist()
    
    for state in stateNameList:
        stateObj = State(state[0],pollList,state[1])
        stateObj.weightPolls()
        stateObjList.append(stateObj)

    #some variables to store data from simulations.

    elecResults = []
    bidenResults = []
    trumpResults = []
    bidenWins = 0
    trumpWins = 0

    noSim = 10000

    for simRound in range(noSim):

        #generate a national polling error with which to calculate state win probabilities.

        natlRes,natlExp = natlPolls.simVote()
        natlError = natlRes - natlExp
        
        bidenElecVotes = 0
        trumpElecVotes = 0

        #simulate each state, adding to the electoral vote total.
        
        for state in stateObjList:
            
            state.genProbs(natlError)
            stateWinner,elecVotes = state.simState()
            if stateWinner == "Biden":
                bidenElecVotes += elecVotes
            elif stateWinner == "Trump":
                trumpElecVotes += elecVotes

        #track victor results.
                
        if bidenElecVotes > 270:
            elecResults.append("Biden")
            bidenWins += 1
        elif trumpElecVotes > 270:
            elecResults.append("Trump")
            trumpWins += 1
        else:
            elecResults.append("Tie")

        bidenResults.append(bidenElecVotes)
        trumpResults.append(trumpElecVotes)

    #calculate win probabilities overall, after simulations.

    bidenWinProb = (bidenWins / noSim) * 100
    trumpWinProb = (trumpWins / noSim) * 100

    bidenAvgElec = sum(bidenResults)/len(bidenResults)
    trumpAvgElec = sum(trumpResults)/len(trumpResults)

    #display basic data to shell.

    print("Biden Win Probability:",bidenWinProb)
    print("Trump Win Probability:",trumpWinProb)

    print("Biden Electoral Votes:",bidenAvgElec)
    print("Trump Electoral Votes:",trumpAvgElec)

    #print more detailed data to txt files, which can be imported to excel.

    writeFile = open("ElectoralDist.txt","w")
    ElectoralDist = ""
    for i in range(noSim):
        margin = bidenResults[i]
        ElectoralDist += str(margin) + "\n"
    writeFile.write(ElectoralDist)
    writeFile.close()

    writeFile = open("StateProbs.txt","w")
    totalText = "State Name: " + "Biden Win: " + "Trump Win: " + "\n"
    for state in stateObjList:
        bidenWin,trumpWin = state.genProbs(0)
        totalText += str(state.getName()) + " " + str(bidenWin) + " " + str(trumpWin) + "\n"

    writeFile.write(totalText)
    writeFile.close()

main()

    

            
    
