// how to make it so that the videos play based on Astoria time, not local time?

// format dates to just include the time on a 24-hour clock
const clock_format = new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    hourCycle: "h24",
    timeZone: "America/New_York"
});

// create a video player
async function loadVideos(cued_file, timecode) {

    // find container
    const container = document.querySelector(".container");
    
    // create a video element
    const player = document.createElement("video");

    // generate random id
    function getRandomId(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1) + min)
    };
    randomId = getRandomId(1000,9999);
    player.id = randomId;

    // get the filename of the video
    player.src = cued_file;

    // set to autoplay
    player.autoplay = true;

    // don't loop the video
    player.loop = false;

    // mute the video (playing the video automatically doesn't work without this)
    player.muted = true;

    // needed for ios
    player.playsinline = true;

    // set max-width if needed
    // player.style.maxWidth = "512px";

    // give the video random coordinates
    // }; // generate random float between -1 and 1
    function getRandomVal(min, max) {
        return Math.random() * (max - min) + min;
    } // get random float, but allows a custom range
    top_spacing = String(`${getRandomVal(-10,30)}vh`); // set range for top spacing
    side_spacing = String(`${getRandomVal(-15, 45)}vw`); // set range for side spacing
    player.style.position = "absolute";
    player.style.top = top_spacing;
    player.style.left = side_spacing;

    // call function to remove element when ended
    player.setAttribute("onended", `remove_video("${randomId}")`);

    // throw that video in the container!
    container.appendChild(player);

};

// match up video recording times with current time
async function get_video_times() {

    // get current time
    const timer = clock_format.format(new Date);
    console.log(`timer: ${timer}`);

    // store data from json file as obj
    const video_metadata = await fetch("./video_metadata.json");
    let obj = await video_metadata.json();

    // cycle through objects in json, and check if the times match the current time
    for (let i = 0; i < obj.length; i++) {
        let video_file = obj[i];
        let video_title = video_file.video;
        // format the date in the metadata to match format of timer
        let recording_time = clock_format.format(new Date(video_file.creation_date));

        // if the time matches, play the video
        if (recording_time == timer) {
            console.log(`the recording time of ${video_file.video} matches the current time`);
            loadVideos(video_title, recording_time);
        };
    };

    // restart the function every second
    setTimeout(get_video_times, 1000);
};

// remove video element when it ends
async function remove_video(playerId) {
    document.getElementById(playerId).remove();
};

get_video_times();

// remove disclaimer box after set interval
setTimeout(function removeDisclaimer() {
    document.getElementById("disclaimer").remove();
}, 30000);