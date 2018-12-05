//Based on samples of using ExtendScript and docs(unofficial):
//https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
//https://media.readthedocs.org/pdf/premiere-scripting-guide/latest/premiere-scripting-guide.pdf

/*Creates sequence
params:
name - name of sequence as string
preset - path to .sqpreset file as string*/
function createSequence(name, preset) {
    app.enableQE();
    qe.project.newSequence(name, preset);
}

/*Appends item to sequence
params:
item - projectItem to append to sequence
targetVTrackNumber - number of track to append*/
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

/*Appends list of items to sequence
params:
path - base path to directory with media items
files - array of file names of media items
trackNumber - track number of sequence*/
function appendToSequence(path, files, trackNumber) {
    var fullPaths = files.slice();
    for(var i = 0; i < files.length; i++) {
          fullPaths[i] = path + files[i];
    }
    app.project.importFiles(fullPaths);
    for(var i = 0; i < app.project.rootItem.children.numItems; i++) {
        for(var j = 0; j < files.length; j++) {
            if (app.project.rootItem.children[i].name === files[j]) { //indexOf() isn't supported by ExtendScript
                try {
                    appendItemToSequence(app.project.rootItem.children[i], trackNumber);
                } catch (e) {
                    app.project.closeDocument(0, 0); // 0 - without save before closing to avoid creating project with missing files; 0 - to close without modal dialog
                    app.quit();
                }
                break;
            }   
        }
    }
}

createSequence(outputName, presetPath);
appendToSequence(basePath, professorVideos, 1);
appendToSequence(basePath, screenVideos, 0);
app.project.saveAs(basePath + outputName + '.prproj'); //save as another project(without template modification)
app.project.closeDocument(1, 0); // 1 - to save before closing; 0 - to close without modal dialog
app.quit();