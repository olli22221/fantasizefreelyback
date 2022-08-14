import os
import subprocess
from converter import convertCompositionToRnn, convertMidiToScore, compToMidi
import os ,json


def computeNewNotes(input, userPath):

    inputToRNN = convertCompositionToRnn(input)
    numOfGeneratedNotes = 256

    #result = subprocess.call(['source activate venv;python3.7','../magenta/magenta/models/melody_rnn/melody_rnn_generate.py','--config=attention_rnn --output_dir=rnnModel/generatedMelodies/','--numoutputs=10','--num_steps=128', '--primer_melody='+str(input),'--bundle_file=rnnModel/attention_rnn.mag'])
    result = subprocess.check_call(["../magenta/venv/bin/python3.7", "../magenta/magenta/models/melody_rnn/melody_rnn_generate.py",'--config=attention_rnn','--output_dir='+userPath,'--num_outputs=10','--num_steps='+str(numOfGeneratedNotes), '--primer_melody='+str(inputToRNN),'--bundle_file=rnnModel/attention_rnn.mag'])
    return result

def clearUserPath(path):
    pass


def getSuggestions(path,numberOfNotes,measureNoteCount):
    suggestions = []
    for file in os.listdir(path):
         duration, notes, accent = convertMidiToScore(file,numberOfNotes,measureNoteCount)
         suggestions.append([duration,notes, accent])
    print(suggestions)
    return suggestions


def computeLength(composition):
    cnt = 0
    for measure in composition:
        for note in composition:
            cnt = cnt + 1
    return cnt

meterToNoteCount = {0:16,2:8,1:12}
def runRnn(composition, userPath, meter):
    result = computeNewNotes(composition,userPath)

    if result == 0:
        numberOfNotes = computeLength(composition)
        measureNoteCount = meterToNoteCount[meter]
        suggestions = getSuggestions(userPath, numberOfNotes,measureNoteCount)

        #clearUserPath(userPath)
        for arr in suggestions:

            if None in arr:

                suggestions.remove(arr)

            else:
                for note in arr[1]:

                    if note not in compToMidi:

                        suggestions.remove(arr)
                        break

        response = {}
        response['suggestions'] = suggestions
        response = json.dumps(response)
        return response

def main():
    #runRnn([60,-2,-2,-2,60,-2,67,-2,67,-2],"rnnModel/generatedMelodies/")
    #res =convertMidiToMusicat('rnnModel/generatedMelodies/2022-08-07_224822_01.mid')
    #print(res)
    pass


if __name__ == "__main__":
    main()