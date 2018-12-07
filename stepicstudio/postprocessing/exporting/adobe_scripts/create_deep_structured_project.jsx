//Based on samples of using ExtendScript and docs(unofficial):
//https://github.com/Adobe-CEP/Samples/blob/master/PProPanel/jsx/PPRO/Premiere.jsx
//https://media.readthedocs.org/pdf/premiere-scripting-guide/latest/premiere-scripting-guide.pdf

const screenTargetTrack = 0;
const profTargetTrack = 1;
const sequenceNamePostfix = "_sequence";

// var templateProject = "C:\\Development\\AdobeScripts\\template.prproj";
// var presetPath = "C:\\Development\\AdobeScripts\\ppro.sqpreset";
// var screenVideos = ["Step4from376_Screen.mp4", "Step3from376_Screen.mp4", "Step1from377_Screen.mp4", "Step2from378_Screen.mp4"];
// var professorVideos = ["Step4from376_Professor.mp4", "Step3from376_Professor.mp4", "Step1from377_Professor.mp4", "Step2from378_Professor.mp4"];
// var basePath = "D:\\STEPIKSTUDIO\\TESTER\\test_course\\TestPProLesson3";
// var outputName = "TestPProLesson3";
//
// app.openDocument(templateProject);

/*Creates sequence
    params:
    name: name of sequence as string;
    presetPath: path to .sqpreset file as string. */
function createSequence(name, preset) {
    app.enableQE();
    qe.project.newSequence(name, preset);
}

/*Appends item to sequence
    params:
    item: projectItem to append to sequence;
    targetVTrackNumber: number of track to append. */
function appendItemToSequence(item, targetVTrackNumber) {
    const seq = app.project.activeSequence;

    if (targetVTrackNumber >= seq.videoTracks.numTracks ||
        targetVTrackNumber < 0) {
        throw new Error("Number of video track is out of bounds");
    }
    var targetVTrack = seq.videoTracks[targetVTrackNumber];

    if (!targetVTrack) {
        throw new Error("Could not find video track to append.");
    }
    // If there are already clips in this track,
    // append this one to the end. Otherwise,
    // insert at start time.
    if (targetVTrack.clips.numItems > 0) {
        var lastClip = targetVTrack.clips[(targetVTrack.clips.numItems - 1)];
        targetVTrack.insertClip(item, lastClip.end.seconds);
    } else {
        targetVTrack.insertClip(item, "00;00;00;00");
    }
}

/*Checks that array contains items value */
function arrayContainsItem(arr, item) {
    for (var i = 0; i < arr.length; i++) {
        if (item === arr[i]) { //indexOf() isn't supported by ExtendScript
            return true;
        }
    }
    return false;
}

/*Return projectItem with name itemName if exists.
    params:
    itemName: name of item to find;
    root: root item to start searching;
    Uses app.project.rootItem by default;*/
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

/* Returns corresponding sequence track number if filenameToCheck found in
    screenVideos array or professorVideos array; */
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

/* Depth crawl of file system folders structure. 
    Creates similar bin scructure with suquence for each bin according to media files in folder.  
    params:
    parentFolder: Folder object of root;
    currentBin: projectItem representing bin object, accroding to parentFolder;
    seqPreset: path to presetPath with sequences config;
    screenVideos: array of target screen filenames;
    professorVideos: array of target prof filenames.
    return true if success, false otherwise.*/
function createDeepBinStructure(parentFolder, currentBin, seqPreset, screenVideos, profVideos) {
    var subItems = parentFolder.getFiles();
    for (var i = 0; i < subItems.length; i++) {
        if (subItems[i] instanceof File) {
            var targetSequenceNumber = getTargetSequenceNumber(subItems[i].name,
                screenVideos,
                profVideos,
                screenTargetTrack,
                profTargetTrack);

            if (targetSequenceNumber === undefined) { //skip current file if it is out of target files
                continue;
            }
            app.project.importFiles([subItems[i].fsName],
                1,				// suppress warnings
                currentBin,
                0);                // import as numbered stills

            var currentSequence = getItemByName(parentFolder.name + sequenceNamePostfix, currentBin);

            if (currentSequence === undefined) { //if there is no sequence for this folder
                createSequence(parentFolder.name + sequenceNamePostfix, seqPreset);
                getItemByName(parentFolder.name + sequenceNamePostfix)
                    .moveBin(currentBin);
            }
            var currentMovie = getItemByName(subItems[i].name, currentBin);
            try {
                appendItemToSequence(currentMovie, targetSequenceNumber); //appends movie to active sequence
            } catch (e) {
                return false;
            }
        } else { //subItems[i] is folder
            var childFolder = Folder(subItems[i]);
            var childBin = currentBin.createBin(childFolder.name);

            createDeepBinStructure(childFolder,
                childBin,
                seqPreset,
                screenVideos,
                profVideos);
        }
    }
    return true;
}

/*Uses global variables*/
function createProject() {
    var parentFolder = Folder(basePath); //may return File
    var parentBin = app.project
        .rootItem
        .createBin(parentFolder.name);

    var result = createDeepBinStructure(parentFolder,
        parentBin,
        presetPath,
        screenVideos,
        professorVideos);

    if (result) {
        app.project.saveAs(basePath + outputName + ".prproj"); //save as another project(without template modification)
        app.project.closeDocument(1, 0); // 1 - to save before closing; 0 - to close without modal dialog
    } else {
        app.project.closeDocument(0, 0);  // 0 - without save before closing; 0 - to close without modal dialog
    }
}

createProject();
app.quit();
