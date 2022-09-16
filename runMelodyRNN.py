import os
import subprocess
from converter import convertCompositionToRnn, convertMidiToScore, compToMidi
import os ,json


def computeNewNotes(input, userPath, temperature):

    inputToRNN = convertCompositionToRnn(input)
    numOfGeneratedNotes = 256

    #result = subprocess.call(['source activate venv;python3.7','../magenta/magenta/models/melody_rnn/melody_rnn_generate.py','--config=attention_rnn --output_dir=rnnModel/generatedMelodies/','--numoutputs=10','--num_steps=128', '--primer_melody='+str(input),'--temperature=temperature','--bundle_file=rnnModel/attention_rnn.mag'])
    result = subprocess.check_call(["../magenta/venv/bin/python3.7", "../magenta/magenta/models/melody_rnn/melody_rnn_generate.py",'--config=attention_rnn','--output_dir='+userPath,'--num_outputs=15','--num_steps='+str(numOfGeneratedNotes), '--primer_melody='+str(inputToRNN),'--bundle_file=rnnModel/attention_rnn.mag'])
    return result


def clearUserPath(path):
    for file in os.listdir(path):
        print(path+"/"+file)
        os.remove(path+"/"+file)


def getSuggestions(path,numberOfNotes,measureNoteCount):
    suggestions = []
    for file in os.listdir(path):
         duration, notes, accent = convertMidiToScore(path+"/"+file,numberOfNotes,measureNoteCount)
         suggestions.append([duration,notes, accent])
    return suggestions


def computeLength(composition):
    cnt = 0

    for measure in composition:

        for note in measure:

            cnt = cnt + 1
    return cnt

meterToNoteCount = {0:16,2:8,1:12}
def runRnn(composition, userPath, meter, temperature):
    result = computeNewNotes(composition,userPath,temperature)

    if result == 0:
        numberOfNotes = computeLength(composition)
        measureNoteCount = meterToNoteCount[meter]
        suggestions = getSuggestions(userPath, numberOfNotes,measureNoteCount)
        print(suggestions)
        clearUserPath(userPath)

        suggestions = [x for x in suggestions if not None in x]
        suggestions = [x for x in suggestions if not len(x[0])==0]

      #  for i in len(suggestions):
       #     print(suggestions[i])
        #    if None in suggestions[i]:
         #       print(suggestions[i])
          #      suggestions.remove(arr)
           #     continue
           # else:
            #    for note in arr[1]:

#                    if note not in compToMidi:
 #                       print(note)
  #                      suggestions.remove(arr)
   #                     break
        print(suggestions)
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
