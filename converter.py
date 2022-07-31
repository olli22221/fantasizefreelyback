from music21 import *
import os
from midi2audio import FluidSynth


durationDict = {"16th":"S","eighth":"E","quarter":"Q","half":"H","whole":"W"}
notesDict = {"rest":"r","A-":"Ab","B-":"Bb","C-":"Cb","D-":"Db","E-":"Eb","F-":"Fb","G-":"Gb"}
dotsDict = {0:"", 1:"."}

musicatDurationDict = {"w":"W", "h":"H", "q":"Q", "8d":"E", "16":"S"}
musicatPitchDict = {"c":"C","d":"D","e":"E","f":"F","g":"G","a":"A","b":"B"}
musicatAccent = {0:"",1:"#",2:"b"}

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


def convertCompositionToMidi():
    pass







def main():
    convertMidiToMusicat("../creativityScoring/midi_data/2022-06-05_005751_1.mid")


if __name__ == "__main__":
    main()