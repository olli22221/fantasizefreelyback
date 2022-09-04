from converter import calculateMidiPitch
import editdistance
from GroundCompositions.groundValues import groundCompositions

testData1 = [[{'type': ['a/3'], 'duration': 'q', 'accented': 0}, {'type': ['c/4'], 'duration': 'q', 'accented': 0},
              {'type': ['d/4'], 'duration': 'q', 'accented': 0}],
             [{'type': ['f/5'], 'duration': 'q', 'accented': 0}, {'type': ['f/4'], 'duration': 'q', 'accented': 0},
              {'type': ['g/4'], 'duration': 'q', 'accented': 0}],
             [{'type': ['d/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/5'], 'duration': '8d', 'accented': 0},
              {'type': ['f/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0},
              {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['g/4'], 'duration': '8d', 'accented': 0}],
             [{'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['b/5'], 'duration': '8d', 'accented': 0},
              {'type': ['a/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0},
              {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['d/4'], 'duration': '8d', 'accented': 0}]]


def calculateCreativityScores(data,userCompositions):
    groundAndUserCompositions = userCompositions + groundCompositions
    
    pitchesVector = computePitchVector(data)
    numberOfConcepts = len(pitchesVector)
    durationVector = computeDurationVector(data)
    flex = calculateFlexibility(pitchesVector,durationVector)
    #userCompositions = getUserCompositions()
    fluency = computeFluency(data)
    orig = calculateOriginality(data,groundAndUserCompositions)

    return orig/len(groundCompositions),flex/numberOfConcepts,fluency

noteWeights = {"16":8,"8d":6,"q":4,"h":2,"w":1}

def computeFluency(data):
    cnt = 0
    for measure in data:
        for note in measure:
            cnt += noteWeights[note['duration']]
    return cnt

def computePitchVector(input):
    pitches = []

    for measure in input:
        expandedMeasure = expandMeasure(measure)
        print(len(expandedMeasure))
        tmpVector = []
        for note in expandedMeasure:

            tmpVector.append(calculateMidiPitch(note['type'][0],note['accented']))
        pitches.append(tmpVector)

    return pitches

def computeDurationVector(input):
    durations = []

    for measure in input:
        expandedMeasure = expandMeasure(measure)
        tmpVector = []
        for note in expandedMeasure:
            tmpVector.append(calculateDurationValue(note['duration']))
        durations.append(tmpVector)

    return durations


def calculateFlexibility(pitches, durations):
    result = 0

    for i in range(0,len(pitches)-1):
        for j in range(i+1, len(pitches)):

            result += calculateMeasureDiff(pitches[i],pitches[j])
            result += calculateDurationDiff(durations[i],durations[j])
    return result


midiToDuration = {"16":4,"8d":3,"q":2,"h":1,"w":0}
midiDuplication = {"16":1,"8d":2,"q":4,"h":8,"w":16}

def calculateDurationDiff(measure1, measure2):
    result = 0
    iterations = min(len(measure1), len(measure2))
    for i in range(iterations):
        result += abs(measure2[i] - measure1[i])
    return result

def calculateDurationValue(duration):
    return midiToDuration[duration]

def calculateMeasureDiff(measure1, measure2):
    result = 0
    iterations = min(len(measure1),len(measure2))
    for i in range(iterations):
        result += abs(measure2[i] - measure1[i])
    return result


def calculateDuplication(dur):
    return midiDuplication[dur]

def expandMeasure(measure):
    result = []
    for note in measure:
        i = calculateDuplication(note['duration'])
        for j in range(i):

            result.append(note)
    return result

def prepareComposition(composition):
    result = []
    for measure in composition:
        for note in measure:
            tmpStr = note['type'][0]+note['duration']+str(note['accented'])
            result.append(tmpStr)
    return result

def levensteindistance(composition1,composition2):

    comp1 = prepareComposition(composition1)
    comp2 = prepareComposition(composition2)
    return editdistance.eval(comp1,comp2)

def calculateOriginality(userComposition,ground_compositions):
    result = 0
    for ground_composition in ground_compositions:
        result += levensteindistance(userComposition,ground_composition)
    return result



def main():
    testData1 =  [[{'type': ['a/3'], 'duration': 'q', 'accented': 0}, {'type': ['c/4'], 'duration': 'q', 'accented': 0}, {'type': ['d/4'], 'duration': 'q', 'accented': 0}], [{'type': ['f/5'], 'duration': 'q', 'accented': 0}, {'type': ['f/4'], 'duration': 'q', 'accented': 0}, {'type': ['g/4'], 'duration': 'q', 'accented': 0}], [{'type': ['d/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['f/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0}, {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['g/4'], 'duration': '8d', 'accented': 0}], [{'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['b/5'], 'duration': '8d', 'accented': 0}, {'type': ['a/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0}, {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['d/4'], 'duration': '8d', 'accented': 0}]]

    testData = [[ {'type': ['b/3'], 'duration': 'q', 'accented': 0}, {'type': ['d/4'], 'duration': 'q', 'accented': 0}], [{'type': ['f/5'], 'duration': 'q', 'accented': 0}, {'type': ['f/4'], 'duration': 'q', 'accented': 0}, {'type': ['g/4'], 'duration': 'q', 'accented': 0}], [{'type': ['d/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['f/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0}, {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['g/4'], 'duration': '8d', 'accented': 0}], [{'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['b/5'], 'duration': '8d', 'accented': 0}, {'type': ['a/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0}, {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['d/4'], 'duration': '8d', 'accented': 0}]]
    #print(calculateCreativityScores(testData))
    print(calculateOriginality(testData1, groundCompositions))

if __name__ == "__main__":
    main()
