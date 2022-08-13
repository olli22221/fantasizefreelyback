from converter import calculateMidiPitch

def calculateCreativityScores(data):

    pitchesVector = computePitchVector(data)
    numberOfConcepts = len(pitchesVector)
    durationVector = computeDurationVector(data)
    flex = calculateFlexibility(pitchesVector,durationVector)
    #orig = calculateOriginality()
    return flex/numberOfConcepts

def computePitchVector(input):
    pitches = []

    for measure in input:
        expandedMeasure = expandMeasure(measure)

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

def calculateOriginality(data):
    pass

midiToDuration = {"16":4,"8d":3,"q":2,"h":1,"w":0}
midiDuplication = {"16":1,"8d":2,"q":4,"w":16}

def calculateDurationDiff(measure1, measure2):
    result = 0
    for i in range(len(measure1)):
        result += abs(measure2[i] - measure1[i])
    return result

def calculateDurationValue(duration):
    return midiToDuration[duration]

def calculateMeasureDiff(measure1, measure2):
    result = 0
    for i in range(len(measure1)):
        result += abs(measure2[i] - measure1[i])
    return result

def calculateMeasureDiff(measure1, measure2):
    result = 0
    for i in range(len(measure1)):
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



def main():
    testData = [[{'type': ['a/3'], 'duration': 'q', 'accented': 0}, {'type': ['c/4'], 'duration': 'q', 'accented': 0}, {'type': ['d/4'], 'duration': 'q', 'accented': 0}], [{'type': ['f/5'], 'duration': 'q', 'accented': 0}, {'type': ['f/4'], 'duration': 'q', 'accented': 0}, {'type': ['g/4'], 'duration': 'q', 'accented': 0}], [{'type': ['d/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['f/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0}, {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['g/4'], 'duration': '8d', 'accented': 0}], [{'type': ['e/5'], 'duration': '8d', 'accented': 0}, {'type': ['b/5'], 'duration': '8d', 'accented': 0}, {'type': ['a/5'], 'duration': '8d', 'accented': 0}, {'type': ['e/4'], 'duration': '8d', 'accented': 0}, {'type': ['f/4'], 'duration': '8d', 'accented': 0}, {'type': ['d/4'], 'duration': '8d', 'accented': 0}]]
    print(calculateCreativityScores(testData))

if __name__ == "__main__":
    main()