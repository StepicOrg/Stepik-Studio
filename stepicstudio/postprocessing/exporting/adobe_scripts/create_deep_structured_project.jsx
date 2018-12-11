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

function getInsertionTime(needSynchronize, targetVTrack, sequence) {
    if (targetVTrack.clips.numItems === 0) {
        return "00;00;00;00";
    }

    if (!needSynchronize) {
        return targetVTrack.clips[targetVTrack.clips.numItems - 1].end.seconds
    }

    const sceenVTrack = sequence.videoTracks[screenTargetTrackNumber];
    const profVTrack = sequence.videoTracks[profTargetTrackNumber];

    if (sceenVTrack.clips.numItems !== profVTrack.clips.numItems) {
        throw new Error("Tracks contains different number of videos.");
    }

    const screenEndTrackTime = sceenVTrack.clips[sceenVTrack.clips.numItems - 1].end.seconds;
    const profEndTrackTime = profVTrack.clips[profVTrack.clips.numItems].end.seconds;

    return Math.max(screenEndTrackTime, profEndTrackTime);
}

function appendVideoItemToSequence(videoItem, targetVTrackNumber, needSynchronize) {
    const seq = app.project.activeSequence;

    if (targetVTrackNumber >= seq.videoTracks.numTracks ||
        targetVTrackNumber < 0) {
        throw new Error("Number of video track is out of bounds");
    }

    const targetVTrack = seq.videoTracks[targetVTrackNumber];

    if (!targetVTrack) {
        throw new Error("Could not find video track to append.");
    }

    targetVTrack.insertClip(videoItem, getInsertionTime(needSynchronize, targetVTrack, seq));
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
 * @param needSynchronize Synchronize flag
 * @returns {boolean} true if success, false otherwise.
 */
function createDeepBinStructure(parentFolder,
                                currentBin,
                                seqPreset,
                                screenVideos,
                                profVideos,
                                needSynchronize) {
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

        try {
            var currentVideo = getItemByName(subItems[i].name, currentBin);
            appendVideoItemToSequence(currentVideo, targetSequenceNumber, needSynchronize); //appends movie to active sequence
        } catch (e) {
            return false;
        }
    }
    return true;
}

function createProject(basePath,
                       presetPath,
                       screenVideos,
                       professorVideos,
                       outputName,
                       needSynchronize) {
    var parentFolder = Folder(basePath);
    var parentBin = app.project
                       .rootItem
                       .createBin(parentFolder.name);
    const result = createDeepBinStructure(parentFolder,
                                        parentBin,
                                        presetPath,
                                        screenVideos,
                                        professorVideos,
                                        needSynchronize);

    if (result) {
        app.project.saveAs(basePath + outputName + extensionLabel); //save as another project(without template modification)
        app.project.closeDocument(1, 0); // 1 - to save before closing; 0 - to close without modal dialog
    } else {
        app.project.closeDocument(0, 0);  // 0 - without save before closing; 0 - to close without modal dialog
    }
}

createProject(basePath,
              presetPath,
              screenVideos,
              professorVideos,
              outputName,
              needSync);
app.quit();
