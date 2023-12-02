// load videos from a json file called "videos.json"
async function loadVideos() {

    // get the container where we will put the videos
    const container = document.querySelector(".container")

    // fetch the json file and parse it into an array of video urls
    const response = await fetch("videos.json");
    let vids = await response.json();

    let videoCount = 0;
    for (let v of vids) {
        videoCount++;
    }
    console.log("videoCount = " + videoCount);
    randomVideo = Math.floor(Math.random() * videoCount);
    console.log("randomVideo = " + randomVideo);
    
    // create a video element
    const player = document.createElement("video");

    // player.classList.add("bg")

    // pick a random video out of the hat
    player.src = vids[randomVideo];

    // loop the video
    player.loop = true;

    // mute the video (playing the video automatically doesn't work without this)
    player.muted = true;

    player.autoplay = true;

    // needed for ios
    player.playsinline = true;

    // add the video to our container element
    container.appendChild(player);

}

loadVideos();