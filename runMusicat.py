import subprocess
from converter import convertMidiToMusicat, convertToMusicat
import os ,json
import time

def run(pathToMusicat, input, pathToImageDir):
    print(input)
    inputToMusicat = convertToMusicat(input)
    now = time.time()
    result = subprocess.run([pathToMusicat,"noGUI", "input="+inputToMusicat, "png="+pathToImageDir+"out.png"],stdout=subprocess.PIPE)
    now_ = time.time()
    diff = now - now_
    print(diff)
    #os.system("mono "+pathToMusicat+ " noGUI" + " input="+"\""+ inputToMusicat + "\""+ " png="+"\""+os.getcwd()+"/out.png"+"\"")
    json_result = result.stdout.decode("utf-8")
    json_result = json_result.split('\n')
    json_result.pop()
    groups = []
    analogies = []
    measure_links = []
    strengths = []
    meta_groups = []
    for elem in json_result:
        if elem.count('-') == 1:
            measure_links.append(elem)

        elif elem.count('-') == 3:
            analogies.append(elem)

        elif elem.count('+') == 1:
            elem = elem.split(',')
            elem_ = elem[0]
            elem__ = elem_.split("+")
            if (int(elem__[1]) - int(elem__[0])) < 2:
                groups.append(elem_)
                strengths.append(elem[1])
            else:
                meta_groups.append(elem_)
    response = {}
    response['analogies'] = analogies
    response['measure_links'] = measure_links
    response['groups'] = groups
    response['meta_groups'] = meta_groups
    response['strengths'] = strengths





    return response



def main():
    run(os.getcwd()+"/RhythmCat.exe","../creativityScoring/midi_data/2022-06-05_005751_1.mid")


if __name__ == "__main__":
    main()
