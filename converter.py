from music21 import *
import os
from midi2audio import FluidSynth


durationDict = {"16th":"S","eighth":"E","quarter":"Q","half":"H","whole":"W"}
notesDict = {"rest":"r","A-":"Ab","B-":"Bb","C-":"Cb","D-":"Db","E-":"Eb","F-":"Fb","G-":"Gb"}
dotsDict = {0:"", 1:"."}

musicatDurationDict = {"w":"W", "h":"H", "q":"Q", "8d":"E", "16":"S"}
musicatPitchDict = {"c":"C","d":"D","e":"E","f":"F","g":"G","a":"A","b":"B"}
musicatAccent = {0:"",1:"#",2:"b"}
midiSharps = ["A#","B#","C#","D#","E#","F#","G#"]
midiB = ["A-","B-","C-","D-","E-","F-","G-"]
midiToComposition = {"A":"a","B":"b","C":"c","D":"d","E":"e","F":"f","G":"g","rest":"r"}
midiToDuration = {"16th":"16","eighth":"8d","quarter":"q","half":"h","whole":"w"}

compToMidi = {"g/3":55,"a/3":57,"b/3":59,"c/4":60,"d/4":62,"e/4":64,"f/4":65,"g/4":67,"a/4":69,"b/4":71,"c/5":72
              ,"d/5":74,"e/5":76,"f/5":77,"g/5":79,"a/5":81,"b/5":83,"c/6":84}


def calculateMidiPitch(note, accented):
    if accented == 1:
        return compToMidi[note]+1

    if accented == -1:
        return compToMidi[note]-1

    if accented == 0:
        return compToMidi[note]


def convertToMusicat(composition):
    measureCount = 0
    musicatString = ""
    for arr in composition:
        measureCount+=1
        for elem in arr:
            duration = elem['duration']
            musicatString += musicatDurationDict[duration]
            pitchType = elem['type']
            pitch = pitchType[0]
            musicatPitch = musicatPitchDict[pitch[0]]
            octave = pitch[2]
            accent = elem['accented']
            accent_ = musicatAccent[accent]
            musicatString += musicatPitch
            musicatString += accent_
            musicatString += octave
            musicatString += " "
        if measureCount < len(composition):
            musicatString += " | "

    print(musicatString)
    return musicatString

restDuration = {"16":"16r","8d":"8r","q":"qr","h":"hr","w":"wr"}
def convertMidiToScore(file, numberOfMeasures):
    mf = midi.MidiFile()
    mf.open("rnnModel/generatedMelodies/"+file)
    mf.read()

    s = midi.translate.midiFileToStream(mf)

    mf.close()
    resultNotes = []
    resultDuration = []
    resultAccent = []
    noteToAdd = ""
    for thisnote in s.recurse().notesAndRests:
        if thisnote.duration.type == 'complex':
            return None, None, None
        m21noteDuration = midiToDuration[thisnote.duration.type]
        m21noteName = thisnote.name


        if thisnote.measureNumber < numberOfMeasures+1:
            continue
        else:
            if m21noteName == "rest":

                dur = restDuration[m21noteDuration]
                resultDuration.append(dur)
                resultNotes.append("b/4")
                resultAccent.append(0)
                continue
            m21noteOctave = thisnote.octave
            if m21noteName in midiSharps:
                noteToAdd += midiToComposition[m21noteName[0]]
                noteToAdd += "/"
                resultAccent.append(1)
            elif m21noteName in midiB:
                noteToAdd += midiToComposition[m21noteName[0]]
                noteToAdd += "/"
                resultAccent.append(-1)
            else:
                noteToAdd += midiToComposition[m21noteName]
                noteToAdd += "/"
                resultAccent.append(0)

            noteToAdd += str(m21noteOctave)
            resultNotes.append(noteToAdd)
            noteToAdd = ""
            resultDuration.append(m21noteDuration)
    return  resultDuration, resultNotes,resultAccent






def convertMidiToMusicat(pathToMidi):

    musicatStringFormat = ""
    mf = midi.MidiFile()
    print(os.getcwd())
    mf.open(pathToMidi)
    mf.read()

    s = midi.translate.midiFileToStream(mf)

    mf.close()
    measureNumber=1
    for thisnote in s.recurse().notesAndRests:
        #print(thisnote.measureNumber)
        #if thisnote.tie is not None:

        #print(thisnote.tie)
        #print(thisnote.name)
        #print(thisnote.duration.type)
        #print(thisnote.duration.dots)
        #print(thisnote.octave)
        if thisnote.measureNumber > measureNumber:
            musicatStringFormat+= "| "
            measureNumber+=1
        if thisnote.duration.type != "complex":
            musicatStringFormat += durationDict[thisnote.duration.type] + dotsDict[thisnote.duration.dots]
            if thisnote.name in notesDict:
                musicatStringFormat +=  notesDict[thisnote.name]
            else:
                musicatStringFormat += thisnote.name
            if thisnote.name != "rest":
                musicatStringFormat += str(thisnote.octave)
            if thisnote.tie is not None:
                musicatStringFormat += "_"
        else:
            components = thisnote.duration.components
            count = 0
            for component in components:
                musicatStringFormat += durationDict[component.type] + dotsDict[component.dots]
                if thisnote.name in notesDict:
                    musicatStringFormat += notesDict[thisnote.name]
                else:
                    musicatStringFormat += thisnote.name
                musicatStringFormat += str(thisnote.octave)
                if count == 0:
                    musicatStringFormat += "_"
                    count+=1
        musicatStringFormat += " "
    return musicatStringFormat



def convertMidiToWav(pathToMidi,outputPath):

    FluidSynth().midi_to_audio(pathToMidi,outputPath)


durationToNoteOff = {"w":[-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2],"h":[-2,-2,-2,-2,-2,-2,-2],"q":[-2,-2,-2],"8d":[-2],"16":[]}
def calculateDurationSymbols(duration):

    return durationToNoteOff[duration]


def convertCompositionToRnn(composition):

    rnnArray = []
    for arr in composition:

        for elem in arr:
            duration = elem['duration']
            accent = elem['accented']
            pitchType = elem['type']

            midiPitch = calculateMidiPitch(pitchType[0],accent)
            noteOffEvents = calculateDurationSymbols(duration)

            rnnArray.append(midiPitch)
            for i in noteOffEvents:
                rnnArray.append(i)
    return rnnArray









def main():
    convertMidiToMusicat("../creativityScoring/midi_data/2022-06-05_005751_1.mid")


if __name__ == "__main__":
    main()