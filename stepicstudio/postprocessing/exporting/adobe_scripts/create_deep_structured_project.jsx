//Based on samples of using ExtendScript and docs(unofficial):
//https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
//https://media.readthedocs.org/pdf/premiere-scripting-guide/latest/premiere-scripting-guide.pdf

const screenTargetTrackNumber = 0;
const profTargetTrackNumber = 1;
const sequenceNamePostfix = "_sequence";
const extensionLabel = ".prproj";

/**
 * @param name {string} Name of sequence.
 * @param {string} preset Path to .sqpreset file.
 */
function createSequence(name, preset) {
    app.enableQE();
    qe.project.newSequence(name, preset);
}

function getInsertionTime(needSynchronize, targetVTrack, sequence, syncOffset) {
    if (targetVTrack.clips.numItems === 0) {
        return syncOffset;
    }

    var orderNumber = targetVTrack.clips.numItems - 1; //both of tracks have to contain item with this index

    if (!needSynchronize) {
        return targetVTrack.clips[orderNumber].end.seconds;
    }

    var screenVTrack = sequence.videoTracks[screenTargetTrackNumber];
    var profVTrack = sequence.videoTracks[profTargetTrackNumber];

    var screenEndTrackTime = screenVTrack.clips[orderNumber].end.seconds;
    var profEndTrackTime = profVTrack.clips[orderNumber].end.seconds;

    return syncOffset + Math.max(screenEndTrackTime, profEndTrackTime);
}

function appendVideoItemToSequence(videoItem, targetVTrackNumber, needSynchronize, syncOffsets) {
    var seq = app.project.activeSequence;

    if (targetVTrackNumber >= seq.videoTracks.numTracks || targetVTrackNumber < 0) {
        throw new Error("Number of video track is out of bounds");
    }

    var targetVTrack = seq.videoTracks[targetVTrackNumber];

    if (!targetVTrack) {
        throw new Error("Could not find video track to append.");
    }

    var syncOffset = syncOffsets[videoItem.name] !== undefined ? parseFloat(syncOffsets[videoItem.name]) : 0;
    var insertionTime = getInsertionTime(needSynchronize, targetVTrack, seq, syncOffset);
    targetVTrack.insertClip(videoItem, insertionTime);

    return insertionTime;
}

function appendMarkers(videoItem, itemAppendingTime, markerTimes) {
    if (markerTimes[videoItem.name] === undefined) {
        return;
    }

    var seq = app.project.activeSequence;

    for (var i = 0; i < markerTimes[videoItem.name].length; i++) {
        seq.markers.createMarker(itemAppendingTime + parseFloat(markerTimes[videoItem.name][i]));
    }
}

function arrayContainsItem(arr, item) {
    for (var i = 0; i < arr.length; i++) {
        if (item === arr[i]) { //indexOf() isn't supported by ExtendScript
            return true;
        }
    }
    return false;
}

function getItemByName(itemName, root) {
    if (root === undefined) {
        root = app.project.rootItem;
    }

    for (var i = 0; i < root.children.numItems; i++) {
        if (root.children[i].name === itemName) { //indexOf() isn't supported by ExtendScript
            return root.children[i];
        }
    }

    return undefined;
}

/**
 * Returns corresponding sequence track number if filenameToCheck found in
 * screenVideos array or professorVideos array.
 */
function getTargetSequenceNumber(filenameToCheck,
                                 screenVideos,
                                 profVideos,
                                 screenTarget,
                                 profTarget) {
    if (arrayContainsItem(screenVideos, filenameToCheck)) {
        return screenTarget;
    } else if (arrayContainsItem(profVideos, filenameToCheck)) {
        return profTarget;
    } else {
        return undefined;
    }
}

/**
 * Depth crawl of file system folders structure.
 * Creates similar bin structure with sequences for each bin according to media files in folder.
 *
 * @param parentFolder Root of folder structure.
 * @param currentBin Bin object, according to parentFolder.
 * @param seqPreset Path to sequences config.
 * @param screenVideos Array of target screen filenames.
 * @param profVideos Array of target prof filenames.
 * @param needSynchronize Synchronize flag.
 * @param markerTimes markers which indicates screencasts frame change
 * @param syncOffset offset which should be added to synchronize video tracks via audio
 * @returns {boolean} true if success, false otherwise.
 */
function createDeepBinStructure(parentFolder,
                                currentBin,
                                seqPreset,
                                screenVideos,
                                profVideos,
                                needSynchronize,
                                markerTimes,
                                syncOffset) {
    var subItems = parentFolder.getFiles();
    for (var i = 0; i < subItems.length; i++) {
        if (subItems[i] instanceof Folder) {
            createDeepBinStructure(subItems[i],
                                   currentBin.createBin(subItems[i].name),
                                   seqPreset,
                                   screenVideos,
                                   profVideos,
                                   needSynchronize);

            continue;
        }

        var targetSequenceNumber = getTargetSequenceNumber(subItems[i].name,
                                                           screenVideos,
                                                           profVideos,
                                                           screenTargetTrackNumber,
                                                           profTargetTrackNumber);

        if (targetSequenceNumber === undefined) { //skip current file if it is out of target files
            continue;
        }

        app.project.importFiles([subItems[i].fsName],
                                1,                      // suppress warnings
                                currentBin,
                                0);                     // import as numbered stills

        var currentSequence = getItemByName(parentFolder.name + sequenceNamePostfix, currentBin);

        if (currentSequence === undefined) { //if there is no sequence for this folder
            createSequence(parentFolder.name + sequenceNamePostfix, seqPreset);
            getItemByName(parentFolder.name + sequenceNamePostfix)
                .moveBin(currentBin);
        }

        var currentItem = getItemByName(subItems[i].name, currentBin);
        //appends movie to active(last created) sequence
        var itemAppendingTime = appendVideoItemToSequence(currentItem,
                                                          targetSequenceNumber,
                                                          needSynchronize,
                                                          syncOffset);

        appendMarkers(currentItem,
                      itemAppendingTime,
                      markerTimes)
    }
}

function createProject(basePath,
                       presetPath,
                       screenVideos,
                       professorVideos,
                       outputName,
                       needSynchronize,
                       markerTimes,
                       sync_offsets) {
    var parentFolder = Folder(basePath);
    var parentBin = app.project
                       .rootItem
                       .createBin(parentFolder.name);

    try {
        createDeepBinStructure(parentFolder,
                               parentBin,
                               presetPath,
                               screenVideos,
                               professorVideos,
                               needSynchronize,
                               markerTimes,
                               sync_offsets);
        app.project.saveAs(basePath + outputName + extensionLabel); //save as another project(without template modification)
        app.project.closeDocument(1, 0); // 1 - to save before closing; 0 - to close without modal dialog
    } catch (e) {
        app.project.closeDocument(0, 0);  // 0 - without save before closing; 0 - to close without modal dialog
    }
}

createProject(basePath,
              presetPath,
              screenVideos,
              professorVideos,
              outputName,
              needSync,
              markerTimes,
              syncOffsets);
app.quit();
