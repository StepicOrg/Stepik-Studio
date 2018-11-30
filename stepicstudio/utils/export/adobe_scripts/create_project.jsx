//Based on samples of using ExtendScript and docs: 
//https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
//https://media.readthedocs.org/pdf/premiere-scripting-guide/latest/premiere-scripting-guide.pdf

//Creates sequence
//params:
//name - name of sequence as string
//preset - path to .sqpreset file as string
function createSequence(name, preset) {
    app.enableQE();
    qe.project.newSequence(name, preset);
}

//Appends to sequence
//params:
//item - projectItem to append to sequence
//targetVTrackNumber - number of track to append
function appendItemToSequence(item, targetVTrackNumber) {
    var seq = app.project.activeSequence;
    if (seq){
        if (item){
            var numVTracks = seq.videoTracks.numTracks;
            if (targetVTrackNumber >= numVTracks || targetVTrackNumber < 0) {
                throw new Error("Number of video track is out of bounds");
            }
            var targetVTrack = seq.videoTracks[targetVTrackNumber];
            if (targetVTrack){
                // If there are already clips in this track,
                // append this one to the end. Otherwise, 
                // insert at start time.

                if (targetVTrack.clips.numItems > 0){
                    var lastClip = targetVTrack.clips[(targetVTrack.clips.numItems - 1)];
                    if (lastClip){
                        targetVTrack.insertClip(item, lastClip.end.seconds);
                    }
                }else {
                        targetVTrack.insertClip(item, '00;00;00;00');
                }
            } else {
                throw new Error("Could not find video track to append.");
            }
        } else {
            throw new Error("Couldn't locate first projectItem.");
        }
    } else {
        throw new Error("no active sequence.");
    }
}

function appendToSequence(path, files, trackNumber) {
    fullPaths = files.map(function(fileName) {
        return path + fileName;
    });

    app.project.importFiles(fullPaths);
    
    for(var i = 0; i < app.project.rootItem.children.numItems; i++) {
        if(files.indexOf (app.project.rootItem.children[i].name) > -1) {
            appendItemToSequence(app.project.rootItem.children[i], trackNumber);
            k++;
        }
    }
}

var basePath = "D:\\STEPIKSTUDIO\\TESTER\\test_course\\Lesson_1123123\\Step123123123\\"
var professorVideos = ["Step2from367_Professor.mp4",  "Step3from367_Professor.mp4"]; 
var screenVideos = ["Step2from367_Screen.mp4", "Step3from367_Screen.mp4"]
var preset = "C:\\Development\\AdobeScripts\\PProPanel.sqpreset";

createSequence("testSequence", preset);
    
//Imports files:
appendToSequence(basePath, professorVideos, 1);
appendToSequence(basePath, screenVideos, 0);

