function addSelectedClass(elem) {
    if (elem.classList.contains('list-group-item-success')) {
        elem.classList.remove('list-group-item-success');
        elem.classList.remove('selected');
    } else {
        elem.classList.add('list-group-item-success');
        elem.classList.add('selected');
    }
}

function validateSelectTracks() {
    let tracks = document.getElementsByClassName('selected');
    if (tracks.length >= 1) {
        return true

    } else {
        alert('Please select at least 1 track');
        return false
    }
}

function getSelectedTracks() {
    let tracks = document.getElementsByClassName('selected');

    if (tracks.length >= 1) {
        let res = [];
        for (let i = 0; i < tracks.length; i++) {
            res.push(tracks[i].getAttribute("value"))
        }
        return res

    } else {
        return false
    }
}

function getTracks() {
    let val_tag = document.getElementById('selected_tracks');
    val_tag.value = getSelectedTracks();
}
